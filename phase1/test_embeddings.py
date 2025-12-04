"""
Phase 1: Embedding Model Tester (Colab Optimized)
Tests multiple embedding models on NL->Code mapping task with GPU acceleration
"""

import json
import time
import gc
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from concept_validators import ALL_VALIDATORS, validate_file_for_concept


class ColabEmbeddingTester:
    """Test embedding models for code semantic search with Colab optimizations"""

    def __init__(self, test_data_dir: Path = Path("test_code")):
        self.test_data_dir = test_data_dir
        self.test_files = {}
        self.results = {}
        self.device = self._setup_device()

    def _setup_device(self):
        """Detect and setup GPU if available"""
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✓ GPU detected: {gpu_name} ({gpu_memory:.1f} GB)")

            # Clear cache
            torch.cuda.empty_cache()
        else:
            device = "cpu"
            print("⚠️  No GPU detected. Using CPU (will be slower)")

        return device

    def load_test_files(self):
        """Load all test files into memory"""
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

                        relative_path = str(filepath.relative_to(self.test_data_dir))
                        self.test_files[relative_path] = {
                            "content": content,
                            "language": lang_dir,
                            "path": str(filepath),
                        }
                    except Exception as e:
                        print(f"  Error loading {filepath}: {e}")

        print(f"  ✓ Loaded {len(self.test_files)} files")
        return len(self.test_files)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def test_model(self, model_name: str, model) -> Dict:
        """
        Test a single embedding model on all concepts with Colab optimizations

        Args:
            model_name: Name of the model (for logging)
            model: SentenceTransformer or compatible model object

        Returns:
            Dict with results including P@1, P@5, per-concept scores
        """
        print(f"\n{'='*60}")
        print(f"Testing Model: {model_name}")
        print(f"Device: {self.device}")
        print("=" * 60)

        start_time = time.time()

        # Step 1: Embed all test files (batch for efficiency)
        print("\n1️⃣ Embedding test files...")
        file_embeddings = {}
        file_list = list(self.test_files.keys())
        content_list = [self.test_files[f]["content"] for f in file_list]

        try:
            # FIXED: Reduced batch size to prevent OOM
            batch_size = 8 if self.device == "cuda" else 8

            embeddings = model.encode(
                content_list,
                show_progress_bar=True,
                batch_size=batch_size,
                device=self.device,
                convert_to_numpy=True,  # Ensure numpy output
            )

            for filepath, embedding in zip(file_list, embeddings):
                file_embeddings[filepath] = embedding

            print(f"  ✓ Embedded {len(file_embeddings)} files")

            # Free GPU memory
            if self.device == "cuda":
                torch.cuda.empty_cache()

        except Exception as e:
            print(f"  ✗ Error embedding files: {e}")
            return {"error": str(e)}

        # Step 2: Test each concept
        print("\n2️⃣ Testing concepts...")
        concept_results = []

        # Check if model requires special query formatting
        requires_coderank_prefix = "CodeRankEmbed" in model_name
        requires_bge_prefix = "bge-" in model_name and "large" not in model_name
        requires_qwen_prefix = "Qwen" in model_name
        requires_nomic_prefix = "nomic-embed-code" in model_name

        for concept_name in ALL_VALIDATORS.keys():
            # Embed query (add prefix for specific models)
            try:
                if requires_coderank_prefix:
                    query_text = f"Represent this query for searching relevant code: {concept_name}"
                elif requires_bge_prefix:
                    query_text = f"Represent this sentence for searching relevant passages: {concept_name}"
                elif requires_qwen_prefix:
                    query_text = f"search_query: {concept_name}"
                elif requires_nomic_prefix:
                    query_text = f"search_query: {concept_name}"
                else:
                    query_text = concept_name

                query_embedding = model.encode(
                    query_text, device=self.device, convert_to_numpy=True
                )
            except Exception as e:
                print(f"  ✗ Error embedding query '{concept_name}': {e}")
                continue

            # Calculate similarities
            similarities = {}
            for filepath, file_embedding in file_embeddings.items():
                sim = self.cosine_similarity(query_embedding, file_embedding)
                similarities[filepath] = sim

            # Get top 5 results
            top_5 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]

            # Validate each result
            valid_results = []
            for filepath, score in top_5:
                content = self.test_files[filepath]["content"]
                is_valid = validate_file_for_concept(filepath, content, concept_name)
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
            status = "✓" if p5 >= 0.6 else "✗"
            print(f"  {status} {concept_name:40s} P@5: {p5:.2f} | P@1: {p1:.0f}")

        # Step 3: Aggregate metrics
        total_concepts = len(concept_results)
        overall_p5 = sum(r["precision_at_5"] for r in concept_results) / total_concepts
        overall_p1 = sum(r["precision_at_1"] for r in concept_results) / total_concepts
        overall_mrr = (
            sum(r["reciprocal_rank"] for r in concept_results) / total_concepts
        )

        inference_time = time.time() - start_time

        # Calculate pass rate (concepts with P@5 >= 0.6)
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

        # Filter out errored results
        valid_results = [r for r in results_list if "error" not in r]
        if not valid_results:
            return "All models failed to produce results."

        # Sort by P@5 (best first)
        valid_results = sorted(
            valid_results,
            key=lambda x: x.get("overall_precision_at_5", 0),
            reverse=True,
        )

        # Create markdown table
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

            # Decision logic
            if p5 >= 0.70:
                decision = "✅ GO"
            elif p5 >= 0.50:
                decision = "⚠️ CONDITIONAL"
            else:
                decision = "❌ NO-GO"

            table += f"| {result['model']} | {p5:.1%} | {p1:.1%} | {mrr:.3f} | {pass_rate:.1%} | {time_s:.1f} | {device} | {decision} |\n"

        # Add decision summary
        best = valid_results[0]
        best_p5 = best["overall_precision_at_5"]

        table += f"\n### Recommendation\n\n"

        if best_p5 >= 0.70:
            table += f"**✅ PROCEED TO PHASE 2** with `{best['model']}`\n\n"
            table += f"- Achieves {best_p5:.1%} P@5 (threshold: ≥70%)\n"
            table += f"- {best['concepts_passed']}/{best['total_concepts']} concepts pass (P@5≥60%)\n"
            table += f"- Device: {best.get('device', 'unknown')}\n"
        elif best_p5 >= 0.50:
            table += f"**⚠️ CONDITIONAL PROCEED** - Try enhancement strategies\n\n"
            table += f"- Best model: `{best['model']}` at {best_p5:.1%} P@5\n"
            table += f"- Recommendation: Add file extension hints to queries\n"
            table += f"- Re-test with hints. If P@5 reaches ≥70%, proceed to Phase 2\n"
        else:
            table += f"**❌ STOP PROJECT** - Embedding approach not viable\n\n"
            table += f"- Best model: `{best['model']}` at {best_p5:.1%} P@5\n"
            table += f"- Threshold: ≥50% for conditional proceed\n"
            table += f"- Recommendation: Consider alternative approaches or wait for better models\n"

        return table

    def save_results(self, results: Dict, output_file: str = "results.json"):
        """Save results to JSON file"""
        output_path = Path(output_file)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {output_path}")


def setup_hf_auth():
    """Setup HuggingFace authentication for gated models"""
    try:
        # Try Colab secrets first
        from google.colab import userdata
        from huggingface_hub import login

        hf_token = userdata.get("HF_TOKEN")
        if hf_token:
            login(token=hf_token)
            print("✓ Authenticated with HuggingFace")
            return True
        else:
            print("⚠️ No HF_TOKEN in Colab secrets")
            print("   Some gated models (embeddinggemma-300m) will fail")
            print("   Add token via left sidebar → 🔑 Secrets")
            return False
    except ImportError:
        # Not in Colab
        try:
            from huggingface_hub import login

            login()  # Will use cached token or prompt
            print("✓ Authenticated with HuggingFace")
            return True
        except Exception as e:
            print(f"⚠️ HuggingFace auth failed: {e}")
            print("   Some gated models may fail")
            return False
    except Exception as e:
        print(f"⚠️ HuggingFace auth failed: {e}")
        return False


def main():
    """
    Main testing workflow optimized for Colab
    Usage: python test_embeddings.py
    """
    # Setup authentication first
    print("\n🔐 Setting up authentication...")
    setup_hf_auth()

    # Initialize tester
    tester = ColabEmbeddingTester()

    # Load test files
    file_count = tester.load_test_files()
    if file_count == 0:
        print("❌ No test files found. Run dataset_generator.py first!")
        return

    print(f"\n✓ Ready to test on {file_count} files and {len(ALL_VALIDATORS)} concepts")

    # FIXED: Updated model names and order
    models_to_test = [
        "Qwen/Qwen3-Embedding-0.6B",
        "intfloat/multilingual-e5-large-instruct",  # FIXED: added intfloat/ prefix
        "google/embeddinggemma-300m",
        "Alibaba-NLP/gte-multilingual-base",
    ]

    all_results = []

    for model_name in models_to_test:
        print(f"\n\n{'#'*60}")
        print(f"Loading model: {model_name}")
        print("#" * 60)

        try:
            # FIXED: Add model-specific loading kwargs
            model_kwargs = {"device": tester.device}

            # FIXED: Add trust_remote_code for Alibaba/gte models
            if "Alibaba-NLP" in model_name or "gte-multilingual" in model_name:
                model_kwargs["trust_remote_code"] = True
                print("  → Using trust_remote_code=True")

            # FIXED: Add trust_remote_code for nomic/qwen models
            if "nomic" in model_name.lower() or "qwen" in model_name.lower():
                model_kwargs["trust_remote_code"] = True
                print("  → Using trust_remote_code=True")

            # Optional: Use fp16 for memory efficiency on GPU
            if tester.device == "cuda":
                model_kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
                print("  → Using torch.float16 for memory efficiency")

            model = SentenceTransformer(model_name, **model_kwargs)

            results = tester.test_model(model_name, model)
            all_results.append(results)

            # Save individual results
            safe_name = model_name.replace("/", "_")
            tester.save_results(results, f"results_{safe_name}.json")

            # Clear memory
            del model
            if tester.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

        except Exception as e:
            print(f"❌ Failed to test {model_name}: {e}")
            import traceback

            traceback.print_exc()
            all_results.append({"model": model_name, "error": str(e)})
            continue

    # Generate comparison
    if all_results:
        comparison = tester.compare_models(all_results)
        print("\n\n" + comparison)

        # Save comparison
        with open("comparison.md", "w") as f:
            f.write(comparison)
        print("\n💾 Comparison saved to comparison.md")

        # Save all results
        tester.save_results(
            {"all_models": all_results, "comparison_table": comparison},
            "all_results.json",
        )


if __name__ == "__main__":
    main()
