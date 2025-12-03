# Phase 1 Project Structure

Complete file organization and relationships for the embedding viability test.

---

## Directory Structure

```
codebase-concept-mapper/
│
├── docs/                           # Documentation (already exists)
│   ├── CONTEXT.md                  # Project overview
│   ├── PHASED_PLAN.md             # All phases
│   └── phase1_context.md          # Phase 1 details
│
├── phase1/                         # Phase 1 implementation (create this)
│   ├── dataset_generator.py       # Clones repos, samples files
│   ├── concept_validators.py      # 20 content-based validators
│   ├── test_embeddings.py         # Tests models, generates comparison
│   ├── requirements.txt           # Python dependencies
│   ├── setup_phase1.sh           # Environment setup
│   ├── run_phase1.sh             # Complete pipeline runner
│   ├── QUICKSTART.md             # Step-by-step guide
│   ├── README_PHASE1.md          # Detailed documentation
│   ├── MODEL_RECOMMENDATIONS.md  # Embedding model research
│   └── RESEARCH_QUERY.md         # Template for model research
│
├── test_code/                     # Generated dataset (created by script)
│   ├── python/                    # Python code samples
│   │   ├── pallets_flask_01.py
│   │   ├── pallets_flask_02.py
│   │   └── ...                    # 40-50 Python files
│   ├── javascript/                # JavaScript code samples
│   │   ├── axios_axios_01.js
│   │   ├── expressjs_express_01.js
│   │   └── ...                    # 40-50 JavaScript files
│   └── metadata.json              # Dataset provenance
│
├── temp_repos/                    # Cloned repositories (gitignored)
│   ├── flask/
│   ├── requests/
│   ├── axios/
│   └── ...                        # 8 repositories
│
├── results/                       # Test results (created by script)
│   ├── results_nomic-ai_CodeRankEmbed.json
│   ├── results_nomic-ai_nomic-embed-text-v1.5.json
│   ├── results_BAAI_bge-small-en-v1.5.json
│   ├── all_results.json           # Combined results
│   └── comparison.md              # Decision report
│
├── venv/                          # Virtual environment (gitignored)
│
├── .gitignore                     # Git ignore rules
└── README.md                      # Project root README
```

---

## File Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1 WORKFLOW                         │
└─────────────────────────────────────────────────────────────┘

[setup_phase1.sh]
    â†"
Creates venv, installs requirements.txt
    â†"
[dataset_generator.py]
    â†"
Clones repos from TEST_REPOS → temp_repos/
Samples random files → test_code/python/ and test_code/javascript/
Generates metadata.json
    â†"
[test_embeddings.py]
    ├─ Loads files from test_code/
    ├─ Uses validators from [concept_validators.py]
    ├─ Tests 3 models sequentially
    â†"
Generates:
    ├─ results/results_MODEL1.json
    ├─ results/results_MODEL2.json
    ├─ results/results_MODEL3.json
    ├─ results/all_results.json
    └─ results/comparison.md
    â†"
[comparison.md] → GO/NO-GO decision
```

---

## Key Files Explained

### Core Implementation

#### `dataset_generator.py` (300 lines)
**Purpose:** Generate realistic test dataset from real open-source repos

**Key Functions:**
- `clone_repo()` - Git clone with depth=1
- `is_valid_code_file()` - Filter logic (50-500 lines, no tests)
- `sample_files()` - Random sampling (no cherry-picking)
- `copy_file_to_output()` - Sanitize names, organize by language

**Input:** Hardcoded `TEST_REPOS` config
**Output:** `test_code/` directory + `metadata.json`

---

#### `concept_validators.py` (400 lines)
**Purpose:** Content-based validation (NOT filename matching)

**Key Classes:**
- `ConceptValidator` - Generic validator with must_contain/must_not rules

**Key Data:**
- `PYTHON_VALIDATORS` - 10 Python concepts
- `JAVASCRIPT_VALIDATORS` - 10 JavaScript concepts
- `ALL_VALIDATORS` - Combined 20 concepts

**Critical Feature:** Language disambiguation via `must_not_contain`

**Example:**
```python
"async await python": {
    "must_contain_any": ["async def", "await ", "asyncio"],
    "must_not_contain": ["Promise", "async function"],  # Blocks JS
    "min_occurrences": 2
}
```

---

#### `test_embeddings.py` (500 lines)
**Purpose:** Test models, calculate metrics, generate comparison

**Key Classes:**
- `EmbeddingModelTester` - Main test orchestration

**Key Methods:**
- `load_test_files()` - Load all test files to memory
- `test_model()` - Test single model on all concepts
- `compare_models()` - Generate comparison table
- `save_results()` - Save JSON results

**Flow:**
```python
for model in [Model1, Model2, Model3]:
    # 1. Batch embed all files
    file_embeddings = model.encode(all_files)
    
    # 2. For each concept:
    for concept in 20_concepts:
        query_embed = model.encode(concept)
        top_5 = rank_by_similarity(query_embed, file_embeddings)
        valid_count = sum(validate(file, concept) for file in top_5)
        p5 = valid_count / 5
    
    # 3. Aggregate metrics
    overall_p5 = mean(all_p5_scores)
```

---

### Documentation

#### `QUICKSTART.md` (Actionable)
- Step-by-step execution guide
- Expected outputs at each step
- Troubleshooting common issues
- What results mean

**Audience:** You, right now, ready to run tests

---

#### `README_PHASE1.md` (Comprehensive)
- Project overview
- Decision criteria explanation
- Metric definitions (P@1, P@5, MRR)
- Timeline estimates
- What NOT to do

**Audience:** Future you, reviewing decisions

---

#### `MODEL_RECOMMENDATIONS.md` (Research)
- 3 models identified with specs
- Installation instructions
- Expected performance
- Trade-offs analysis

**Audience:** Understanding model selection

---

#### `RESEARCH_QUERY.md` (Template)
- Deep research query for finding models
- Follow-up queries if needed
- Evaluation checklist

**Audience:** If you need to research different models later

---

### Scripts

#### `setup_phase1.sh` (Initialization)
```bash
# What it does:
1. Check Python 3.8+
2. Create venv if not exists
3. Activate venv
4. Install requirements.txt
5. Check Git available
```

---

#### `run_phase1.sh` (Automation)
```bash
# What it does:
1. Check venv activated
2. Prompt to regenerate dataset if exists
3. Run dataset_generator.py
4. Run test_embeddings.py
5. Display comparison.md
```

---

#### `requirements.txt` (Dependencies)
```
sentence-transformers>=2.2.0  # Embedding models
numpy>=1.24.0                 # Vector operations
torch>=2.0.0                  # Model backend
pytest>=7.0.0                 # Testing (optional)
```

---

## Execution Flow

### Manual Execution

```bash
# 1. Setup (once)
bash setup_phase1.sh
source venv/bin/activate

# 2. Generate dataset (once)
python dataset_generator.py  # 1-2 hours

# 3. Test models (repeatable)
python test_embeddings.py    # 3-6 hours

# 4. Review results
cat comparison.md
```

### Automated Execution

```bash
# All-in-one
bash run_phase1.sh  # 4-8 hours total
```

---

## Output Files

### `test_code/metadata.json`
```json
{
  "generation_date": "2025-12-03T10:00:00",
  "repos": {
    "pallets/flask": {
      "url": "https://github.com/pallets/flask",
      "source_dir": "src/flask",
      "files_sampled": 12,
      "files": [...]
    }
  },
  "stats": {
    "total_files": 100,
    "python_files": 48,
    "javascript_files": 52
  }
}
```

---

### `results/results_MODEL.json`
```json
{
  "model": "nomic-ai/CodeRankEmbed",
  "overall_precision_at_5": 0.755,
  "overall_precision_at_1": 0.680,
  "pass_rate": 0.850,
  "inference_time_seconds": 8.2,
  "per_concept": [
    {
      "concept": "promises javascript",
      "precision_at_5": 0.80,
      "precision_at_1": 1.0,
      "top_5_results": [
        {"file": "axios_01.js", "score": 0.92, "valid": true},
        ...
      ]
    },
    ...
  ]
}
```

---

### `results/comparison.md`
```markdown
## Model Comparison

| Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Decision |
|-------|-----|-----|-----|-----------|----------|----------|
| CodeRankEmbed | 75.5% | 68.0% | 0.812 | 85.0% | 8.2 | ✅ GO |
| nomic-embed-text | 71.0% | 62.0% | 0.755 | 75.0% | 6.8 | ✅ GO |
| bge-small | 58.5% | 45.0% | 0.621 | 55.0% | 4.1 | ⚠️ CONDITIONAL |

### Recommendation
**✅ PROCEED TO PHASE 2** with `nomic-ai/CodeRankEmbed`
```

---

## What to Commit

### âœ… Commit These:
```
phase1/
  ├── *.py                  # All Python scripts
  ├── *.sh                  # All shell scripts
  ├── *.md                  # All documentation
  ├── requirements.txt
  └── .gitignore            # Ignore patterns below
```

### ❌ Ignore These (.gitignore):
```
# Virtual environment
venv/
.venv/

# Cloned repositories (large, can regenerate)
temp_repos/

# Test data (can regenerate)
test_code/

# Results (generated output)
results/
*.json

# Python artifacts
__pycache__/
*.pyc
*.pyo
*.egg-info/

# System files
.DS_Store
Thumbs.db
```

---

## Dependencies Between Files

```
┌─────────────────────────────────────────────────────────┐
│ STANDALONE FILES (No dependencies)                      │
└─────────────────────────────────────────────────────────┘
- setup_phase1.sh
- requirements.txt
- concept_validators.py (can run standalone with test)
- MODEL_RECOMMENDATIONS.md
- RESEARCH_QUERY.md
- QUICKSTART.md

┌─────────────────────────────────────────────────────────┐
│ DEPENDENT FILES                                         │
└─────────────────────────────────────────────────────────┘

dataset_generator.py
    └── Depends on: Git (external)

test_embeddings.py
    ├── Depends on: concept_validators.py (import)
    ├── Depends on: test_code/ (input data)
    └── Depends on: sentence_transformers (pip)

run_phase1.sh
    ├── Depends on: dataset_generator.py
    └── Depends on: test_embeddings.py
```

---

## Size Estimates

| Item | Size | Note |
|------|------|------|
| Python scripts | ~5MB | Negligible |
| Documentation | ~200KB | Negligible |
| venv/ | ~1GB | Gitignored |
| temp_repos/ | ~2-3GB | Gitignored, can delete after |
| test_code/ | ~50MB | Can regenerate |
| Models (downloaded) | ~1.2GB | Cached in ~/.cache/ |
| Results | ~5MB | Per test run |

**Total committed:** <10MB  
**Total disk usage:** ~5GB during execution

---

## Next Steps After Phase 1

### If GO Decision:
```
codebase-concept-mapper/
├── phase1/              # ✅ Complete
├── phase2/              # ← Create next
│   ├── test_chunking.py
│   ├── chunking_strategies.py
│   └── ...
└── docs/
    └── DECISIONS.md     # ← Document Phase 1 winner
```

### If NO-GO Decision:
```
codebase-concept-mapper/
├── phase1/              # ✅ Complete (research output)
├── docs/
│   └── PIVOT_PLAN.md   # ← Document alternative approaches
└── alternative_project/ # ← Start different approach
```

---

## Quick Reference

**Start here:** `QUICKSTART.md`  
**Need details:** `README_PHASE1.md`  
**Understanding models:** `MODEL_RECOMMENDATIONS.md`  
**Full project context:** `docs/CONTEXT.md`  
**All phases:** `docs/PHASED_PLAN.md`

**Run everything:** `bash run_phase1.sh`  
**Make decision:** `cat results/comparison.md`

---

Ready to build? All files have been provided. Execute in order:
1. Create `phase1/` directory
2. Copy all artifacts into it
3. Run `setup_phase1.sh`
4. Follow `QUICKSTART.md`
