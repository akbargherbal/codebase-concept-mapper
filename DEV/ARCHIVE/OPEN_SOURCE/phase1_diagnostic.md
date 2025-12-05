# Phase 1 Diagnostic Context: Code Concept Mapper

## Original Problem Statement

**Goal**: Build a RAG system that maps natural language learning concepts to actual code implementations in open-source repositories.

**Use Case Example**:
- User query: `"Promises in JavaScript"`
- Expected output: Code files containing Promise implementations (async/await, .then() chains, Promise constructors)
- Challenge: Files may be named generically (`api.js`, `utils.js`) rather than obviously (`promises.js`)

**Core Requirement**: Semantic understanding that bridges natural language concepts to programming implementations across multiple languages (Python, JavaScript, etc.).

---

## Phase 1 Objective

**Test the fundamental assumption**: Can embedding models semantically map natural language concepts to code implementations?

**Success Criteria**:
- ✅ GO: Best model achieves ≥70% Precision@5
- ⚠️ CONDITIONAL: 50-70% P@5 (with query hints)
- ❌ NO-GO: <50% P@5

**Metric Definition**:
- **Precision@5 (P@5)**: Of the top 5 retrieved files, how many actually implement the queried concept?
- Validation: Content-based keyword/pattern matching (not filename matching)

---

## What We Did in Colab

### Test Setup

**Models Tested** (4 total):
1. `Qwen/Qwen3-Embedding-0.6B` → **21% P@5**
2. `intfloat/multilingual-e5-large-instruct` → **23% P@5**
3. `google/embeddinggemma-300m` → **7% P@5**
4. `Alibaba-NLP/gte-multilingual-base` → **25% P@5** (best)

**Test Dataset**:
- 84 code files randomly sampled from 8 real open-source repos
- Distribution: 45 Python files, 39 JavaScript files
- Sources: Flask, Django, Requests, aiohttp, axios, Express, React, Next.js
- File size: 50-500 lines (excluding tests, configs, build files)
- Sampling: Random selection from `src/`, `lib/` directories

**Test Queries** (20 concepts):
- 10 Python concepts: context managers, async/await, decorators, list comprehensions, exception handling, generators, class inheritance, file handling, lambda functions, dataclasses
- 10 JavaScript concepts: promises, async/await, React hooks, closures, arrow functions, destructuring, event handling, callbacks, array methods, classes

**Validation Method**:
- Content-based: Each concept has a validator with `must_contain_any` keywords
- Example: "promises javascript" must contain `["new Promise(", ".then(", ".catch(", "Promise.all"]`
- Language detection: `must_not_contain` prevents cross-language false positives

### Results Summary

**Best Model Performance** (`Alibaba-NLP/gte-multilingual-base`):
- Overall P@5: **25%**
- Overall P@1: **30%**
- Mean Reciprocal Rank: **0.458**
- Pass Rate (concepts ≥60% P@5): **20%** (4/20 concepts)

**Successful Concepts** (≥60% P@5):
- class inheritance python (80%)
- async await python (60%)
- exception handling python (60%)
- array methods javascript (60%)

**Failed Concepts** (<60% P@5):
- 16 out of 20 concepts below threshold
- JavaScript concepts particularly weak (only 1/10 passed)

**Decision**: ❌ NO-GO - Threshold not met (need ≥50% for conditional proceed)

---

## Hypotheses About the Failure

We need to investigate which of these explanations is true:

### Hypothesis 1: Open-Source Models Insufficient
**Claim**: Embedding models (open-source or otherwise) simply cannot perform natural language → code mapping reliably yet.

**Evidence For**:
- All 4 models failed dramatically (best: 25% vs 70% threshold)
- Mix of model sizes (137M to 1.1B parameters)
- Mix of architectures (Qwen, E5, Gemma, GTE)

**Evidence Against**:
- Research mentions code-specific models exist (VoyageCode3, Nomic Embed Code, CodeRankEmbed)
- CodeSearchNet benchmark shows models can achieve 70-80% MRR on docstring→code tasks
- We may not have tested the RIGHT models

**Status**: NEEDS INVESTIGATION

---

### Hypothesis 2: Wrong Model Category
**Claim**: We tested general-purpose text embedding models instead of code-specific embedding models.

**Evidence For**:
- All tested models are described as "multilingual text" or "general text" embeddings
- Model training likely focused on natural language (Wikipedia, web text, general corpora)
- No explicit mention of code training in model cards

**Evidence Against**:
- Some models claim multilingual support (which could include programming languages)
- Qwen3-Embedding claims to support "100+ natural and programming languages"

**Status**: HIGHLY LIKELY - Needs verification by checking:
1. Model training data (was code included? how much?)
2. Model benchmarks (any CodeSearchNet scores?)
3. Existence of specialized code models we didn't test

---

### Hypothesis 3: Missing Task Instruction Prefixes
**Claim**: Modern embedding models require task-specific prefixes (e.g., "search_query:", "Represent this code:") that we didn't use.

**Evidence For**:
- Research found that `nomic-embed-text-v1.5` requires prefixes: `"search_query:"` and `"search_document:"`
- Instruction-tuned models (e5-large-instruct) are designed to use task instructions
- Our code used raw queries: `model.encode("promises javascript")` without any prefix

**Evidence Against**:
- Not all models require prefixes (older models work without them)
- Some models tested (embeddinggemma) may not need prefixes

**Status**: CONFIRMED for at least 1-2 models - Needs systematic check:
1. Review model documentation for each tested model
2. Identify required prefixes
3. Retest with correct prefixes

---

### Hypothesis 4: Task Mismatch (Concept vs Docstring)
**Claim**: Our queries are abstract concepts ("promises", "decorators"), but models are trained on docstring→code pairs (concrete function descriptions).

**Evidence For**:
- CodeSearchNet uses function-level retrieval with docstrings
- Example: Query = "calculate factorial", Code = `def factorial(n): ...`
- Our queries are broader: "promises javascript" could match 100+ different implementations

**Evidence Against**:
- Semantic embeddings should capture abstract concepts
- Real users will query with concepts, not specific function descriptions

**Status**: POSSIBLE - Represents task difficulty mismatch:
1. Models may perform better on docstring-style queries
2. Our use case may be inherently harder than CodeSearchNet benchmark
3. May need to adjust expectations (50% P@5 acceptable vs 70%)

---

### Hypothesis 5: Validator Brittleness
**Claim**: Our keyword-based validators produce false negatives (rejecting valid implementations).

**Evidence For**:
- Modern JavaScript uses `async/await` instead of `.then()` chains
- Code may use abstractions (no explicit `new Promise()` visible)
- Implicit patterns (closures, generators) hard to detect with keywords

**Evidence Against**:
- Validators designed to be flexible (`must_contain_any` with multiple options)
- Language detection (`must_not_contain`) successfully prevents cross-language matches

**Status**: MINOR CONTRIBUTOR - Not the primary issue:
- Validators may lower scores by 5-10% (false negatives)
- Doesn't explain 25% vs 70% gap
- Easy to fix after primary issues resolved

---

### Hypothesis 6: Dataset Quality Issues
**Claim**: Random sampling produced low-quality test data (config files, boilerplate, non-obvious implementations).

**Evidence For**:
- Random sampling doesn't guarantee concept representation
- Large repos (Django, Next.js) may have mostly framework code
- Files may use concepts implicitly (no clear keywords)

**Evidence Against**:
- 84 files is reasonable sample size
- Real-world use case will have random files
- Some concepts succeeded (class inheritance: 80%)

**Status**: UNLIKELY PRIMARY CAUSE - May contribute to difficulty:
- Dataset reflects realistic conditions
- Curated dataset might improve scores by 10-15%
- Not sufficient to explain 45-point gap

---

## Investigation Plan: Systematic Diagnosis

### Phase 1: Evidence Collection (Session 1)

**DO NOT CODE YET.** First establish ground truth.

#### Step 1.1: Review Actual Test Code
**Objective**: Understand exactly what was executed in Colab.

**Files to examine**:
- `phase1/test_embeddings.py` - Main test script
- `phase1/concept_validators.py` - Validation logic
- `phase1/dataset_generator.py` - How files were sampled

**Questions to answer**:
1. Were task prefixes used in the code? (Check `model.encode()` calls)
2. How exactly were similarities calculated?
3. Were there any errors/warnings in execution logs?
4. Are validators correctly implemented? (Check regex, keyword matching)

---

#### Step 1.2: Verify Model Specifications
**Objective**: Confirm what models were actually designed for.

**For each tested model, determine**:
1. **Training data**: Was code included? What percentage?
2. **Training task**: Text similarity? Code search? General embedding?
3. **Required prefixes**: Does documentation specify task instructions?
4. **Benchmarks**: Any scores on CodeSearchNet, code retrieval tasks?

**Sources to check**:
- Model cards on HuggingFace
- Official documentation / papers
- Community discussions / GitHub issues

**Expected outcome**: Classification of each model:
- ✅ Code-specific (trained on code pairs, benchmarked on code tasks)
- ⚠️ Multilingual (includes code but not specialized)
- ❌ Text-only (no code training)

---

#### Step 1.3: Research Code-Specific Models
**Objective**: Identify models actually designed for code→concept mapping.

**Search for**:
1. Models explicitly trained on CodeSearchNet
2. Models benchmarked on code retrieval tasks
3. Open-source alternatives to proprietary models (VoyageCode3)

**Candidate models to investigate**:
- `nomic-ai/nomic-embed-code` (7B parameters, claimed SOTA)
- `nomic-ai/CodeRankEmbed` (137M parameters, code-specific)
- `Salesforce/codesage-large` (1.3B parameters)
- `jinaai/jina-code-v2` (code similarity focused)

**For each candidate**:
- Required task prefixes?
- CPU vs GPU requirements?
- Expected performance on code tasks?
- Installation complexity?

---

#### Step 1.4: Establish Performance Baseline
**Objective**: What accuracy is realistic for this task?

**Research questions**:
1. What do SOTA models achieve on CodeSearchNet? (Look for MRR scores)
2. How does "concept query" compare to "docstring query" in difficulty?
3. What's the gap between P@5 and MRR metrics?

**Expected finding**: Benchmark numbers like:
- SOTA on CodeSearchNet: 70-80% MRR
- Translation to P@5: approximately equivalent
- Our task difficulty: potentially 10-20% harder (concept vs docstring)

**Conclusion**: Realistic target might be 50-70% P@5 (not 70% minimum)

---

### Phase 2: Root Cause Confirmation (Session 1-2)

**DO NOT CODE YET.** Confirm diagnosis before implementing fixes.

#### Step 2.1: Diagnosis Decision Tree

```
START: 25% P@5 observed

Q1: Were tested models code-specific?
├─ NO → Primary cause = Wrong model category (Hypothesis 2)
│         Action: Test code-specific models
└─ YES → Continue to Q2

Q2: Were task prefixes used correctly?
├─ NO → Primary cause = Missing prefixes (Hypothesis 3)
│         Action: Add prefixes, retest
└─ YES → Continue to Q3

Q3: Is task fundamentally too hard? (Check benchmarks)
├─ YES → Primary cause = Task difficulty (Hypothesis 4)
│         Action: Adjust expectations or pivot approach
└─ NO → Continue to Q4

Q4: Are validators producing false negatives?
├─ YES → Contributing cause = Validator brittleness (Hypothesis 5)
│         Action: Refine validators
└─ NO → Continue to Q5

Q5: Is dataset quality poor?
└─ MAYBE → Minor contributor (Hypothesis 6)
          Action: Curate better dataset (optional)
```

#### Step 2.2: Evidence-Based Ranking

After investigation, rank hypotheses by likelihood:

**Example ranking** (to be updated after investigation):
1. Hypothesis 2 (Wrong model category) - 70% likely
2. Hypothesis 3 (Missing prefixes) - 60% likely
3. Hypothesis 4 (Task mismatch) - 30% likely
4. Hypothesis 5 (Validator brittleness) - 20% likely
5. Hypothesis 6 (Dataset quality) - 10% likely
6. Hypothesis 1 (Models insufficient) - 5% likely

**Note**: Hypotheses are not mutually exclusive (multiple can be true).

---

### Phase 3: Systematic Fixes (Session 2+)

**NOW we can code.** Apply fixes in order of impact.

#### Fix Priority Order

**Priority 1: Test Code-Specific Models** (if Hypothesis 2 confirmed)
- Install `nomic-ai/CodeRankEmbed` (137M, CPU-friendly)
- Test with 5 concepts as quick validation
- If promising (>40% P@5), run full test suite
- Expected improvement: +25 to +45 percentage points

**Priority 2: Add Task Prefixes** (if Hypothesis 3 confirmed)
- Modify test script to use correct prefixes per model
- Retest existing models with prefixes
- Expected improvement: +10 to +20 percentage points

**Priority 3: Adjust Success Threshold** (if Hypothesis 4 confirmed)
- Accept 50-60% P@5 as "GO" (not 70%)
- Justify based on task difficulty vs CodeSearchNet
- Document adjusted expectations

**Priority 4: Refine Validators** (if Hypothesis 5 contributing)
- Add regex patterns for implicit patterns (closures)
- Accept multiple implementation styles (async patterns)
- Expected improvement: +5 to +10 percentage points

**Priority 5: Curate Dataset** (if Hypothesis 6 contributing)
- Use tutorial repos (files labeled by concept)
- Sample from concept-focused directories
- Expected improvement: +5 to +10 percentage points

---

## Decision Framework: When to Proceed vs Pivot

After systematic investigation and fixes:

### GO to Phase 2 (Chunking Tests)
**Conditions**:
- Best model achieves ≥50% P@5 with code-specific models
- Clear path to 60-70% with minor improvements
- Models run on available hardware (CPU or Colab GPU)

### CONDITIONAL GO
**Conditions**:
- Models achieve 40-50% P@5
- Improvements possible with query hints or hybrid approach
- Acceptable for MVP with reduced scope (Python-only)

### PIVOT Approach
**Conditions**:
- Code-specific models still <40% P@5
- GPU required but unavailable/expensive
- Consider alternatives:
  1. Docstring→code (easier task, proven to work)
  2. Keyword search + LLM reranking (hybrid)
  3. Single-language only (reduce complexity)

### STOP Project
**Conditions**:
- Code-specific models <30% P@5
- No clear improvement path
- Task fundamentally too hard for current models
- Wait 6-12 months for better models

---

## Key Files to Review

### Test Infrastructure
- `phase1/test_embeddings.py` - Main test script (need to check prefix usage)
- `phase1/concept_validators.py` - Validation logic (check brittleness)
- `phase1/dataset_generator.py` - Sampling strategy (check quality)

### Results
- `phase1/all_results.json` - Complete results for all models
- `phase1/comparison.md` - Summary table
- `phase1/results_*.json` - Per-model detailed results

### Documentation
- `docs/phase1_context.md` - Original test plan
- `docs/PHASED_PLAN.md` - Overall project phases
- `docs/CONTEXT.md` - Project background

---

## Session Checklist

At the start of each session, verify progress on:

- [ ] **Evidence Collection Complete?**
  - [ ] Reviewed actual test code (prefixes, similarity calculation)
  - [ ] Verified model specifications (training data, benchmarks)
  - [ ] Identified code-specific models to test
  - [ ] Established realistic performance baseline

- [ ] **Root Cause Confirmed?**
  - [ ] Ranked hypotheses by likelihood
  - [ ] Identified primary cause(s)
  - [ ] Identified secondary contributors

- [ ] **Fix Plan Defined?**
  - [ ] Prioritized fixes by expected impact
  - [ ] Defined success criteria for each fix
  - [ ] Estimated time/resources needed

- [ ] **Fixes Applied?**
  - [ ] Tested code-specific models
  - [ ] Added task prefixes (if needed)
  - [ ] Refined validators (if needed)
  - [ ] Re-evaluated against thresholds

- [ ] **Decision Made?**
  - [ ] GO / CONDITIONAL / PIVOT / STOP
  - [ ] Documented rationale
  - [ ] Next phase plan (if proceeding)

---

## Critical Principles

1. **Evidence before action**: Don't code until root cause is confirmed
2. **One fix at a time**: Test impact of each change independently
3. **Document everything**: Update this doc with findings
4. **Realistic expectations**: 50-60% P@5 may be acceptable for this task
5. **Kill bad ideas fast**: If code-specific models fail, pivot immediately

---

## Next Steps

**Current Status**: Awaiting evidence collection (Step 1.1-1.4)

**Immediate Action**: Review `test_embeddings.py` to check prefix usage and model encode calls.

**Session Goal**: Complete Phase 1 investigation, confirm root cause(s), define fix plan.
