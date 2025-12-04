"""
Phase 1: Embedding Model Tester (MEMORY OPTIMIZED - OOM FIXED)
- Fixed OOM issues for CodeRankEmbed (batch_size=1, chunked processing)
- Added text truncation to 512 tokens max
- Added aggressive memory cleanup
- Added proper prefixes for all models
"""

import json
import time
import gc
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from concept_validators import ALL_VALIDATORS, validate_file_for_concept


# ============================================================================
# MODEL PREFIX MAPPINGS (COMPLETE)
# ============================================================================

MODEL_PREFIXES = {
    "nomic-ai/nomic-embed-text-v1.5": {
        "query": "search_query: ",
        "document": "search_document: ",
    },
    "nomic-ai/nomic-embed-code": {
        "query": "search_query: ",
        "document": "search_document: ",
    },
    "nomic-ai/CodeRankEmbed": {
        "query": "Represent this query for searching relevant code: ",
        "document": "",  # No prefix for documents
    },
    "intfloat/multilingual-e5-large-instruct": {
        "query": "query: ",
        "document": "passage: ",
    },
    "BAAI/bge-small-en-v1.5": {
        "query": "Represent this sentence for searching relevant passages: ",
        "document": "",
    },
    "Qwen/Qwen3-Embedding-0.6B": {"query": "query: ", "document": ""},
    # Models that don't need prefixes
    "Alibaba-NLP/gte-multilingual-base": {"query": "", "document": ""},
    "google/embeddinggemma-300m": {"query": "", "document": ""},
}


def get_model_prefix(model_name: str, prefix_type: str) -> str:
    """Get the appropriate prefix for a model"""
    if model_name in MODEL_PREFIXES:
        return MODEL_PREFIXES[model_name].get(prefix_type, "")
    return ""


def truncate_text(text: str, max_tokens: int = 512) -> str:
    """
    Truncate text to approximately max_tokens
    Use simple word-based truncation (1 token ≈ 0.75 words)
    """
    words = text.split()
    max_words = int(max_tokens * 0.75)

    if len(words) <= max_words:
        return text

    # Truncate and add marker
    truncated = " ".join(words[:max_words])
    return truncated + "..."


def embed_in_chunks(
    model, texts: List[str], batch_size: int, device: str
) -> np.ndarray:
    """
    Embed texts in chunks with aggressive memory cleanup
    Essential for CodeRankEmbed which has high memory requirements
    """
    all_embeddings = []
    total = len(texts)

    print(f"  → Processing {total} items in chunks of {batch_size}")

    for i in range(0, total, batch_size):
        chunk = texts[i : i + batch_size]
        chunk_size = len(chunk)

        # Show progress
        if i % 10 == 0:
            print(f"  → Progress: {i}/{total} ({i*100//total}%)")

        # Embed chunk
        chunk_embeddings = model.encode(
            chunk,
            show_progress_bar=False,
            batch_size=1,  # Always use batch_size=1 within chunks
            device=device,
            convert_to_numpy=True,
        )

        # Handle single item vs batch
        if chunk_size == 1:
            all_embeddings.append(chunk_embeddings)
        else:
            all_embeddings.extend(chunk_embeddings)

        # Aggressive cleanup after each chunk
        if device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()

    print(f"  → Completed: {total}/{total} (100%)")
    return np.array(all_embeddings)


class ColabEmbeddingTester:
    """Test embedding models for code semantic search (MEMORY OPTIMIZED)"""

    def __init__(self, test_data_dir: Path = Path("test_code"), max_tokens: int = 512):
        self.test_data_dir = test_data_dir
        self.test_files = {}
        self.results = {}
        self.device = self._setup_device()
        self.current_model_name = None
        self.max_tokens = max_tokens

    def _setup_device(self):
        """Detect and setup GPU if available"""
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ GPU detected: {gpu_name} ({gpu_memory:.1f} GB)")

            # Aggressive cache clearing
            torch.cuda.empty_cache()
            gc.collect()
        else:
            device = "cpu"
            print("⚠️  No GPU detected. Using CPU (will be slower)")

        return device

    def load_test_files(self):
        """Load all test files into memory (with truncation)"""
        print("\n📂 Loading test files...")

        for lang_dir in ["python", "javascript"]:
            lang_path = self.test_data_dir / lang_dir
            if not lang_path.exists():
                print(f"  Warning: {lang_path} does not exist")
                continue

            for filepath in lang_path.glob("*.*"):
                if filepath.suffix in [".py", ".js", ".jsx", ".ts", ".tsx"]:
                    try:
                        with open(
                            filepath, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        # Truncate to prevent OOM
                        content_truncated = truncate_text(content, self.max_tokens)

                        relative_path = str(filepath.relative_to(self.test_data_dir))
                        self.test_files[relative_path] = {
                            "content": content_truncated,  # Use truncated
                            "content_full": content,  # Keep full for validation
                            "language": lang_dir,
                            "path": str(filepath),
                        }
                    except Exception as e:
                        print(f"  Error loading {filepath}: {e}")

        print(
            f"  ✅ Loaded {len(self.test_files)} files (truncated to {self.max_tokens} tokens)"
        )
        return len(self.test_files)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def embed_documents(
        self, model, texts: List[str], batch_size: int = 8
    ) -> np.ndarray:
        """
        Embed documents with proper prefix (MEMORY OPTIMIZED)
        """
        doc_prefix = get_model_prefix(self.current_model_name, "document")

        if doc_prefix:
            prefixed_texts = [f"{doc_prefix}{text}" for text in texts]
            print(
                f"  → Using document prefix: '{doc_prefix}' (applied to {len(texts)} docs)"
            )
        else:
            prefixed_texts = texts

        # FIXED: Use chunked processing for CodeRankEmbed
        if "CodeRankEmbed" in self.current_model_name:
            print(f"  → Using chunked processing for CodeRankEmbed (batch_size=1)")
            embeddings = embed_in_chunks(
                model, prefixed_texts, batch_size=1, device=self.device
            )
        else:
            # Normal processing for other models
            embeddings = model.encode(
                prefixed_texts,
                show_progress_bar=True,
                batch_size=batch_size,
                device=self.device,
                convert_to_numpy=True,
            )

        # Clear cache after embedding
        if self.device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        return embeddings

    def embed_query(self, model, query: str) -> np.ndarray:
        """Embed query with proper prefix"""
        query_prefix = get_model_prefix(self.current_model_name, "query")

        if query_prefix:
            prefixed_query = f"{query_prefix}{query}"
        else:
            prefixed_query = query

        embedding = model.encode(
            prefixed_query, device=self.device, convert_to_numpy=True
        )

        return embedding

    def test_model(self, model_name: str, model) -> Dict:
        """Test a single embedding model on all concepts"""
        self.current_model_name = model_name

        print(f"\n{'='*60}")
        print(f"Testing Model: {model_name}")
        print(f"Device: {self.device}")
        print("=" * 60)

        start_time = time.time()

        # Step 1: Embed all test files with PROPER PREFIXES
        print("\n1️⃣ Embedding test files...")
        file_embeddings = {}
        file_list = list(self.test_files.keys())
        content_list = [self.test_files[f]["content"] for f in file_list]

        try:
            # Determine batch size (CodeRankEmbed uses chunked processing internally)
            batch_size = 1 if "CodeRankEmbed" in model_name else 8

            embeddings = self.embed_documents(
                model, content_list, batch_size=batch_size
            )

            for filepath, embedding in zip(file_list, embeddings):
                file_embeddings[filepath] = embedding

            print(f"  ✅ Embedded {len(file_embeddings)} files")

        except Exception as e:
            print(f"  ❌ Error embedding files: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

        # Step 2: Test each concept
        print("\n2️⃣ Testing concepts...")
        concept_results = []

        for concept_name in ALL_VALIDATORS.keys():
            try:
                query_embedding = self.embed_query(model, concept_name)

            except Exception as e:
                print(f"  ❌ Error embedding query '{concept_name}': {e}")
                continue

            # Calculate similarities
            similarities = {}
            for filepath, file_embedding in file_embeddings.items():
                sim = self.cosine_similarity(query_embedding, file_embedding)
                similarities[filepath] = sim

            # Get top 5 results
            top_5 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]

            # Validate each result (use FULL content for validation)
            valid_results = []
            for filepath, score in top_5:
                content_full = self.test_files[filepath]["content_full"]
                is_valid = validate_file_for_concept(
                    filepath, content_full, concept_name
                )
                valid_results.append(
                    {"file": filepath, "score": float(score), "valid": is_valid}
                )

            # Calculate metrics
            valid_count = sum(1 for r in valid_results if r["valid"])
            p5 = valid_count / 5.0
            p1 = 1.0 if valid_results and valid_results[0]["valid"] else 0.0

            # Find position of first valid result (for MRR)
            first_valid_pos = next(
                (i + 1 for i, r in enumerate(valid_results) if r["valid"]), None
            )
            rr = 1.0 / first_valid_pos if first_valid_pos else 0.0

            concept_results.append(
                {
                    "concept": concept_name,
                    "precision_at_5": p5,
                    "precision_at_1": p1,
                    "reciprocal_rank": rr,
                    "valid_in_top5": valid_count,
                    "top_5_results": valid_results,
                }
            )

            # Print result
            status = "✅" if p5 >= 0.6 else "❌"
            print(f"  {status} {concept_name:40s} P@5: {p5:.2f} | P@1: {p1:.0f}")

        # Step 3: Aggregate metrics
        total_concepts = len(concept_results)
        overall_p5 = sum(r["precision_at_5"] for r in concept_results) / total_concepts
        overall_p1 = sum(r["precision_at_1"] for r in concept_results) / total_concepts
        overall_mrr = (
            sum(r["reciprocal_rank"] for r in concept_results) / total_concepts
        )

        inference_time = time.time() - start_time

        # Calculate pass rate
        pass_count = sum(1 for r in concept_results if r["precision_at_5"] >= 0.6)
        pass_rate = pass_count / total_concepts

        # GPU memory stats
        gpu_memory_used = None
        if self.device == "cuda":
            gpu_memory_used = torch.cuda.max_memory_allocated() / 1e9
            torch.cuda.empty_cache()

        results = {
            "model": model_name,
            "device": self.device,
            "gpu_memory_gb": gpu_memory_used,
            "overall_precision_at_5": overall_p5,
            "overall_precision_at_1": overall_p1,
            "overall_mrr": overall_mrr,
            "pass_rate": pass_rate,
            "concepts_passed": pass_count,
            "total_concepts": total_concepts,
            "inference_time_seconds": inference_time,
            "per_concept": concept_results,
            "prefixes_used": {
                "query": get_model_prefix(model_name, "query"),
                "document": get_model_prefix(model_name, "document"),
            },
        }

        # Print summary
        print(f"\n{'='*60}")
        print("RESULTS SUMMARY")
        print("=" * 60)
        print(f"Overall Precision@5:  {overall_p5:.1%}")
        print(f"Overall Precision@1:  {overall_p1:.1%}")
        print(f"Mean Reciprocal Rank: {overall_mrr:.3f}")
        print(f"Pass Rate (P@5≥60%): {pass_rate:.1%} ({pass_count}/{total_concepts})")
        print(f"Inference Time:       {inference_time:.1f}s")
        if gpu_memory_used:
            print(f"Peak GPU Memory:      {gpu_memory_used:.2f} GB")
        print("=" * 60)

        return results

    def compare_models(self, results_list: List[Dict]) -> str:
        """Generate comparison table from multiple model results"""

        if not results_list:
            return "No results to compare"

        valid_results = [r for r in results_list if "error" not in r]
        if not valid_results:
            return "All models failed to produce results."

        valid_results = sorted(
            valid_results,
            key=lambda x: x.get("overall_precision_at_5", 0),
            reverse=True,
        )

        table = "\n## Model Comparison\n\n"
        table += (
            "| Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Device | Decision |\n"
        )
        table += (
            "|-------|-----|-----|-----|-----------|----------|--------|----------|\n"
        )

        for result in valid_results:
            p5 = result["overall_precision_at_5"]
            p1 = result["overall_precision_at_1"]
            mrr = result["overall_mrr"]
            pass_rate = result["pass_rate"]
            time_s = result["inference_time_seconds"]
            device = result.get("device", "unknown")

            if p5 >= 0.60:
                decision = "✅ GO"
            elif p5 >= 0.50:
                decision = "⚠️ CONDITIONAL"
            else:
                decision = "❌ NO-GO"

            table += f"| {result['model']} | {p5:.1%} | {p1:.1%} | {mrr:.3f} | {pass_rate:.1%} | {time_s:.1f} | {device} | {decision} |\n"

        best = valid_results[0]
        best_p5 = best["overall_precision_at_5"]

        table += f"\n### Recommendation\n\n"

        if best_p5 >= 0.60:
            table += f"**✅ PROCEED TO PHASE 2** with `{best['model']}`\n\n"
            table += f"- Achieves {best_p5:.1%} P@5 (threshold: ≥60%)\n"
            table += f"- {best['concepts_passed']}/{best['total_concepts']} concepts pass (P@5≥60%)\n"
        elif best_p5 >= 0.50:
            table += f"**⚠️ CONDITIONAL PROCEED** - Acceptable for MVP\n\n"
            table += f"- Best model: `{best['model']}` at {best_p5:.1%} P@5\n"
            table += f"- Meets minimum threshold (≥50% P@5)\n"
        else:
            table += f"**❌ STOP PROJECT** - Embedding approach not viable\n\n"
            table += f"- Best model: `{best['model']}` at {best_p5:.1%} P@5\n"
            table += f"- Threshold: ≥50% for conditional proceed\n"

        return table

    def save_results(self, results: Dict, output_file: str = "results.json"):
        """Save results to JSON file"""
        output_path = Path(output_file)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {output_path}")


def setup_hf_auth():
    """Setup HuggingFace authentication"""
    try:
        from google.colab import userdata
        from huggingface_hub import login

        hf_token = userdata.get("HF_TOKEN")
        if hf_token:
            login(token=hf_token)
            print("✅ Authenticated with HuggingFace")
            return True
        else:
            print("⚠️ No HF_TOKEN in Colab secrets")
            return False
    except ImportError:
        try:
            from huggingface_hub import login

            login()
            print("✅ Authenticated with HuggingFace")
            return True
        except Exception as e:
            print(f"⚠️ HuggingFace auth failed: {e}")
            return False
    except Exception as e:
        print(f"⚠️ HuggingFace auth failed: {e}")
        return False


def main():
    """Main testing workflow (MEMORY OPTIMIZED)"""
    print("\n🔐 Setting up authentication...")
    setup_hf_auth()

    # Initialize tester with truncation
    tester = ColabEmbeddingTester(max_tokens=512)

    file_count = tester.load_test_files()
    if file_count == 0:
        print("❌ No test files found. Run dataset_generator.py first!")
        return

    print(
        f"\n✅ Ready to test on {file_count} files and {len(ALL_VALIDATORS)} concepts"
    )

    # UPDATED: Priority order - Code-specific models first
    models_to_test = [
        # PRIORITY 1: Code-specific models
        "nomic-ai/CodeRankEmbed",  # Test first with fixed memory!
        "nomic-ai/nomic-embed-text-v1.5",
        # Previously tested (now with proper prefixes)
        "intfloat/multilingual-e5-large-instruct",
        "Alibaba-NLP/gte-multilingual-base",
        # Lower priority
        "Qwen/Qwen3-Embedding-0.6B",
        "google/embeddinggemma-300m",
    ]

    all_results = []

    for model_name in models_to_test:
        print(f"\n\n{'#'*60}")
        print(f"Loading model: {model_name}")
        print("#" * 60)

        # Clear GPU memory before loading new model
        if tester.device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        try:
            model_kwargs = {"device": tester.device}

            if any(x in model_name for x in ["Alibaba-NLP", "nomic", "Qwen"]):
                model_kwargs["trust_remote_code"] = True
                print("  → Using trust_remote_code=True")

            if tester.device == "cuda":
                model_kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
                print("  → Using torch.float16 for memory efficiency")

            query_prefix = get_model_prefix(model_name, "query")
            doc_prefix = get_model_prefix(model_name, "document")
            if query_prefix or doc_prefix:
                print(f"  → Query prefix: '{query_prefix}'")
                print(f"  → Document prefix: '{doc_prefix}'")

            model = SentenceTransformer(model_name, **model_kwargs)

            results = tester.test_model(model_name, model)
            all_results.append(results)

            safe_name = model_name.replace("/", "_")
            tester.save_results(results, f"results_{safe_name}.json")

            # Aggressive cleanup
            del model
            if tester.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

        except Exception as e:
            print(f"❌ Failed to test {model_name}: {e}")
            import traceback

            traceback.print_exc()
            all_results.append({"model": model_name, "error": str(e)})

            # Try to recover from OOM
            if tester.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            continue

    # Generate comparison
    if all_results:
        comparison = tester.compare_models(all_results)
        print("\n\n" + comparison)

        with open("comparison.md", "w") as f:
            f.write(comparison)
        print("\n💾 Comparison saved to comparison.md")

        tester.save_results(
            {"all_models": all_results, "comparison_table": comparison},
            "all_results.json",
        )
        print("\n🎉 Testing complete! Check comparison.md for decision.")


if __name__ == "__main__":
    main()
