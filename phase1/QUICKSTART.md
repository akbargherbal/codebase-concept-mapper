# Phase 1 Quick Start Guide

**Goal:** Test if embedding models can map natural language concepts to code in 6-8 hours

---

## Prerequisites

- Python 3.8+
- Git
- 10GB free disk space (for repos + models)
- Internet connection (to clone repos and download models)

---

## Step-by-Step Execution

### Step 1: Setup Environment (5 minutes)

```bash
# Clone/navigate to your project directory
cd codebase-concept-mapper

# Run setup script
bash setup_phase1.sh

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

**Expected output:**
```
✓ Virtual environment created
✓ Dependencies installed
✓ Git is available
```

---

### Step 2: Generate Test Dataset (1-2 hours)

```bash
python dataset_generator.py
```

**What happens:**
- Clones 8 repositories (Flask, Express, React, Django, etc.)
- Randomly samples 12 files per repo
- Filters for valid code files (50-500 lines)
- Copies 50-100 files to `test_code/`
- Saves metadata to `test_code/metadata.json`

**Expected output:**
```
PHASE 1: GENERATING TEST DATASET
✓ Created output directories
📦 Processing PYTHON repositories...
  ✓ Cloned pallets/flask
  Found 45 candidate files
  Sampled 12 files
  ✓ PYTHON: 48 files collected
📦 Processing JAVASCRIPT repositories...
  ✓ JAVASCRIPT: 52 files collected

DATASET GENERATION COMPLETE
Total files: 100
Python: 48
JavaScript: 52
```

**Troubleshooting:**
- If Git clone fails: Check internet connection, try again
- If too few files: Repos might have different structures, but 40+ total is fine
- If disk space error: Reduce `FILES_PER_REPO` in `dataset_generator.py` to 8

---

### Step 3: Test Embedding Models (3-6 hours)

```bash
python test_embeddings.py
```

**What happens:**
- Tests 3 models sequentially:
  1. CodeRankEmbed (code-specific)
  2. nomic-embed-text-v1.5 (general)
  3. bge-small-en-v1.5 (baseline)
- For each model:
  - Embeds all 100 code files (1-2 min)
  - Tests 20 concept queries (5-10 min)
  - Validates top-5 results (instant)
  - Calculates P@1, P@5, MRR
- Generates comparison table
- Makes GO/NO-GO recommendation

**Expected output:**
```
Loading model: nomic-ai/CodeRankEmbed
1️⃣ Embedding test files...
  ✓ Embedded 100 files

2️⃣ Testing concepts...
  ✓ promises javascript                     P@5: 0.80 | P@1: 1
  ✓ async await python                      P@5: 0.80 | P@1: 1
  ✓ react hooks                             P@5: 0.60 | P@1: 1
  ...

RESULTS SUMMARY
Overall Precision@5:  73.5%
Overall Precision@1:  65.0%
Pass Rate (P@5≥60%): 85.0% (17/20)
Inference Time:       8.2s
```

**Progress tracking:**
- Model loading: 30-60 seconds per model
- File embedding: 1-2 minutes per model
- Concept testing: 5-10 minutes per model
- Total per model: ~10 minutes
- 3 models: ~30 minutes + model download time

---

### Step 4: Review Results (5 minutes)

```bash
# Read the comparison report
cat comparison.md

# Or view detailed results
cat results_nomic-ai_CodeRankEmbed.json | jq .overall_precision_at_5
```

**Look for:**

#### ✅ GO Decision (Best case)
```markdown
| Model | P@5 | P@1 | Pass Rate | Decision |
|-------|-----|-----|-----------|----------|
| CodeRankEmbed | 75% | 68% | 85% | ✅ GO |

**✅ PROCEED TO PHASE 2** with `CodeRankEmbed`
- Achieves 75% P@5 (threshold: ≥70%)
- 17/20 concepts pass (P@5≥60%)
```

**Action:** Document model, proceed to Phase 2 chunking tests

---

#### ⚠️ CONDITIONAL Decision (Needs enhancement)
```markdown
| Model | P@5 | P@1 | Pass Rate | Decision |
|-------|-----|-----|-----------|----------|
| nomic-embed-text | 62% | 54% | 70% | ⚠️ CONDITIONAL |

**⚠️ CONDITIONAL PROCEED** - Try enhancement strategies
- Best model: `nomic-embed-text` at 62% P@5
- Recommendation: Add file extension hints
```

**Action:** Try file extension hints (see Step 5), then re-test

---

#### ❌ NO-GO Decision (Project not viable)
```markdown
| Model | P@5 | P@1 | Pass Rate | Decision |
|-------|-----|-----|-----------|----------|
| bge-small | 45% | 32% | 40% | ❌ NO-GO |

**❌ STOP PROJECT** - Embedding approach not viable
- Best model: `bge-small` at 45% P@5
- Threshold: ≥50% for conditional proceed
```

**Action:** Consider project pivot or wait for better models

---

### Step 5: Enhancement (If CONDITIONAL)

If best model scored 50-70% P@5, try adding file extension hints:

**Update concept_validators.py:**
```python
# Add language hints to queries
ENHANCED_QUERIES = {
    "promises javascript": "promises in .js files",
    "async await python": "async await in .py files",
    # ... etc
}
```

**Re-run test:**
```bash
python test_embeddings.py
```

**Decision after enhancement:**
- If P@5 now ≥70% → ✅ GO to Phase 2
- If still <70% → Consider scope reduction (Python-only) or pivot

---

## Complete Pipeline (Automated)

If you want to run everything in one go:

```bash
bash run_phase1.sh
```

This will:
1. Check if dataset exists (prompt to regenerate if yes)
2. Generate dataset if needed
3. Test all 3 models
4. Generate comparison report
5. Display decision

---

## Understanding Your Results

### What is Precision@5?

If you query "promises in javascript" and the model returns top 5 files:

**Example 1: Good Result (P@5 = 0.80)**
```
1. ✓ axios_client.js       (has Promise code)
2. ✓ fetch_utils.js        (has async/await)
3. ✗ router.js             (no promises)
4. ✓ api_handler.js        (has .then() chains)
5. ✓ data_loader.js        (has Promise.all)
```
**4 out of 5 correct = 80% P@5**

**Example 2: Poor Result (P@5 = 0.20)**
```
1. ✓ promises.js           (has Promise code)
2. ✗ config.js             (no promises)
3. ✗ index.js              (just imports)
4. ✗ types.ts              (TypeScript types)
5. ✗ utils.py              (wrong language!)
```
**1 out of 5 correct = 20% P@5**

### Why 70% Threshold?

- **≥70% P@5:** 3-4 out of 5 results are relevant → users can find what they need
- **50-70% P@5:** 2-3 out of 5 relevant → workable with hints
- **<50% P@5:** ≤2 out of 5 relevant → too much noise, not usable

---

## File Structure After Completion

```
codebase-concept-mapper/
├── venv/                                # Virtual environment
├── test_code/                           # Generated test dataset
│   ├── python/                          # 40-50 Python files
│   ├── javascript/                      # 40-50 JavaScript files
│   └── metadata.json                    # Dataset provenance
├── temp_repos/                          # Cloned repos (can delete after)
├── results_nomic-ai_CodeRankEmbed.json  # Model 1 results
├── results_nomic-ai_nomic-embed-text-v1.5.json  # Model 2 results
├── results_BAAI_bge-small-en-v1.5.json  # Model 3 results
├── all_results.json                     # Combined results
└── comparison.md                        # Decision report
```

---

## Time Budget

| Task | Time | Can Run While... |
|------|------|------------------|
| Setup | 5 min | Active |
| Dataset generation | 1-2 hours | Background (Git cloning) |
| Model testing | 3-6 hours | Background (model inference) |
| Results review | 5 min | Active |
| **Total** | **4-8 hours** | **Mostly automated** |

**Reality:** Start in the morning, review results by afternoon.

---

## Common Pitfalls

### ❌ Don't: Cherry-pick test files
**Why:** Biases results. Random sampling proves real-world viability.

### ❌ Don't: Skip validation
**Why:** High similarity scores don't prove semantic understanding.

### ❌ Don't: Proceed to Phase 2 if <70% P@5
**Why:** Later phases can't fix fundamentally broken embeddings.

### ✅ Do: Trust the process
**Why:** This phase is designed to fail fast if embeddings don't work.

### ✅ Do: Document findings
**Why:** Even NO-GO is valuable learning (saves weeks of wasted effort).

---

## What's Next?

### If ✅ GO:
1. Document winning model in `docs/DECISIONS.md`
2. Read `docs/PHASED_PLAN.md` Phase 2 (Chunking Tests)
3. Proceed to code chunking quality validation

### If ⚠️ CONDITIONAL:
1. Try file extension hints (Step 5)
2. If improves to ≥70% → GO
3. If still <70% → Consider Python-only scope

### If ❌ NO-GO:
1. Document findings in project log
2. Review alternative approaches:
   - Keyword-based search + LLM reranking
   - Wait 6 months for better models
   - Pivot to video RAG extension (proven approach)
3. Don't force it - embeddings either work or don't

---

## Getting Help

### Model download issues:
```bash
# Pre-download manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/CodeRankEmbed', trust_remote_code=True)"
```

### Out of memory:
```python
# Reduce batch size in test_embeddings.py
embeddings = model.encode(content_list, batch_size=8)  # Default is 32
```

### Slow inference:
- Normal for first run (model download + compilation)
- Subsequent runs are much faster (cached)
- CodeRankEmbed: ~5-10 min for 100 files
- bge-small: ~2-5 min for 100 files

### Results seem wrong:
```bash
# Check validator logic on sample
python concept_validators.py

# Inspect specific result
cat results_*.json | jq '.per_concept[] | select(.concept == "promises javascript")'
```

---

## Success Looks Like...

```bash
$ cat comparison.md

## Model Comparison

| Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Decision |
|-------|-----|-----|-----|-----------|----------|----------|
| nomic-ai/CodeRankEmbed | 75.5% | 68.0% | 0.812 | 85.0% | 8.2 | ✅ GO |
| nomic-ai/nomic-embed-text-v1.5 | 71.0% | 62.0% | 0.755 | 75.0% | 6.8 | ✅ GO |
| BAAI/bge-small-en-v1.5 | 58.5% | 45.0% | 0.621 | 55.0% | 4.1 | ⚠️ CONDITIONAL |

### Recommendation

**✅ PROCEED TO PHASE 2** with `nomic-ai/CodeRankEmbed`

- Achieves 75.5% P@5 (threshold: ≥70%)
- 17/20 concepts pass (P@5≥60%)
- Fast inference (8.2s for 20 queries)
- Code-optimized model shows clear advantage
```

**That's a wrap! You've proven embedding viability and can confidently proceed to Phase 2.**

---

## Ready? Let's Go!

```bash
bash setup_phase1.sh
source venv/bin/activate
python dataset_generator.py
# Go get coffee ☕
python test_embeddings.py
# Go get lunch 🍔
cat comparison.md
# Make your GO/NO-GO decision 🎯
```

**Total active time:** ~15 minutes  
**Total elapsed time:** 4-8 hours  
**Value:** Validates core assumption of entire project 🚀
