# Session Summary: Code Concept Mapper Project Review

**Date:** December 5, 2024  
**Session Focus:** Big picture review after project hiatus, validation strategy refinement

---

## Project Overview (What We're Building)

### Core Goal
Build a **semantic code search engine** that maps abstract programming concepts to concrete implementations in real-world codebases.

### Primary Use Case
**Educational Content Generation:**
- **Input:** "Context Managers in Flask"
- **Output:** Ranked list of actual production code files/functions that implement context managers
- **Why:** Replace toy examples with real-world patterns from respected libraries

### The Mental Model You Clarified
```
Framework X (Flask) 
    ↓
Concept Y (Context Managers) 
    ↓
File U / Function V in Repo R (werkzeug/local.py::LocalProxy.__enter__())
```

---

## Project History

### Phase 1 (Open Source) - FAILED
- Tested 5 open-source embedding models
- Result: **35% accuracy** (target was ≥70%)
- **Root cause:** General-purpose embeddings can't map natural language concepts → code implementations
- **Decision:** Project placed on hold

### Current Status: Google Pivot
- **New approach:** Use Google Gemini File Search Tool (managed RAG infrastructure)
- Google handles: chunking, embeddings, vector storage, retrieval
- You control: taxonomy, validators, ranking logic, business rules
- **Critical assumption:** Google File Search achieves ≥70% accuracy

---

## Two Operating Modes

### Mode A: Interactive Search (Primary)
```python
Query: "Context Managers in Flask"
→ Returns: Top 5 implementations in real-time
→ Use case: Code discovery, learning, exploration
```

### Mode B: Batch Analysis (Derived from A)
```python
Input: Repository + 20 concepts
→ Run Mode A for each concept, cache results
→ Output: "Flask covers 15/20 concepts (75%)"
→ Use case: Curriculum planning, gap analysis
```

**Decision:** Build Mode A first (validates viability), add Mode B only if A succeeds.

---

## The Critical Validation Problem

### Your Key Question
> "How do we know context managers are actually in Flask file X? What are the assumptions?"

### The Breakthrough
We don't need to know the "correct" file path beforehand. Instead:

**Validate based on CODE CONTENT, not file names:**
```python
# Don't check: "Did Google find local.py?"
# Instead check: "Does the returned code contain __enter__ and __exit__?"
```

---

## Three Validation Approaches Discussed

### Approach 1: Keyword Validators (From Phase 1)
```python
CONTEXT_MANAGER_VALIDATOR = {
    "must_contain_any": ["__enter__", "__exit__", "@contextmanager"],
    "must_not_contain": ["# example", "def test_"],
    "min_length": 50
}
```
**Pros:** Free, instant, deterministic  
**Cons:** Less accurate, brittle, misses edge cases

### Approach 2: LLM Ground Truth Generation (Your Proposal)
```python
# Use Claude/GPT-4 to audit codebase ONCE
# Generate reference JSON: "These 3 files implement context managers"
# Then test: Does Google find what the LLM found?
```
**Pros:** More accurate, reusable, version-controlled  
**Cons:** Costs $1-2, takes 2-4 hours, LLM might hallucinate

### Approach 3: Hybrid (Recommended)
```python
# Stage 1: Quick keyword validation (2 hours)
if accuracy < 40%: STOP

# Stage 2: LLM ground truth for validation (2-4 hours)  
if 40% <= accuracy < 70%:
    generate_ground_truth_with_llm()
    recalculate_accuracy()
```

---

## Gemini CLI Approach (Your Latest Idea)

### The Concept
Use **Gemini CLI** as a semi-automated auditor to generate ground truth:

1. **GEMINI.md = System Prompt**
   - Per-project instructions for how to identify concepts
   - Version controlled, persistent across sessions
   - Example: "Context Managers = classes with __enter__ and __exit__"

2. **Custom Tool = Data Integrity**
   ```python
   # write_concept_json.py
   # - Schema validation
   # - Atomic writes (prevent corruption)
   # - Type checking
   ```

3. **Batch Processing**
   ```bash
   cd repos/flask
   gemini "Audit for all Python concepts" → concepts_python.json
   
   cd repos/django  
   gemini "Audit for all Python concepts" → concepts_python.json
   ```

### Key Insight from Discussion
**GCLI is a productivity multiplier, not fully autonomous:**
- Still requires manual validation (especially first run)
- Should be 5-10x faster than pure manual auditing
- Risk: LLM hallucination, inconsistency across runs
- Mitigation: Validation layer, multiple passes, confidence scoring

---

## Ground Truth JSON Format (What LLM Should Generate)

### Essential Fields
```json
{
  "concept": "Context Managers",
  "language": "python",
  "implementations": [
    {
      "file_path": "src/werkzeug/local.py",
      "class_or_function": "LocalProxy",
      "line_range": [45, 62],
      "confidence": "high",
      "evidence": {
        "key_patterns_found": ["__enter__", "__exit__"],
        "is_production_code": true,
        "is_test_code": false
      }
    }
  ],
  "summary": {
    "total_implementations_found": 3,
    "high_confidence": 3,
    "primary_files": ["src/werkzeug/local.py", "src/werkzeug/ctx.py"]
  }
}
```

### Why This Format Works
- **For testing:** Check if Google found ANY of the `primary_files`
- **For metrics:** Calculate P@5 with confidence weighting
- **For debugging:** Understand WHY Google failed (missed these files)
- **For validation:** Evidence can be programmatically verified

---

## Recommended Next Steps (When You Resume)

### Week 1 Plan

**Day 1 (2-3 hours): GCLI Proof of Concept**
```bash
1. Setup: Create write_concept_json.py tool + GEMINI.md
2. Test: ONE concept (Context Managers) in Flask
3. Validate: Manually check every result
4. Decision: Does GCLI find the right files?
```

**Day 2 (if Day 1 succeeds): Scale to 5 Concepts**
```bash
5. Run GCLI on 5 Python concepts in Flask
6. Validate: Spot-check 20% of results
7. Refine: Update GEMINI.md based on failures
```

**Days 3-4 (if Day 2 succeeds): Full Ground Truth**
```bash
8. Generate: All 20 concepts for Flask + Django
9. Validate: Automated checks + manual review
10. Freeze: Lock ground truth JSON files
```

**Day 5: Test Google File Search**
```bash
11. Compare: Google retrieval vs ground truth
12. Calculate: Actual accuracy (target ≥70%)
13. Decision: GO/NO-GO for building the system
```

---

## Critical Decision Points

### Phase 1A: Keyword Validation (Fast)
```
If keyword_accuracy < 40% → STOP (Google clearly failing)
If keyword_accuracy ≥ 40% → Proceed to Phase 1B
```

### Phase 1B: LLM Ground Truth (Rigorous)
```
If LLM_validated_accuracy ≥ 70% → GO (Build Phase 2 abstraction)
If 50-70% → CONDITIONAL (Hybrid approach with validators)
If < 50% → STOP (Task fundamentally too hard)
```

---

## Key Architectural Insights

### What Google Handles (Infrastructure)
- Document chunking (configurable: 250 tokens, 50 overlap)
- Embedding generation (code-optimized)
- Vector storage (free, managed)
- Similarity search

### What You Control (Business Logic)
- Concept taxonomy ("Promises" = ["Promise", "async/await", ".then()"])
- Query generation (how to phrase searches)
- Post-retrieval validation (keyword checks)
- Custom ranking (quality, difficulty, relevance)
- Metadata schema (language, framework, concepts)

### Abstraction Layer Design
```
Business Logic (Your code - portable)
    ↓
Provider Interface (Swappable)
    ↓
Google File Search (Current provider)
```

**Goal:** Can swap Google for OpenAI/custom later without rewriting business logic.

---

## Open Questions for Next Session

1. **GCLI Setup:**
   - Have you installed/tested Gemini CLI?
   - Do you have API access configured?

2. **Approach Selection:**
   - GCLI ground truth generation vs keyword validators vs hybrid?
   - How much time can you allocate to ground truth generation?

3. **Validation Strategy:**
   - Manual validation tolerance (how much human oversight)?
   - Acceptable accuracy threshold (really 70% or flexible)?

4. **Scope:**
   - Start with Python only, or multi-language from start?
   - How many repos for ground truth (2? 5? 10?)?

---

## Resources Created This Session

### Planning Documents Reviewed
- `DETAILED_PLAN.md` - 4-phase implementation plan
- `FAST_PLAN.md` - Condensed rapid validation approach
- `NEW_CONTEXT.md` - Complete project context
- `PRICING.md` - Google cost breakdown
- `RESOURCES.md` - Prerequisites checklist
- `GEMINI_CLI_GUIDE.md` - CLI reference for ground truth generation

### Key Concepts Clarified
- Framework → Concept → File/Function mapping
- Validation based on code content, not file paths
- GCLI as semi-automated auditor with human oversight
- Ground truth JSON schema for testing

---

## State When We Resume

**Where we left off:** You're evaluating whether to use GCLI for ground truth generation.

**Next decision:** Choose validation approach and run Phase 1 proof of concept.

**Blocker:** None - project is ready to proceed with validation testing.

**Your action item:** Think about GCLI approach feasibility and time investment.

---

**Status:** Planning complete, awaiting decision on validation strategy to begin Phase 1 execution.