# Embedding Model Recommendations for Phase 1

**Research Date:** December 2025  
**Purpose:** Natural language → code semantic search

---

## Top 3 Models to Test

### 1. **nomic-ai/nomic-embed-text-v1.5** (RECOMMENDED BASELINE)

**Why Test This:**
- Most popular open source embedder on Hugging Face with over 35 million downloads
- Outperforms OpenAI Embeddings on MTEB benchmark at only 137M parameters
- Delivers over 100 queries per second on standard M2 MacBook
- Fully open source (Apache 2.0)

**Specs:**
- **Size:** 137M parameters (~550MB download)
- **Context:** 8,192 tokens
- **CPU-only:** ✅ Yes - very fast on CPU
- **Languages:** 100+ languages, optimized for English

**Installation:**
```bash
pip install sentence-transformers
```

**Usage:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
embeddings = model.encode(["your code here", "query text"])
```

**Expected Performance:** 60-75% P@5 on code tasks (general model, not code-specific)

---

### 2. **nomic-ai/CodeRankEmbed** (CODE-OPTIMIZED, SMALL)

**Why Test This:**
- Specialized code embedding model at only 521MB
- Achieves state-of-the-art performance on CodeSearchNet benchmark for its size
- Designed specifically for code retrieval (natural language → code mapping)
- Much smaller than full nomic-embed-code (521MB vs 7.5GB)

**Specs:**
- **Size:** 137M parameters (~521MB)
- **Context:** Long context support
- **CPU-only:** ✅ Yes
- **Languages:** Python, Java, Ruby, PHP, JavaScript, Go

**Installation:**
```bash
pip install sentence-transformers
```

**Usage:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)

# IMPORTANT: Queries require prefix
query = "Represent this query for searching relevant code: promises in javascript"
code = "function fetch() { return new Promise(...) }"

query_embed = model.encode(query)
code_embed = model.encode(code)
```

**Expected Performance:** 70-80% P@5 on code tasks (code-specific model)

---

### 3. **BAAI/bge-small-en-v1.5** (ULTRA-LIGHTWEIGHT BASELINE)

**Why Test This:**
- Widely used baseline with 22M parameters, extremely fast and low-resource
- Ideal for apps with millions of queries per day
- Good benchmark for "minimum viable" performance

**Specs:**
- **Size:** 33M parameters (~130MB)
- **Context:** 512 tokens
- **CPU-only:** ✅ Yes - extremely fast
- **Languages:** English primarily

**Installation:**
```bash
pip install sentence-transformers
```

**Usage:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
embeddings = model.encode(["code", "query"])
```

**Expected Performance:** 50-65% P@5 on code tasks (general model, not optimized for code)

---

## Alternative: If You Have GPU Available

### **nomic-ai/nomic-embed-code** (7B, CODE-SPECIFIC)

**Why Consider:**
- State-of-the-art 7B parameter code embedding model that outperforms Voyage Code 3 and OpenAI Embed 3 Large on CodeSearchNet
- Supports Python, Java, Ruby, PHP, JavaScript, and Go

**Trade-offs:**
- **Size:** 7B parameters (~7.5GB download)
- **Requires:** GPU for reasonable speed (or very slow on CPU)
- **Expected Performance:** 80-90% P@5 (best possible, but violates CPU-only constraint)

**Decision:** Skip for Phase 1 unless you have GPU. Use CodeRankEmbed instead (same training, much smaller).

---

## Recommended Testing Order

### Test 1: CodeRankEmbed (Code-Specific, Small)
**Hypothesis:** Should perform best as it's optimized for NL→code mapping

**If P@5 ≥ 70%:** ✅ GO - This is your winner  
**If P@5 50-70%:** Continue to Test 2  
**If P@5 < 50%:** Still continue to validate with general models

---

### Test 2: nomic-embed-text-v1.5 (General, Popular)
**Hypothesis:** Should perform reasonably well due to general semantic understanding

**If P@5 ≥ 70%:** ✅ GO - Use this model (more versatile than code-only)  
**If P@5 50-70%:** ⚠️ CONDITIONAL - Try file extension hints  
**If P@5 < 50%:** Continue to Test 3 to establish floor

---

### Test 3: bge-small-en-v1.5 (Ultra-Light Baseline)
**Hypothesis:** Establishes "minimum viable" performance floor

**If P@5 ≥ 70%:** 🎉 Amazing! Even baseline works  
**If P@5 50-70%:** Confirms code-specific models needed  
**If P@5 < 50%:** Confirms our approach is correct (baseline too weak)

---

## Quick Comparison Table

| Model | Size | CPU Speed | Code-Specific | Expected P@5 | Priority |
|-------|------|-----------|---------------|--------------|----------|
| CodeRankEmbed | 521MB | Fast | ✅ Yes | 70-80% | 🥇 Test First |
| nomic-embed-text-v1.5 | 550MB | Very Fast | ❌ No | 60-75% | 🥈 Test Second |
| bge-small-en-v1.5 | 130MB | Extremely Fast | ❌ No | 50-65% | 🥉 Baseline |
| nomic-embed-code (7B) | 7.5GB | Slow (CPU) | ✅ Yes | 80-90% | ⏸️ Skip (GPU req'd) |

---

## Updated test_embeddings.py Configuration

Replace the `models_to_test` list with:

```python
models_to_test = [
    "nomic-ai/CodeRankEmbed",           # Test 1: Code-specific, small
    "nomic-ai/nomic-embed-text-v1.5",   # Test 2: General, popular
    "BAAI/bge-small-en-v1.5",           # Test 3: Ultra-light baseline
]
```

**Important:** CodeRankEmbed requires `trust_remote_code=True`:

```python
# In test_model() function, update model loading:
if "CodeRankEmbed" in model_name or "nomic-ai" in model_name:
    model = SentenceTransformer(model_name, trust_remote_code=True)
else:
    model = SentenceTransformer(model_name)

# For CodeRankEmbed queries, add prefix:
if "CodeRankEmbed" in model_name:
    concept_query = f"Represent this query for searching relevant code: {concept_name}"
else:
    concept_query = concept_name
```

---

## Why These Models?

### ✅ All Meet Requirements:
- CPU-only inference ✓
- Size <1GB ✓
- Active maintenance (2024-2025) ✓
- Proven benchmarks ✓
- Easy pip installation ✓
- Open source ✓

### 📊 Covers All Scenarios:
1. **Code-specific small model** (CodeRankEmbed)
2. **General-purpose strong model** (nomic-embed-text)
3. **Ultra-efficient baseline** (bge-small)

### 🎯 Decision Coverage:
- If CodeRankEmbed ≥70% → GO with code-specific model
- If nomic-embed ≥70% → GO with general model (more versatile)
- If both <70% but >50% → CONDITIONAL (try hints)
- If all <50% → NO-GO (approach not viable)

---

## Installation Before Testing

```bash
# Activate your venv
source venv/bin/activate

# Install required packages
pip install sentence-transformers torch numpy

# Pre-download models (optional, saves time during testing)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/CodeRankEmbed', trust_remote_code=True)"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
```

---

## Key Insights from Research

1. Nomic Embed ecosystem includes specialized code models with efficient inference
2. CodeRankEmbed trained with dual-consistency filtering and progressive hard negative mining - specifically designed for your use case
3. Modern embedding models can handle diverse input types and support instruction-based prompting
4. Small models (137M params) can match or exceed larger models when properly trained

---

## What to Expect

### Best Case Scenario:
- CodeRankEmbed: 75-80% P@5
- Decision: ✅ GO to Phase 2 immediately
- Timeline: Results in 3-6 hours

### Realistic Scenario:
- CodeRankEmbed: 65-70% P@5
- nomic-embed-text: 60-65% P@5
- Decision: ⚠️ Try file extension hints, then GO
- Timeline: Results in 4-8 hours

### Challenging Scenario:
- All models: 50-60% P@5
- Decision: ⚠️ CONDITIONAL - requires enhancement strategies
- Timeline: Results + 2 hours for hint testing

### Worst Case:
- All models: <50% P@5
- Decision: ❌ NO-GO - approach not viable
- Timeline: Results in 3-6 hours, then pivot planning

---

## Next Steps

1. **Update test_embeddings.py** with the three models above
2. **Run setup:** `bash setup_phase1.sh`
3. **Generate dataset:** `python dataset_generator.py` (1-2 hours)
4. **Test models:** `python test_embeddings.py` (3-6 hours)
5. **Review results:** `cat comparison.md`
6. **Make decision:** GO/CONDITIONAL/NO-GO based on P@5 scores

---

## References

- Nomic Embed Ecosystem: https://www.nomic.ai/blog/posts/embed-ecosystem
- CodeRankEmbed on HuggingFace: https://huggingface.co/nomic-ai/CodeRankEmbed
- BGE Models: https://huggingface.co/BAAI/bge-small-en-v1.5
- MTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard

---

**Ready to begin?** Run `bash setup_phase1.sh` and then `python dataset_generator.py`
