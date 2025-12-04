"""
Quick Validation Script: Test CodeRankEmbed on 5 Concepts
Run this FIRST to validate the fix before running full test suite
Expected time: 2-3 minutes
"""

import json
import time
from pathlib import Path
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from concept_validators import ALL_VALIDATORS, validate_file_for_concept


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def quick_test_coderank():
    """Quick test of CodeRankEmbed on 5 representative concepts"""
    
    print("\n" + "="*60)
    print("QUICK VALIDATION: CodeRankEmbed")
    print("="*60)
    
    # Setup device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    
    # Load model
    print("\n📦 Loading nomic-ai/CodeRankEmbed...")
    try:
        model = SentenceTransformer(
            "nomic-ai/CodeRankEmbed",
            trust_remote_code=True,
            device=device
        )
        print("✅ Model loaded")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Load test files
    print("\n📂 Loading test files...")
    test_files = {}
    test_data_dir = Path("test_code")
    
    for lang_dir in ["python", "javascript"]:
        lang_path = test_data_dir / lang_dir
        if not lang_path.exists():
            print(f"  ⚠️ {lang_path} not found. Run dataset_generator.py first!")
            return
        
        for filepath in lang_path.glob("*.*"):
            if filepath.suffix in [".py", ".js", ".jsx"]:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                relative_path = str(filepath.relative_to(test_data_dir))
                test_files[relative_path] = content
    
    print(f"✅ Loaded {len(test_files)} files")
    
    if len(test_files) == 0:
        print("❌ No test files found!")
        return
    
    # Embed files (NO prefix for documents with CodeRankEmbed)
    print("\n🔄 Embedding code files...")
    file_list = list(test_files.keys())
    content_list = [test_files[f] for f in file_list]
    
    file_embeddings = model.encode(
        content_list,
        show_progress_bar=True,
        batch_size=8,
        device=device,
        convert_to_numpy=True
    )
    
    file_embedding_dict = {
        filepath: emb 
        for filepath, emb in zip(file_list, file_embeddings)
    }
    
    print(f"✅ Embedded {len(file_embedding_dict)} files")
    
    # Test 5 representative concepts
    test_concepts = [
        "async await python",           # High importance
        "promises javascript",          # High importance
        "class inheritance python",     # Previously succeeded
        "decorators python",            # Previously failed
        "array methods javascript"      # Mid-range
    ]
    
    print(f"\n🧪 Testing {len(test_concepts)} concepts...")
    print("-" * 60)
    
    results = []
    
    for concept in test_concepts:
        # Embed query WITH prefix
        query_text = f"Represent this query for searching relevant code: {concept}"
        query_embedding = model.encode(query_text, device=device, convert_to_numpy=True)
        
        # Calculate similarities
        similarities = {
            filepath: cosine_similarity(query_embedding, file_emb)
            for filepath, file_emb in file_embedding_dict.items()
        }
        
        # Get top 5
        top_5 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Validate
        valid_count = 0
        for filepath, score in top_5:
            content = test_files[filepath]
            if validate_file_for_concept(filepath, content, concept):
                valid_count += 1
        
        p5 = valid_count / 5.0
        p1 = 1.0 if validate_file_for_concept(top_5[0][0], test_files[top_5[0][0]], concept) else 0.0
        
        results.append({
            "concept": concept,
            "p5": p5,
            "p1": p1,
            "valid_count": valid_count
        })
        
        status = "✅" if p5 >= 0.6 else ("⚠️" if p5 >= 0.4 else "❌")
        print(f"{status} {concept:35s} P@5: {p5:.2f} | Valid: {valid_count}/5")
    
    # Summary
    avg_p5 = sum(r["p5"] for r in results) / len(results)
    avg_p1 = sum(r["p1"] for r in results) / len(results)
    pass_count = sum(1 for r in results if r["p5"] >= 0.6)
    
    print("\n" + "="*60)
    print("QUICK TEST RESULTS")
    print("="*60)
    print(f"Average P@5:    {avg_p5:.1%}")
    print(f"Average P@1:    {avg_p1:.1%}")
    print(f"Concepts Passed: {pass_count}/{len(results)} (≥60% P@5)")
    print("="*60)
    
    # Decision
    if avg_p5 >= 0.50:
        print("\n🎉 PROMISING! Proceed with full test suite.")
        print("   Run: python test_embeddings_fixed.py")
    elif avg_p5 >= 0.35:
        print("\n⚠️  MIXED RESULTS. Full test recommended to confirm.")
        print("   Run: python test_embeddings_fixed.py")
    else:
        print("\n❌ POOR RESULTS. May need to investigate further.")
        print("   Check if dataset is loaded correctly.")
    
    # Save results
    output = {
        "model": "nomic-ai/CodeRankEmbed",
        "test_type": "quick_validation",
        "concepts_tested": len(test_concepts),
        "avg_p5": avg_p5,
        "avg_p1": avg_p1,
        "pass_count": pass_count,
        "results": results
    }
    
    with open("quick_test_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n💾 Results saved to quick_test_results.json")


if __name__ == "__main__":
    quick_test_coderank()