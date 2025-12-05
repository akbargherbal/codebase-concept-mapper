# 🎯 PHASED PLAN: Code Concept Mapper with Google File Search

## 📊 PROJECT CONTEXT & PIVOT RATIONALE

### Why We're Pivoting from Open Source

- **Phase 1 Result**: Open-source embeddings failed at 25-35% P@5 (target was ≥70%)
- **Root Cause**: General-purpose models cannot reliably map natural language concepts → code implementations
- **Decision**: Project on hold with open-source approach → **Pivot to Google File Search**

### What Google File Search Solves

Google's Gemini File Search tool provides a fully managed RAG pipeline that handles document chunking, embedding generation, vector storage, and retrieval automatically. This eliminates the infrastructure work that blocked our open-source approach.

### Strategic Architecture Decision

Based on your "computer vs bundled package" analogy from CHAT_03:

**YOU CONTROL** (Business Logic):

- Concept taxonomy (what defines "Promises"?)
- Query generation (how to search for concepts)
- Result validation (keyword-based validators from original Phase 1)
- Ranking logic (quality scoring, difficulty levels)
- Course outline integration

**GOOGLE HANDLES** (Infrastructure):

- Document parsing and chunking
- Embedding generation
- Vector storage and indexing
- Similarity search
- Infrastructure scaling

**Key Principle**: Build a thin abstraction layer that uses Google as the infrastructure provider while keeping your business logic separate and portable. This prevents vendor lock-in while leveraging Google's managed infrastructure.

---

## 🎯 END GOAL CLARIFICATION

From CHAT_03 discussion, the system has **two operational modes**:

### Primary Mode: Concept → Code (Search-Based)

```
INPUT: "Python Context Manager"
OUTPUT: [
  /flask/src/werkzeug/local.py::LocalProxy.__enter__(),
  /django/db/transaction.py::atomic(),
  /requests/sessions.py::Session.request()
]
```

**Use Cases**:

- Code discovery/navigation (Scenario B)
- Repository analysis (Scenario D)
- Educational content generation

### Derived Mode: Code → Concepts (Analysis)

Generate coverage reports by running batch queries for all taxonomy concepts against a repository, then cache results.

---

## 📋 REVISED PHASED APPROACH

### Strategic Differences from Original Plan

1. **Phase 1 becomes validation, not model selection** - Testing Google's retrieval, not comparing models
2. **Chunking is configurable, not custom** - Google handles it, we tune parameters
3. **Focus shifts to abstraction layer** - Ensuring we can pivot away from Google later
4. **GPU/infrastructure concerns eliminated** - Google's managed service

---

## 🚀 PHASE 1: GOOGLE RETRIEVAL VALIDATION (Days 1-2, CRITICAL)

### Goal

**Answer: "Does Google File Search accurately map NL concepts → code implementations for our use case?"**

### Success Criteria (Go/No-Go Decision)

- ✅ **GO**: Google achieves ≥70% accuracy on 20 test concept queries
- ⚠️ **CONDITIONAL**: 50-70% accuracy → Add post-filtering with your validators
- ❌ **NO-GO**: <50% accuracy → Task is fundamentally harder than expected, reduce scope

### Tasks

#### 1.1: Setup & Quick Indexing Test (2 hours)

- Get Google AI Studio API key (free tier: 1GB storage)
- Upload 2 small test repos (Flask for Python, Express for JavaScript)
- Configure chunking parameters:
  - `max_tokens_per_chunk`: 250 (code-optimized)
  - `overlap_tokens`: 50 (preserve context)
- Test upload time and verify files processed

#### 1.2: Test Core Concept Queries (4 hours)

Run the **same 20 concept queries from original Phase 1** to enable direct comparison:

**Python Concepts** (from original validators):

- Context Managers
- Decorators
- Async/Await
- Generators
- List Comprehensions

**JavaScript Concepts**:

- Promises
- Async/Await
- React Hooks (useEffect, useState)
- Higher-Order Functions
- Closures

**For each query**:

1. Call Google File Search API
2. Examine grounding chunks returned
3. Validate with your keyword-based validators (reuse from original Phase 1)
4. Calculate P@5 (Precision at 5 results)

#### 1.3: Analyze Retrieval Quality (2 hours)

**Key Questions**:

- Are grounding chunks at the right granularity (functions/classes vs whole files)?
- Does Google confuse cross-language concepts (Python async vs JavaScript async)?
- Do metadata filters help (language, framework tags)?

**Document**:

- Which concepts work well (≥80% accuracy)
- Which concepts fail (<50% accuracy)
- Common failure patterns (retrieving comments instead of implementations, wrong language, etc.)

#### 1.4: Phase 1 Decision Point (1 hour)

**IF Google ≥70% accuracy**:

- ✅ **PROCEED TO PHASE 2**
- Google's retrieval is viable
- Focus Phase 2 on abstraction layer design

**IF Google 50-70% accuracy**:

- ⚠️ **CONDITIONAL PROCEED**
- Google handles infrastructure, but needs your validators
- Hybrid approach: Google retrieval + your post-filtering
- Test if combined approach reaches ≥70%

**IF Google <50% accuracy**:

- ❌ **REASSESS PROJECT SCOPE**
- Problem isn't open-source vs Google—it's task difficulty
- Options:
  1. Reduce to single language (Python-only)
  2. Simpler concepts (avoid abstract patterns like "decorators")
  3. Different approach (keyword search + LLM reranking)

### Phase 1 Deliverables

- [ ] Google File Search working with 2 test repos
- [ ] Quantitative accuracy on 20 concept queries
- [ ] Comparison to original Phase 1 results (25-35% open-source vs Google)
- [ ] Go/No-Go decision documented

---

## 🏗️ PHASE 2: ABSTRACTION LAYER DESIGN (Days 3-4, CONDITIONAL)

**Entry Condition**: Phase 1 achieved acceptable accuracy (≥50% with path to ≥70%)

### Goal

**Build a thin abstraction layer that keeps your business logic independent of Google's infrastructure**

### Success Criteria

- ✅ Clean interface separating retrieval (Google) from business logic (yours)
- ✅ Can swap Google implementation for OpenAI/custom in future
- ✅ Your Phase 1 validators and ranking logic integrated
- ✅ System handles metadata (language, framework, difficulty level)

### Tasks

#### 2.1: Define Provider-Agnostic Interfaces (4 hours)

Design interfaces that any retrieval provider must implement:

**Core Abstractions**:

1. **Domain Models**: `CodeChunk`, `RetrievalQuery`, `ConceptMetadata`
2. **Provider Interface**: `RetrievalProvider` with methods:
   - `index_codebase()` - Upload and process files
   - `retrieve()` - Search for concept, return chunks
   - `delete_store()` - Cleanup
3. **Business Logic Layer**: `ConceptToCodeMapper` that uses any provider

**Key Design Decisions**:

- What metadata schema for tagging code? (language, framework, concept_tags, difficulty)
- How to pass filters to providers? (metadata_filter dictionary)
- How to score and rank results? (provider score + your custom scoring)

#### 2.2: Implement Google Provider Wrapper (6 hours)

Create `GoogleFileSearchProvider` that implements `RetrievalProvider` interface:

**Responsibilities**:

- Translate your domain models → Google API calls
- Handle file uploads with your metadata schema
- Convert Google's grounding chunks → your `CodeChunk` model
- Apply metadata filters during retrieval

**What stays in YOUR code** (not Google's):

- Metadata extraction logic (how to tag files)
- Custom metadata schema (what tags to use)
- Prompt engineering (how to phrase queries to Google)

#### 2.3: Integrate Your Business Logic (6 hours)

Build `ConceptToCodeMapper` that implements:

**Query Generation**:

- Expand concepts using your taxonomy (e.g., "Promises" → ["Promise", "async/await", ".then()", "Promise.all"])
- Add language/framework context to queries

**Post-Retrieval Processing**:

- Validate with your keyword-based validators (from original Phase 1)
- Score quality (has docstrings? error handling? clean code?)
- Rank by difficulty (beginner vs advanced examples)
- Deduplicate results

**Key Insight**: This is where your competitive advantage lives—Google handles infrastructure, but your taxonomy, validators, and ranking logic define the product behavior.

#### 2.4: Test Abstraction with Mock Provider (2 hours)

Create a simple mock provider that returns dummy data to verify:

- Business logic works independent of Google
- Easy to swap providers
- Interfaces are well-defined

### Phase 2 Deliverables

- [ ] Interface definitions documented
- [ ] Google provider implementation working
- [ ] Business logic layer integrated
- [ ] Mock provider test passes

---

## 🌍 PHASE 3: MULTI-LANGUAGE & METADATA (Day 5, CONDITIONAL)

**Entry Condition**: Phase 2 abstraction layer working

### Goal

**Validate that metadata-driven filtering enables accurate multi-language retrieval**

### Success Criteria

- ✅ Can query "Promises in JavaScript" and filter out Python results
- ✅ Single vector store handles multiple languages accurately
- ✅ Auto-tagging with metadata works reliably

### Tasks

#### 3.1: Test Cross-Language Queries (3 hours)

**Without metadata filtering**:

- Query "async programming" against mixed Python/JavaScript repo
- Measure: Does Google return mixed results or dominant language?

**With metadata filtering**:

- Query with `metadata_filter={'language': 'javascript'}`
- Measure: Accuracy improvement?

**With language hints in query**:

- Query "async programming in JavaScript"
- Compare to metadata filtering approach

**Decision**: Which approach works best? (Likely: metadata filters + query hints)

#### 3.2: Implement Auto-Tagging (4 hours)

Use Gemini to auto-generate metadata for uploaded files:

**For each file**:

1. Send code to Gemini Flash Lite
2. Prompt: "Extract: language, framework, 5 concept keywords"
3. Parse JSON response
4. Upload file with generated metadata

**Test accuracy**:

- Manual validation on 20 files
- Do auto-tags match expected concepts?
- Adjust prompt if needed

#### 3.3: Test Repository Analysis Mode (2 hours)

Implement "Code → Concepts" derived functionality:

**Process**:

1. Upload repository with metadata
2. For each concept in your taxonomy:
   - Run query against repository
   - Collect matching chunks
3. Generate coverage report: "Repo covers 15/20 concepts"

**Test**:

- Run on Flask repository with Python concepts
- Verify coverage report accuracy

### Phase 3 Deliverables

- [ ] Multi-language filtering working
- [ ] Auto-tagging implemented and tested
- [ ] Repository analysis mode functional
- [ ] Decision: Single model sufficient or per-language needed?

---

## 🎨 PHASE 4: INTEGRATION & MVP (Days 6-7, CONDITIONAL)

**Entry Condition**: Phases 1-3 working with acceptable accuracy

### Goal

**Deliver a minimal working system that demonstrates Concept → Code mapping**

### Success Criteria

- ✅ CLI/UI where user can enter concept → get ranked code examples
- ✅ Query time <5 seconds
- ✅ Manual validation: ≥70% of results are relevant
- ✅ Documentation for future enhancements

### Tasks

#### 4.1: Build Query Interface (4 hours)

Create simple interface (CLI or Streamlit):

**Inputs**:

- Concept (text input)
- Language filter (dropdown: Python, JavaScript, Any)
- Difficulty (dropdown: Beginner, Intermediate, Advanced)

**Outputs**:

- Top 5 code chunks
- File paths and line numbers
- Relevance scores
- Metadata tags

#### 4.2: End-to-End Testing (4 hours)

Test full pipeline with real course outline:

**Example Course**: "Python Web Development"

- Module: "Context Managers"
- Module: "Async Programming"
- Module: "Decorators"

**For each module**:

1. Query system
2. Review top 5 results
3. Rate relevance (manual validation)
4. Document failures

**Target**: ≥70% of queries return ≥3 relevant results in top 5

#### 4.3: Cost & Performance Analysis (2 hours)

**Cost Calculation**:

- Indexing: How many files? Token count?
- Querying: Average tokens per query?
- Estimated monthly cost at target scale

**Performance Benchmarks**:

- Upload time for 100 files?
- Query latency (target: <5 seconds)
- Can system handle your target dataset size?

#### 4.4: Documentation & Next Steps (2 hours)

Document:

- **What works**: Which concepts/languages have high accuracy
- **What fails**: Known limitations and failure patterns
- **Future enhancements**:
  - Custom chunking strategies
  - Alternative providers (OpenAI, custom embeddings)
  - Advanced ranking algorithms
  - UI improvements

### Phase 4 Deliverables

- [ ] Working CLI/UI
- [ ] End-to-end test results documented
- [ ] Cost/performance analysis
- [ ] Next steps roadmap

---

## 📊 DECISION TREE & STOP CONDITIONS

```
START
  ↓
PHASE 1: Validate Google Retrieval
  ├─ ≥70% accuracy → PHASE 2 (full abstraction)
  ├─ 50-70% accuracy → Test with validators
  │   ├─ Now ≥70% → PHASE 2 (hybrid approach)
  │   └─ Still <70% → REASSESS SCOPE
  └─ <50% accuracy → STOP (task too hard)

PHASE 2: Build Abstraction Layer
  ├─ Abstraction working → PHASE 3
  └─ Design issues → Iterate (max 2 days)

PHASE 3: Multi-Language & Metadata
  ├─ Single model + metadata ≥70% → PHASE 4
  ├─ Language mixing issues → Reduce to Python-only
  └─ Auto-tagging fails → Manual metadata acceptable

PHASE 4: Integration & MVP
  ├─ Working system → DONE
  └─ Performance issues → Document as known limitation

DONE: Working MVP or informed decision to reduce scope
```

### Explicit Stop Conditions

**STOP if**:

- Phase 1 Google retrieval <50% after metadata optimization
- Any phase exceeds 2x estimated time
- Combined system <60% accuracy after all optimizations
- Cost exceeds budget ($50/month for production scale)

**DON'T**:

- Spend >2 days on any single phase
- Try to build custom embeddings if Google fails (proves task is hard)
- Over-optimize before proving viability
- Build features beyond MVP before validating accuracy

---

## ⏱️ TIME ESTIMATES

| Phase     | Best Case  | Worst Case | Includes                  |
| --------- | ---------- | ---------- | ------------------------- |
| Phase 1   | 1 day      | 2 days     | Google setup + validation |
| Phase 2   | 1.5 days   | 2 days     | Abstraction layer         |
| Phase 3   | 0.5 day    | 1 day      | Multi-language testing    |
| Phase 4   | 1 day      | 2 days     | MVP integration           |
| **TOTAL** | **4 days** | **7 days** | Within your constraint    |

---

## 💡 KEY DIFFERENCES FROM ORIGINAL PLAN

| Aspect             | Original (Open Source)    | New (Google Pivot)                    |
| ------------------ | ------------------------- | ------------------------------------- |
| **Phase 1**        | Model selection & testing | Google validation                     |
| **Infrastructure** | LanceDB setup required    | Managed by Google                     |
| **Chunking**       | Custom AST-based          | Configurable parameters               |
| **Embeddings**     | Test 3 models, pick best  | Google's model (fixed)                |
| **GPU**            | Major concern             | Not needed                            |
| **Vendor Lock-in** | None                      | Mitigated by abstraction              |
| **Cost**           | Free (local)              | ~$10-50/month                         |
| **Speed to MVP**   | 7 days (stopped at 35%)   | 4-7 days (higher success probability) |

---

## 🎯 SUCCESS METRICS

### Minimum Viable Success (Week 1)

- ✅ System retrieves relevant code for ≥70% of test concepts
- ✅ Abstraction layer allows future provider swaps
- ✅ Working CLI/UI for concept queries
- ✅ Cost analysis shows production viability

### Stretch Goals (If ahead of schedule)

- Repository coverage analysis working
- Auto-tagging with high accuracy
- Multi-language support validated
- Performance benchmarks documented

This phased plan maintains your risk-minimization approach while adapting to the Google infrastructure pivot. Should we proceed with Phase 1 validation, or do you want to refine the plan further?
