# 🎯 PHASED RESEARCH PLAN: Code Concept Mapper MVP

## 🔍 Strategic Approach (Pattern Recognition)

- **Phase-gated progression** (don't move until critical unknowns solved)
- **Risk minimization** (fail fast on blockers, not after weeks of work)
- **Conservative estimates** (7-day max, incremental testing)
- **Leverage existing tools** (don't rebuild what works - LlamaIndex/LanceDB proven)

---

## 📊 PROJECT RISK ANALYSIS

### Critical Path Dependencies (Must Solve First)

```
Phase 1: Embedding Viability
    ↓ (If fails → STOP)
Phase 2: Code Chunking Quality
    ↓ (If fails → STOP or pivot to simpler approach)
Phase 3: Multi-Language Feasibility
    ↓ (If limited → Scope down to 1-2 languages)
Phase 4: Integration & Polish
```

### Why This Order?

1. **Embedding quality IS the project** - if NL→Code mapping doesn't work, nothing else matters
2. **Chunking affects retrieval** - bad chunks = bad results even with good embeddings
3. **Multi-language is additive** - can start with 1 language, expand later
4. **Integration assumes Phases 1-3 work** - don't optimize a broken system

---

# 🚀 PHASE 1: EMBEDDING VIABILITY TEST (Days 1-2, CRITICAL)

## Goal

**Answer the question: "Can ANY embedding model reliably map natural language concepts to code implementations?"**

## Success Criteria (Go/No-Go Decision)

- ✅ **GO**: Model achieves >70% accuracy on 20 test queries (e.g., "Promises in JavaScript" → finds async/await files)
- ❌ **NO-GO**: Model <50% accuracy or requires GPU → STOP or pivot to simpler approach

## Tasks

### 1.1: Research & Select 3 Candidate Models (3 hours)

**Gemini Deep Research Query:**

```
Find the top 3 open-source embedding models (as of 2025) specifically designed for
code semantic search that:
1. Can run locally on CPU (no GPU required)
2. Have proven benchmarks for natural language → code retrieval
3. Support Python installation via pip/huggingface
4. Have examples of mapping concepts (e.g., "async programming") to code files

Prioritize models with:
- Public benchmarks showing >70% retrieval accuracy
- Active maintenance (updated in last 6 months)
- Documentation for local inference
- Size < 1GB for quick testing

Return for each model: name, size, installation command, benchmark results,
and link to usage example.
```

**Deliverable:** Shortlist of 3 models with installation commands

---

### 1.2: Setup Quick Test Environment (1 hour)

```bash
# Create isolated test directory
mkdir code-embedding-test && cd code-embedding-test
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install test dependencies
pip install sentence-transformers numpy
```

**Create test dataset:**

```python
# test_queries.py
TEST_QUERIES = [
    # JavaScript
    ("promises in javascript", ["async.js", "fetch-api.js"]),
    ("react hooks lifecycle", ["useEffect.jsx", "useState.jsx"]),

    # Python
    ("context managers python", ["contextlib.py", "with_statement.py"]),
    ("async await python", ["asyncio_example.py", "aiohttp_client.py"]),

    # Cross-language
    ("error handling", ["try_except.py", "error-boundary.jsx"]),
]
```

**Collect 20 small code files** (5-10 from your existing projects):

- Place in `test_code/python/` and `test_code/javascript/`
- 10 files per language, ~50-200 lines each
- Ensure they cover the test query concepts

---

### 1.3: Test Each Model (2 hours per model = 6 hours)

```python
# test_embedding.py
from sentence_transformers import SentenceTransformer
import numpy as np
import os

def test_model(model_name):
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print('='*60)

    # Load model
    model = SentenceTransformer(model_name)

    # Embed all code files
    code_embeddings = {}
    for root, dirs, files in os.walk('test_code'):
        for file in files:
            if file.endswith(('.py', '.js', '.jsx')):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    code = f.read()
                code_embeddings[file] = model.encode(code)

    # Test queries
    results = []
    for query, expected_files in TEST_QUERIES:
        query_embed = model.encode(query)

        # Calculate similarity
        similarities = {}
        for filename, code_embed in code_embeddings.items():
            sim = np.dot(query_embed, code_embed) / (
                np.linalg.norm(query_embed) * np.linalg.norm(code_embed)
            )
            similarities[filename] = sim

        # Get top 3 results
        top_results = sorted(similarities.items(),
                           key=lambda x: x[1],
                           reverse=True)[:3]

        # Check if expected files in top 3
        hit = any(f in [r[0] for r in top_results] for f in expected_files)
        results.append({
            'query': query,
            'expected': expected_files,
            'got': top_results,
            'hit': hit
        })

        print(f"\nQuery: '{query}'")
        print(f"Expected: {expected_files}")
        print(f"Top 3: {[f'{r[0]} ({r[1]:.3f})' for r in top_results]}")
        print(f"✓ HIT" if hit else "✗ MISS")

    accuracy = sum(r['hit'] for r in results) / len(results) * 100
    print(f"\n{'='*60}")
    print(f"ACCURACY: {accuracy:.1f}%")
    print('='*60)

    return accuracy, results

# Test all 3 models
models_to_test = [
    "model-name-1",  # From GDR results
    "model-name-2",
    "model-name-3"
]

for model_name in models_to_test:
    accuracy, results = test_model(model_name)
    # Log results to JSON for comparison
```

---

### 1.4: Phase 1 Decision Point (30 min)

**IF best model >= 70% accuracy:**

- ✅ **PROCEED TO PHASE 2**
- Document winning model in `DECISIONS.md`
- Note: Context hints (file extensions) can boost accuracy in Phase 3

**IF best model 50-70% accuracy:**

- ⚠️ **CONDITIONAL PROCEED**
- Test with file extension hints (e.g., "promises in .js files")
- If improves to >70% → PROCEED
- If still <70% → Re-scope to supervised approach (manual tagging)

**IF best model <50% accuracy:**

- ❌ **STOP - Project Not Viable**
- Pivot options:
  1. Wait for better models (revisit in 6 months)
  2. Simpler approach: Keyword-based search with LLM reranking
  3. Different project: Extend Python RAG to video + code repos (both natural language)

---

## Phase 1 Deliverables

- [ ] 3 models tested with quantitative results
- [ ] Winning model documented (name, accuracy, install command)
- [ ] Test dataset of 20 code files
- [ ] Go/No-Go decision logged

## Phase 1 Risks & Mitigations

| Risk                   | Mitigation                                           |
| ---------------------- | ---------------------------------------------------- |
| All models fail        | Pre-selected models based on benchmarks, not random  |
| GPU required           | Explicitly filtered for CPU-only models in GDR query |
| Test dataset too small | 20 queries covers core use cases; Phase 2 expands    |

---

# 🔧 PHASE 2: CODE CHUNKING QUALITY (Day 3, CONDITIONAL)

**Entry Condition:** Phase 1 model achieved ≥70% accuracy

## Goal

**Validate that smart code chunking preserves semantic meaning for embeddings**

## Success Criteria

- ✅ Chunked code maintains >70% retrieval accuracy (no worse than Phase 1)
- ✅ Chunks are readable (not mid-function)
- ✅ Chunking runs in <5 min for 100 files

## Tasks

### 2.1: Research Chunking Libraries (2 hours)

**Gemini Deep Research Query:**

```
Find Python libraries for intelligent code chunking optimized for RAG systems that:
1. Split by semantic units (functions, classes, methods) using AST or tree-sitter
2. Preserve docstrings and comments with code
3. Support Python and JavaScript/TypeScript
4. Easy pip installation and usage examples

Return: library name, installation command, code example showing how to chunk
a Python file into function-level blocks with context preservation.
```

**Expected Results:** Libraries like `tree-sitter`, `ast` module, or RAG-specific tools

---

### 2.2: Test Chunking vs Whole Files (3 hours)

```python
# test_chunking.py
from your_chunking_library import chunk_code
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('winning_model_from_phase1')

# Test: Do chunks maintain semantic match?
test_file = "test_code/python/asyncio_example.py"

# Approach 1: Whole file embedding (Phase 1 baseline)
with open(test_file) as f:
    whole_code = f.read()
whole_embed = model.encode(whole_code)

# Approach 2: Chunked embeddings
chunks = chunk_code(test_file)  # Returns list of (chunk_text, metadata)
chunk_embeds = [model.encode(chunk[0]) for chunk in chunks]

# Test query: "async await in python"
query_embed = model.encode("async await in python")

# Compare similarities
whole_sim = cosine_similarity(query_embed, whole_embed)
chunk_sims = [cosine_similarity(query_embed, c) for c in chunk_embeds]
best_chunk_sim = max(chunk_sims)

print(f"Whole file similarity: {whole_sim:.3f}")
print(f"Best chunk similarity: {best_chunk_sim:.3f}")
print(f"Difference: {best_chunk_sim - whole_sim:+.3f}")

# Goal: best_chunk_sim >= whole_sim (chunking doesn't hurt retrieval)
```

**Run on 10 test files, log results**

---

### 2.3: Phase 2 Decision Point (30 min)

**IF chunking maintains accuracy AND improves readability:**

- ✅ **PROCEED TO PHASE 3**
- Document chunking strategy (e.g., "function-level with 2-line context")

**IF chunking hurts accuracy by >10%:**

- ⚠️ **USE WHOLE FILES**
- Note: Might limit to smaller files (< 500 lines)
- Still proceed to Phase 3

**IF chunking is too slow (>10 min for 100 files):**

- ⚠️ **OPTIMIZE OR SKIP**
- Chunking can be added later; Phase 3 more critical

---

## Phase 2 Deliverables

- [ ] Chunking library selected and installed
- [ ] Comparison test: chunks vs whole files
- [ ] Decision logged (use chunking or whole files)

---

# 🌍 PHASE 3: MULTI-LANGUAGE FEASIBILITY (Day 4, CONDITIONAL)

**Entry Condition:** Phase 1 passed, Phase 2 decision made

## Goal

**Test if single model handles multiple languages OR if per-language models needed**

## Success Criteria

- ✅ Model achieves >70% accuracy on cross-language queries
- ✅ File extension hints work (e.g., "promises in .js files")
- ✅ Decision: Single model vs per-language models

## Tasks

### 3.1: Test Cross-Language Queries (2 hours)

```python
# test_multilang.py
CROSS_LANG_QUERIES = [
    ("async programming", ["asyncio.py", "async-await.js"]),
    ("error handling patterns", ["try_except.py", "error-boundary.jsx"]),
    ("data fetching", ["requests_api.py", "fetch-api.js"]),
]

# Test 1: No hints
results_no_hints = test_model_with_queries(CROSS_LANG_QUERIES)

# Test 2: With file extension context
def query_with_extension(query, target_ext):
    return f"{query} in {target_ext} files"

results_with_hints = test_model_with_queries([
    (query_with_extension(q, ".py"), [f for f in files if f.endswith('.py')])
    for q, files in CROSS_LANG_QUERIES
])

print(f"Accuracy without hints: {results_no_hints['accuracy']:.1f}%")
print(f"Accuracy with hints: {results_with_hints['accuracy']:.1f}%")
```

---

### 3.2: Test Per-Language Models (Optional, 2 hours)

**IF Phase 3.1 accuracy < 70%:**

**Gemini Deep Research Query:**

```
Find language-specific code embedding models:
1. Python-only code embeddings (e.g., CodeBERT variants trained on Python)
2. JavaScript/TypeScript-only embeddings

Compare accuracy for language-specific vs multilingual models on the same queries.
Return: model names, benchmark differences, installation commands.
```

Test both approaches, document trade-offs (accuracy vs complexity)

---

### 3.3: Phase 3 Decision Point (30 min)

**IF single model ≥70% cross-language accuracy:**

- ✅ **PROCEED TO PHASE 4 (Full integration)**
- Use single model for simplicity

**IF single model <70% BUT per-language models ≥70%:**

- ⚠️ **PROCEED WITH LIMITATIONS**
- Scope: Start with Python-only MVP
- Expand to JS/TS in future iteration

**IF no approach ≥70% for multiple languages:**

- ⚠️ **REDUCE SCOPE**
- Deliver Python-only RAG system
- Multi-language as future enhancement

---

## Phase 3 Deliverables

- [ ] Cross-language accuracy tested
- [ ] File extension hint effectiveness measured
- [ ] Decision: Single model vs per-language vs Python-only

---

# 🎨 PHASE 4: INTEGRATION & POC (Days 5-7, CONDITIONAL)

**Entry Condition:** Phases 1-3 passed with acceptable accuracy

## Goal

**Integrate winning model + chunking strategy into minimal working POC**

## Success Criteria

- ✅ Can query "Promises" → returns top 5 relevant files
- ✅ Query time <5 seconds
- ✅ Works on user's local codebase (not just test data)

## Tasks

### 4.1: Adapt Python Course RAG Pipeline (4 hours)

**Reuse your proven architecture:**

```python
# src/build_index.py (adapt from previous project)
# CHANGES:
# - Input: Code files from open-source repos (not SRT files)
# - Parser: Use chunking library from Phase 2 (not SRT parser)
# - Embeddings: Use winning model from Phase 1
# - Storage: Same LanceDB setup

# src/query_engine.py (minimal changes)
# - Same query logic
# - Add file extension filtering if needed (from Phase 3 results)
```

**Test indexing time:**

```bash
# Index a small repo (e.g., Flask - 50 files)
python -m src.build_index --repo flask-source/
# Target: <5 minutes for 50 files
```

---

### 4.2: Test on Real Queries (3 hours)

```python
# Test with course outline concepts
REAL_QUERIES = [
    "React hooks useEffect",
    "Express middleware error handling",
    "Python async context managers",
    "Django ORM relationships",
    "JavaScript promises chaining"
]

for query in REAL_QUERIES:
    results = query_engine.search(query, top_k=5)
    print(f"\nQuery: {query}")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['file']} (score: {result['score']:.3f})")
        print(f"   Preview: {result['code'][:100]}...")
```

**Manual validation:**

- Are top 3 results relevant?
- Are code previews readable?
- Does it feel useful for learning?

---

### 4.3: Handle GPU Decision (IF NEEDED, 4 hours)

**ONLY IF Phase 1 winner requires GPU:**

**Gemini Deep Research Query:**

```
How to run large embedding models on Google Colab Pro ($10/month) and export
the resulting vector database (LanceDB format) to local machine?

Include:
1. Colab notebook template for batch embedding generation
2. How to save LanceDB files to (Google Drive / GCP Bucket)
3. How to download and import into local LlamaIndex setup
4. Estimated time for 100 files

Prioritize simplicity - single notebook workflow preferred.
```

**Test Colab workflow:**

- Upload 20 test files
- Generate embeddings
- Save to Google Drive / GCP Bucket (if huge size)
- Download locally
- Query works?

---

### 4.4: Create Simple CLI/UI (4 hours)

**Reuse your Streamlit app from Python RAG:**

```python
# app.py (adapt from previous project)
import streamlit as st

st.title("Code Concept Search")

stack = st.selectbox("Stack", ["Python", "JavaScript", "React"])
concept = st.text_input("Concept (e.g., 'async programming')")

if st.button("Search"):
    results = query_engine.search(f"{concept} in {stack}")
    for result in results:
        st.code(result['code'], language=result['language'])
        st.caption(f"File: {result['file']} | Score: {result['score']:.2f}")
```

---

### 4.5: Final POC Test (2 hours)

**End-to-End Workflow:**

1. Start with course outline: "JavaScript - Promises"
2. Run query → Get top 5 files
3. Review code snippets
4. Rate relevance: How many of top 5 are actually about Promises?

**Success:** ≥3 out of 5 relevant for 80% of test queries

---

## Phase 4 Deliverables

- [ ] Working POC: Query → Results
- [ ] Tested on ≥20 real queries
- [ ] CLI or Streamlit UI
- [ ] Decision: GPU needed or not?

---

# 📋 PHASE SUMMARY & DECISION TREE

```
START
  ↓
PHASE 1: Test Embeddings
  ├─ ≥70% accuracy → PHASE 2
  ├─ 50-70% accuracy → Add hints, retest
  │   ├─ Now ≥70% → PHASE 2
  │   └─ Still <70% → STOP (pivot to simpler project)
  └─ <50% accuracy → STOP

PHASE 2: Test Chunking
  ├─ Maintains accuracy → Use chunking in PHASE 3
  └─ Hurts accuracy → Use whole files in PHASE 3

PHASE 3: Test Multi-Language
  ├─ Single model ≥70% → PHASE 4 (full stack)
  ├─ Per-language ≥70% → PHASE 4 (per-language models)
  └─ <70% → PHASE 4 (Python-only scope)

PHASE 4: Build POC
  ├─ CPU models work → Local-only setup
  └─ GPU needed → Colab workflow

DONE: Viable POC or informed decision to pivot
```

---

# 🎯 YOUR GEMINI DEEP RESEARCH QUERIES (Prioritized)

## Critical Path (Do First)

1. **Phase 1 Embedding Models** (HIGHEST PRIORITY)
   - Already drafted above in Phase 1.1
2. **Phase 2 Chunking Libraries**

   - Already drafted above in Phase 2.1

3. **Phase 3 Multi-Language Models** (Conditional)
   - Already drafted above in Phase 3.2

## Optional (Only If Needed)

4. **Phase 4 Colab Workflow** (If GPU required)
   - Already drafted above in Phase 4.3

---

# ⏱️ TIME ESTIMATES (Conservative)

| Phase     | Best Case  | Worst Case | Includes                |
| --------- | ---------- | ---------- | ----------------------- |
| Phase 1   | 1 day      | 2 days     | GDR + test 3 models     |
| Phase 2   | 4 hours    | 8 hours    | GDR + chunk testing     |
| Phase 3   | 4 hours    | 8 hours    | Cross-lang + hints      |
| Phase 4   | 2 days     | 3 days     | Integration + POC       |
| **TOTAL** | **4 days** | **7 days** | Matches your constraint |

---

# 🛑 EXPLICIT STOP CONDITIONS

**STOP if:**

- Phase 1 <50% accuracy after hints
- Phase 2 + Phase 3 combined <60% accuracy
- GPU required AND Colab workflow fails
- Any phase takes >2x estimated time

**DON'T:**

- Spend >2 days on any single phase
- Try to "fix" bad embeddings with prompt engineering
- Build chunking from scratch (use libraries)
- Over-optimize before proving viability

---

Does this phased approach match your SpeedTyper methodology? Should I adjust the go/no-go thresholds or reorder any phases?
