# Phase 1 Implementation Context: Embedding Viability Test

## Session Goal
Build an **automated test pipeline** to evaluate whether embedding models can semantically map natural language concepts to code implementations. This is the **CRITICAL GO/NO-GO** decision point for the entire project.

---

## Core Problem Statement

**Question to Answer:** Can ANY embedding model reliably find code files that implement a given concept, when queried with natural language?

**Example:**
- Query: `"promises in javascript"`
- Expected Behavior: Retrieve files containing `new Promise()`, `async/await`, `.then()` chains
- Success: Model finds these files even if named generically (`api.js`, `utils.js`) rather than obviously (`promises.js`)

---

## Critical Design Decisions (From Previous Discussion)

### ❌ What NOT to Do: Hard-Coded Filenames

```python
# WRONG - Circular logic:
TEST_CASES = {
    "promises": ["promise.js", "async-handler.js"]  
    # We're testing if model can find promise.js
    # But we already told it the answer is promise.js!
}
```

**Problem:** This tests filename matching, not semantic understanding. Real usage won't have obvious filenames.

### ✅ What TO Do: Content-Based Validation

```python
# CORRECT - Validate retrieved content contains concept:
VALIDATORS = {
    "promises javascript": {
        "must_contain_any": ["new Promise(", ".then(", "async ", "await "],
        "must_not_contain": ["def ", "import python"],  # Wrong language
        "min_occurrences": 2  # Not just a comment mentioning it
    }
}
```

**Key Insight:** Don't tell the model which files are correct. Let it retrieve files, then programmatically validate if retrieved content actually implements the concept.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: EMBEDDING VIABILITY TEST                          │
└─────────────────────────────────────────────────────────────┘

[1] Generate Diverse Test Codebase
    ↓
    - Clone 4-6 real open-source repos (Flask, Express, React, etc.)
    - Extract 10-15 random files per repo (NOT cherry-picked!)
    - Create a realistic "haystack" of 50-100 code files
    - Languages: Python (.py) and JavaScript (.js, .jsx)
    
[2] Define Concept Validators (20 concepts minimum)
    ↓
    - 10 Python concepts (async, context managers, decorators, etc.)
    - 10 JavaScript concepts (promises, hooks, closures, etc.)
    - Each validator: keywords to detect, anti-patterns, min occurrences
    - NO filename expectations
    
[3] Test Each Model
    ↓
    For each candidate model:
      a. Embed all 50-100 code files
      b. For each of 20 concepts:
         - Embed the natural language query
         - Retrieve top 5 files by cosine similarity
         - Validate: How many of top 5 actually implement the concept?
      c. Calculate Precision@1 and Precision@5
      d. Log results to JSON
    
[4] Compare Models & Make Go/No-Go Decision
    ↓
    - Generate comparison table (accuracy, speed, requirements)
    - Decision criteria:
      * ✅ GO if best model ≥70% P@5
      * ⚠️ CONDITIONAL if 50-70% P@5 (try query hints)
      * ❌ NO-GO if <50% P@5
```

---

## Success Metrics

### Primary Metric: Precision@5
**Definition:** Of the top 5 retrieved files, how many actually implement the queried concept?

**Why P@5 not P@1?**
- Accounts for multiple valid implementations
- Realistic: users will review top results, not just #1
- More forgiving than strict top-1 accuracy

**Calculation:**
```python
valid_in_top5 = sum(validate_content(file, concept) for file in top_5_results)
precision_at_5 = valid_in_top5 / 5  # 0.0 to 1.0
```

### Secondary Metrics
- **Precision@1:** Is the #1 result correct? (Strict test)
- **Mean Reciprocal Rank (MRR):** Average position of first correct result
- **Coverage:** % of concepts where at least 1 valid result appears in top 5

---

## Test Dataset Specifications

### Repos to Clone (Diverse, Well-Known)
```python
TEST_REPOS = {
    "python": [
        "pallets/flask",       # Web framework (routes, context, decorators)
        "psf/requests",        # HTTP library (async, exceptions, sessions)
        "aio-libs/aiohttp",    # Async patterns
        "django/django"        # ORM, middleware, views (sample 10 files only)
    ],
    "javascript": [
        "axios/axios",         # Promises, error handling
        "expressjs/express",   # Middleware, routing
        "facebook/react",      # Hooks, components, lifecycle
        "vercel/next.js"       # Server-side, routing (sample 10 files only)
    ]
}
```

### Sampling Strategy
- **Random sampling per repo:** 10-15 files from `src/`, `lib/`, or root
- **No cherry-picking:** Don't pre-select files for specific concepts
- **File size filter:** 50-500 lines (avoid huge files, skip trivial ones)
- **Exclude:** Tests, configs, build files (only production code)

### Resulting Test Set
- **Total files:** 50-100 code files
- **Distribution:** ~50% Python, ~50% JavaScript
- **Concepts covered:** 20 (10 per language)
- **Unknown mapping:** We don't know which files contain which concepts until validation

---

## Concept Validators: 20 Examples

### Python Concepts (10)

```python
PYTHON_VALIDATORS = {
    "context managers python": {
        "must_contain_any": ["__enter__", "__exit__", "with ", "@contextmanager"],
        "must_not_contain": ["function(", "const ", "=>"],
        "min_occurrences": 1
    },
    "async await python": {
        "must_contain_any": ["async def", "await ", "asyncio"],
        "must_not_contain": ["Promise", "async function"],
        "min_occurrences": 2
    },
    "decorators python": {
        "must_contain_any": ["@", "def decorator", "functools.wraps"],
        "must_not_contain": ["@interface", "@component"],
        "min_occurrences": 2
    },
    "list comprehensions": {
        "must_contain_any": ["[", "for ", " in ", "]"],
        "must_not_contain": [".map(", ".filter("],
        "min_occurrences": 1,
        "regex_pattern": r"\[.+for .+ in .+\]"  # Actual comprehension syntax
    },
    "exception handling python": {
        "must_contain_any": ["try:", "except ", "finally:", "raise "],
        "must_not_contain": ["catch", "throw new"],
        "min_occurrences": 2
    },
    "generators python": {
        "must_contain_any": ["yield ", "def ", "next("],
        "must_not_contain": ["function*", "yield*"],
        "min_occurrences": 1
    },
    "class inheritance python": {
        "must_contain_any": ["class ", "(", "):", "super("],
        "must_not_contain": ["extends ", "class {"],
        "min_occurrences": 1
    },
    "file handling python": {
        "must_contain_any": ["open(", "with open", ".read(", ".write("],
        "must_not_contain": ["fs.readFile", "require('fs')"],
        "min_occurrences": 1
    },
    "lambda functions python": {
        "must_contain_any": ["lambda ", "map(", "filter("],
        "must_not_contain": ["=>", "function("],
        "min_occurrences": 1
    },
    "dataclasses python": {
        "must_contain_any": ["@dataclass", "from dataclasses", "__post_init__"],
        "must_not_contain": ["interface ", "type "],
        "min_occurrences": 1
    }
}
```

### JavaScript Concepts (10)

```python
JAVASCRIPT_VALIDATORS = {
    "promises javascript": {
        "must_contain_any": ["new Promise(", ".then(", ".catch(", "Promise.all"],
        "must_not_contain": ["async def", "await asyncio"],
        "min_occurrences": 2
    },
    "async await javascript": {
        "must_contain_any": ["async function", "async (", "await "],
        "must_not_contain": ["async def", "asyncio"],
        "min_occurrences": 2
    },
    "react hooks": {
        "must_contain_any": ["useState", "useEffect", "useContext", "useReducer"],
        "must_not_contain": ["@hook", "def use"],
        "min_occurrences": 1
    },
    "closures javascript": {
        "must_contain_any": ["function", "return function", "() =>"],
        "must_not_contain": ["def ", "lambda"],
        "min_occurrences": 1,
        "context_required": True  # Needs nested function structure
    },
    "arrow functions": {
        "must_contain_any": ["=>", "const ", "let "],
        "must_not_contain": ["lambda", "def "],
        "min_occurrences": 2
    },
    "destructuring javascript": {
        "must_contain_any": ["const {", "let {", "const [", "..."],
        "must_not_contain": ["def ", "import "],
        "min_occurrences": 1
    },
    "event handling javascript": {
        "must_contain_any": ["addEventListener", "onClick", "onSubmit", ".on("],
        "must_not_contain": ["def on_", "@event"],
        "min_occurrences": 1
    },
    "callbacks javascript": {
        "must_contain_any": ["function(", "callback", "(err, ", "=>"],
        "must_not_contain": ["def callback", "lambda"],
        "min_occurrences": 1
    },
    "array methods javascript": {
        "must_contain_any": [".map(", ".filter(", ".reduce(", ".forEach("],
        "must_not_contain": ["[x for x in", "list(map"],
        "min_occurrences": 2
    },
    "classes javascript": {
        "must_contain_any": ["class ", "constructor(", "extends ", "super("],
        "must_not_contain": ["class :", "def __init__"],
        "min_occurrences": 1
    }
}
```

---

## Model Testing Protocol

### Candidate Models to Test (3 minimum)

**Selection Criteria:**
- Must run locally on CPU (no GPU required for testing)
- Size <1GB (fast download/load)
- Designed for code or general semantic search
- Active maintenance (updated in last 6 months)

**Research Query for Future Me:**
```
Find the top 3 open-source embedding models (as of early 2025) for code semantic search:
1. Optimized for natural language → code mapping
2. CPU-compatible (no GPU required)
3. Installation: pip or huggingface
4. Benchmarks showing >60% retrieval accuracy on code tasks
5. Size <1GB

Return: model name, size, installation command, benchmark results, usage example
```

**Expected candidates (validate these are still current):**
- `nomic-ai/nomic-embed-text-v1.5` (general, 137M params)
- `BAAI/bge-small-en-v1.5` (general semantic, 33M params)
- `sentence-transformers/all-MiniLM-L6-v2` (baseline, 22M params)

### Testing Script Structure

```python
# test_model.py

def test_single_model(model_name, test_files, validators):
    """
    Test one embedding model against all concepts
    
    Returns:
        {
            "model": str,
            "overall_p5": float,
            "overall_p1": float,
            "per_concept": [{"concept": str, "p5": float, "p1": float}, ...],
            "inference_time_sec": float
        }
    """
    
    # 1. Load model
    model = SentenceTransformer(model_name)
    
    # 2. Embed all test files (batch for speed)
    file_embeddings = {}
    for filepath, content in test_files.items():
        file_embeddings[filepath] = model.encode(content)
    
    # 3. Test each concept
    results = []
    for concept, validator in validators.items():
        query_embedding = model.encode(concept)
        
        # Rank all files by similarity
        similarities = {
            filepath: cosine_similarity(query_embedding, file_emb)
            for filepath, file_emb in file_embeddings.items()
        }
        
        top_5 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Validate each of top 5
        valid_results = []
        for filepath, score in top_5:
            is_valid = validate_file_content(
                test_files[filepath], 
                validator
            )
            valid_results.append(is_valid)
        
        p5 = sum(valid_results) / 5
        p1 = valid_results[0] if valid_results else 0
        
        results.append({
            "concept": concept,
            "p5": p5,
            "p1": p1,
            "top_files": [f for f, _ in top_5],
            "valid_flags": valid_results
        })
    
    # 4. Aggregate metrics
    overall_p5 = sum(r["p5"] for r in results) / len(results)
    overall_p1 = sum(r["p1"] for r in results) / len(results)
    
    return {
        "model": model_name,
        "overall_p5": overall_p5,
        "overall_p1": overall_p1,
        "per_concept": results
    }


def validate_file_content(content, validator):
    """
    Check if file content actually implements the concept
    
    Returns: bool (True if valid)
    """
    # Check must_contain_any
    matches = sum(
        1 for keyword in validator["must_contain_any"]
        if keyword.lower() in content.lower()
    )
    
    if matches < validator["min_occurrences"]:
        return False
    
    # Check must_not_contain (language detection)
    if any(anti in content for anti in validator.get("must_not_contain", [])):
        return False
    
    # Optional: regex pattern validation
    if "regex_pattern" in validator:
        import re
        if not re.search(validator["regex_pattern"], content):
            return False
    
    return True
```

---

## Decision Criteria

### ✅ GO to Phase 2 (Integration)
- **Best model achieves ≥70% Precision@5**
- **At least 60% Precision@1** (top result correct more than half the time)
- **Inference time <10 seconds for 20 queries**

**Action:** Document winning model, proceed to chunking tests

### ⚠️ CONDITIONAL GO
- **Best model achieves 50-70% Precision@5**
- **Try enhancement:** Add file extension hints (e.g., "promises in .js files")
- **Re-test:** If improves to ≥70% P@5 → GO
- **If still <70%:** Consider per-language models or reduce scope to Python-only

### ❌ NO-GO (Stop Project)
- **All models <50% Precision@5**
- **GPU required for acceptable accuracy**
- **Inference time >30 seconds per query**

**Pivot Options:**
1. Wait 6 months for better models
2. Switch to keyword-based search + LLM reranking
3. Different project: Extend video RAG (both inputs are natural language)

---

## Output Artifacts

### 1. Test Dataset (Committed to Repo)
```
test_code/
├── python/
│   ├── flask_app.py
│   ├── requests_session.py
│   └── ... (25 files)
├── javascript/
│   ├── axios_client.js
│   ├── react_component.jsx
│   └── ... (25 files)
└── metadata.json  # Which repos, which commits
```

### 2. Test Results (JSON)
```json
{
  "test_date": "2025-01-XX",
  "models_tested": [
    {
      "name": "nomic-embed-text-v1.5",
      "overall_p5": 0.73,
      "overall_p1": 0.61,
      "inference_time_sec": 8.2,
      "per_concept": [...]
    },
    ...
  ],
  "decision": "GO - nomic-embed achieves 73% P@5",
  "next_phase": "Phase 2: Chunking Tests"
}
```

### 3. Comparison Table (Markdown)
```markdown
| Model | P@5 | P@1 | Time (s) | CPU Only | Size |
|-------|-----|-----|----------|----------|------|
| nomic-embed-text-v1.5 | 73% | 61% | 8.2 | ✓ | 137M |
| bge-small-en-v1.5 | 68% | 54% | 6.1 | ✓ | 33M |
| all-MiniLM-L6-v2 | 52% | 38% | 4.3 | ✓ | 22M |

**Decision:** ✅ GO with nomic-embed-text-v1.5
```

---

## Implementation Checklist

When building the Phase 1 pipeline, ensure:

- [ ] **No hard-coded filenames** - Validation is content-based only
- [ ] **Diverse test set** - Random sampling from real repos, not cherry-picked
- [ ] **20+ concepts** - 10 Python, 10 JavaScript minimum
- [ ] **Batch embeddings** - Don't re-embed files for each query (cache them)
- [ ] **Clear validation logic** - Each validator has objective criteria
- [ ] **Language detection** - `must_not_contain` prevents cross-language false positives
- [ ] **Regex patterns** (optional) - For complex syntax like list comprehensions
- [ ] **Logging** - Save all results to JSON for later analysis
- [ ] **Time tracking** - Measure inference speed (critical for local use)
- [ ] **Reproducibility** - Pin model versions, repo commits, random seeds

---

## Key Insights to Remember

1. **Content validation, not filename matching** - The model must find semantically similar code, not match obvious names
2. **Realistic test set** - Random files from real repos, not curated examples
3. **Precision@5 over Precision@1** - Users will review top results, not just #1
4. **Language disambiguation is critical** - `must_not_contain` prevents "async" matching both Python and JS
5. **This is a GO/NO-GO gate** - Don't proceed if embeddings fundamentally don't work
6. **Speed matters** - If queries take 30+ seconds, the tool is unusable
7. **Document everything** - Future phases depend on understanding why this model won

---

## Timeline Estimate

- **Setup test dataset:** 1-2 hours (one-time, cached)
- **Write validators:** 1 hour (20 concepts)
- **Write test script:** 2 hours
- **Test 3 models:** 1-2 hours (mostly waiting)
- **Analysis & decision:** 1 hour

**Total: 6-8 hours (Day 1 of project)**

---

## Future Me: Start Here

When you begin Phase 1 implementation:

1. **First:** Clone the 8 repos and sample files (script this)
2. **Second:** Define all 20 validators (copy from above, adjust as needed)
3. **Third:** Write `test_model.py` with batch embedding
4. **Fourth:** Test 3 models, generate comparison table
5. **Fifth:** Make GO/NO-GO decision based on ≥70% P@5 threshold

**Do NOT:**
- Manually collect files
- Hard-code expected filenames
- Skip the validation step
- Test only 1-2 models
- Proceed to Phase 2 if <70% P@5

**Remember:** This phase gates the entire project. If embeddings don't work semantically, no amount of engineering in later phases will fix it.
