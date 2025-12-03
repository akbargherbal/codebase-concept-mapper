# Phase 1: Embedding Viability Test

**CRITICAL GO/NO-GO DECISION POINT FOR THE ENTIRE PROJECT**

This phase answers the fundamental question: **Can embedding models reliably map natural language concepts to code implementations?**

---

## Quick Start

```bash
# 1. Setup environment
bash setup_phase1.sh

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 3. Run complete pipeline
bash run_phase1.sh
```

**Total time:** 6-8 hours (mostly automated waiting)

---

## What Gets Built

### 1. Test Dataset (`dataset_generator.py`)
- Clones 8 real open-source repositories
- Randomly samples 50-100 code files (Python + JavaScript)
- Creates realistic "haystack" for semantic search testing
- **No cherry-picking** - ensures unbiased evaluation

### 2. Concept Validators (`concept_validators.py`)
- 20 programming concepts (10 Python, 10 JavaScript)
- Content-based validation (NOT filename matching)
- Language disambiguation (prevents "async" matching both Python & JS)

### 3. Model Testing Framework (`test_embeddings.py`)
- Batch embedding generation
- Cosine similarity ranking
- Automated validation of top-5 results
- Metrics: Precision@1, Precision@5, Mean Reciprocal Rank

### 4. Comparison Report (`comparison.md`)
- Model performance table
- GO/NO-GO recommendation
- Next steps based on results

---

## Decision Criteria

### ✅ GO TO PHASE 2
- **Best model achieves ≥70% Precision@5**
- Inference time <10 seconds for 20 queries
- Document winning model, proceed to chunking tests

### ⚠️ CONDITIONAL GO
- **Best model achieves 50-70% Precision@5**
- Try adding file extension hints (e.g., "promises in .js files")
- Re-test with hints. If improves to ≥70% → GO

### ❌ NO-GO (STOP PROJECT)
- **All models <50% Precision@5**
- GPU required for acceptable accuracy
- Inference time >30 seconds per query

**Pivot options:**
1. Wait 6 months for better models
2. Switch to keyword-based search + LLM reranking
3. Different project: Extend video RAG (both inputs are NL)

---

## File Structure

```
codebase-concept-mapper/
├── dataset_generator.py       # Clones repos, samples files
├── concept_validators.py      # 20 content-based validators
├── test_embeddings.py         # Tests models, generates comparison
├── requirements.txt           # Python dependencies
├── setup_phase1.sh           # Environment setup
├── run_phase1.sh             # Complete pipeline runner
├── README_PHASE1.md          # This file
│
├── test_code/                 # Generated dataset
│   ├── python/               # Python code samples
│   ├── javascript/           # JavaScript code samples
│   └── metadata.json         # Dataset provenance
│
├── temp_repos/               # Cloned repositories (gitignored)
│
└── results_*.json            # Test results
    ├── results_model1.json
    ├── all_results.json
    └── comparison.md
```

---

## Step-by-Step Guide

### Step 1: Research Embedding Models (BEFORE RUNNING TESTS)

**CRITICAL:** You need to identify 3 candidate models before testing.

Use this Deep Research query:

```
Find the top 3 open-source embedding models (as of early 2025) for 
code semantic search that:

1. Can run locally on CPU (no GPU required for inference)
2. Have proven benchmarks for natural language → code retrieval
3. Support Python installation via pip or Hugging Face
4. Model size <1GB for quick testing
5. Active maintenance (updated in last 6 months)

Prioritize models with:
- Public benchmarks showing >60% retrieval accuracy on code tasks
- Documentation for local inference
- Examples of semantic code search

Return for each model:
- Model name and identifier (for sentence-transformers or HF)
- Model size and parameter count
- Installation command (pip install ...)
- Benchmark results on code retrieval tasks
- Link to usage example or documentation

Expected candidates might include:
- nomic-ai/nomic-embed-text-v1.5
- BAAI/bge-small-en-v1.5
- sentence-transformers/all-MiniLM-L6-v2 (baseline)
- Code-specific models like microsoft/codebert-base

Verify these are still current and recommend best 3 for testing.
```

**Update `test_embeddings.py`** with the model names from research:

```python
models_to_test = [
    "sentence-transformers/all-MiniLM-L6-v2",  # Baseline
    "your-researched-model-1",
    "your-researched-model-2",
]
```

---

### Step 2: Generate Test Dataset

```bash
python dataset_generator.py
```

**What it does:**
1. Clones 8 repositories (Flask, Express, React, etc.)
2. Randomly samples 12 files per repo
3. Filters for valid code files (50-500 lines, no tests/configs)
4. Copies to `test_code/` with sanitized names
5. Saves metadata to `test_code/metadata.json`

**Expected output:**
- 50-100 code files in `test_code/python/` and `test_code/javascript/`
- Roughly 50% Python, 50% JavaScript
- Random sampling ensures unbiased test set

**Time:** 1-2 hours (mostly Git cloning)

---

### Step 3: Test Embedding Models

```bash
python test_embeddings.py
```

**What it does:**
1. Loads all test files (50-100 files)
2. For each model:
   - Batch embeds all files
   - Tests 20 concept queries
   - Ranks files by cosine similarity
   - Validates top-5 results using concept_validators
   - Calculates P@1, P@5, MRR
3. Generates comparison table
4. Makes GO/NO-GO recommendation

**Expected output:**
- Per-model results: `results_*.json`
- Combined results: `all_results.json`
- Decision report: `comparison.md`

**Time:** 1-2 hours per model (3 models = 3-6 hours)

---

### Step 4: Review Results & Make Decision

```bash
cat comparison.md
```

**Look for:**
- Best model's Precision@5 score
- Pass rate (% of concepts with P@5 ≥ 60%)
- Inference time
- GO/NO-GO recommendation

**Example good result:**

```
| Model | P@5 | P@1 | Pass Rate | Decision |
|-------|-----|-----|-----------|----------|
| nomic-embed-v1.5 | 73% | 61% | 80% | ✅ GO |
```

**Example bad result:**

```
| Model | P@5 | P@1 | Pass Rate | Decision |
|-------|-----|-----|-----------|----------|
| all-MiniLM-L6 | 42% | 28% | 35% | ❌ NO-GO |
```

---

## Understanding the Metrics

### Precision@5 (P@5)
**Definition:** Of the top 5 retrieved files, how many actually implement the concept?

**Why it matters:** Users will review top results, not just #1. A model with 80% P@5 means 4 out of 5 results are relevant.

**Threshold:** ≥70% for GO decision

### Precision@1 (P@1)
**Definition:** Is the top result correct?

**Why it matters:** Strict test - model must rank best match first.

**Threshold:** ≥60% preferred

### Mean Reciprocal Rank (MRR)
**Definition:** Average position of first correct result (1/position).

**Example:** If first correct result is at position 2, RR = 1/2 = 0.5

**Why it matters:** Measures how quickly users find relevant code.

---

## Common Issues & Solutions

### Issue: "No test files found"
**Solution:** Run `dataset_generator.py` first

### Issue: "Git clone failed"
**Solution:** Check internet connection, verify repo URLs still exist

### Issue: Model download fails
**Solution:** 
```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('model-name')"
```

### Issue: Out of memory
**Solution:** Reduce `FILES_PER_REPO` in `dataset_generator.py` to 8

### Issue: All models score <50%
**Solution:** This is a valid outcome - document findings, consider project pivot

---

## What NOT to Do

❌ **Don't hard-code expected filenames** - defeats the purpose of testing semantic search

❌ **Don't cherry-pick test files** - biases results, use random sampling

❌ **Don't skip validation** - raw similarity scores don't prove semantic understanding

❌ **Don't proceed to Phase 2 if <70% P@5** - later phases can't fix fundamentally broken embeddings

❌ **Don't manually curate validators** - they should be objective, reproducible

---

## After Phase 1

### If GO (≥70% P@5):
1. Document winning model in `docs/DECISIONS.md`
2. Note any language-specific performance gaps
3. Proceed to Phase 2: Chunking Quality Tests

### If CONDITIONAL (50-70% P@5):
1. Add file extension hints to queries
2. Re-run tests: `python test_embeddings.py`
3. If now ≥70% → GO, else consider pivot

### If NO-GO (<50% P@5):
1. Document findings in project log
2. Consider alternative approaches:
   - Keyword-based search + LLM reranking
   - Wait for better embedding models
   - Pivot to different project
3. Don't spend weeks trying to "fix" - embeddings either work or don't

---

## Key Insights

1. **Content validation > filename matching** - Model must understand semantics, not memorize names

2. **Random sampling is critical** - Real repos have messy, generic filenames like `utils.js`

3. **Language disambiguation matters** - Prevent "async" matching both Python `async def` and JS `async function`

4. **This gates the project** - No amount of later engineering fixes broken embeddings

5. **Speed is essential** - Queries taking 30+ seconds make tool unusable

---

## Timeline

- **Setup:** 30 minutes
- **Research models:** 2-3 hours
- **Generate dataset:** 1-2 hours (one-time)
- **Test 3 models:** 3-6 hours (mostly waiting)
- **Analysis:** 1 hour

**Total:** 6-8 hours (Day 1 of project)

---

## Next Steps

After completing Phase 1:
- If GO → Proceed to `docs/PHASED_PLAN.md` Phase 2 (Chunking)
- If CONDITIONAL → Try enhancement strategies, re-test
- If NO-GO → Review project pivot options

**Remember:** This phase is designed to fail fast if embeddings don't work. A NO-GO decision after 8 hours is a success - you avoided weeks of wasted effort.
