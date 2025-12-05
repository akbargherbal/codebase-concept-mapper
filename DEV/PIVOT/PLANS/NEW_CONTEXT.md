# Project Brief: Code Concept Mapper with Google File Search

## Project Overview

I am developing a **Retrieval-Augmented Generation (RAG) system** that maps natural language learning concepts to actual code implementations in open-source repositories. This project enables developers and students to explore programming concepts through real-world code examples (e.g., "React Hooks" → relevant useEffect implementations in production codebases).

### Project History & Pivot

**Original Approach (FAILED)**:

- Tested 5 open-source embedding models on 84 code files
- Goal: Achieve ≥70% P@5 (Precision at 5) for concept → code retrieval
- **Result**: Maximum 35% accuracy achieved
- **Root Cause**: General-purpose embeddings cannot reliably map natural language concepts to code implementations
- **Decision**: Project placed on hold with open-source approach

**New Approach (CURRENT)**:

- **Pivot to Google Gemini File Search Tool** (managed RAG infrastructure)
- Google handles: document parsing, chunking, embeddings, vector storage, retrieval
- Focus shifts to: business logic, concept taxonomy, validation, ranking
- **Key Architectural Decision**: Build thin abstraction layer to prevent vendor lock-in while leveraging Google's infrastructure

### Previous Success (Reference Project)

Successfully built a local RAG system for a 100+ hour Python course that enabled semantic search on video subtitles (SRT files). Proved viability of LlamaIndex, LanceDB, Snowflake embeddings, and ms-marco reranker for NL→NL retrieval. This project is **different in nature**: requires NL→code semantic mapping, not NL→NL.

---

## Core Concept & End Goals

### Primary Use Case: Concept → Code Mapping (Search-Based)

**Input**: Natural language learning concept from course outline
**Output**: Ranked list of code files/snippets implementing that concept

**Example**:

```
Query: "Python Context Managers"
Results:
  1. /flask/src/werkzeug/local.py::LocalProxy.__enter__() (lines 45-52)
  2. /django/db/transaction.py::atomic() (lines 180-195)
  3. /requests/sessions.py::Session.request() (lines 23-35)
```

### Secondary Use Case: Repository Analysis (Coverage Reports)

**Input**: Repository + course outline
**Output**: Coverage analysis showing which concepts are present/missing

**Example**:

```
Analyzing Flask repository against "Python Web Development" course:
  ✅ Context Managers (3 examples found)
  ✅ Decorators (5 examples found)
  ✅ Async/Await (2 examples found)
  ❌ Metaclasses (0 examples found)

Coverage: 7/8 concepts (87.5%)
```

### Target Scenarios

**Scenario B: Code Discovery/Navigation**

- User types concept → instant search across indexed codebases
- Exploratory learning: "Show me all Promise examples in this repo"
- Flexible queries beyond predefined taxonomy

**Scenario D: Repository Analysis**

- "Does this repo cover these 20 concepts from my syllabus?"
- Gap analysis for curriculum planning
- Reliable coverage metrics for course validation

---

## Objectives

### Primary Goal

**Validate that Google File Search can achieve ≥70% accuracy for NL→code concept mapping within 1 week**

### Secondary Goals

1. **Build abstraction layer** separating business logic from Google infrastructure
2. **Preserve original Phase 1 work**: Reuse concept taxonomy, validators, ranking logic
3. **Enable future flexibility**: Design allows swapping Google for OpenAI/custom providers
4. **Multi-language support**: Test if single system handles Python + JavaScript effectively
5. **Production viability**: Document cost, performance, and scaling characteristics

### Desired Outputs

- Working MVP with CLI/UI for concept queries
- Quantitative accuracy comparison: Open-source (35%) vs Google (target ≥70%)
- Abstraction layer code demonstrating provider independence
- Documentation of what works, what fails, and next steps

---

## Technical Approach

### What Google Handles (Infrastructure)

- **Document parsing**: Upload PDFs, code files, markdown (40+ file types)
- **Semantic chunking**: Configurable (250 tokens, 50 overlap for code)
- **Embedding generation**: Gemini embedding models (code-optimized)
- **Vector storage**: Free managed storage, no setup required
- **Similarity search**: Cosine similarity, multi-hop queries
- **Citation tracking**: Grounding metadata with source chunks

**Key Benefits**: Zero infrastructure management, no GPU required, ~$10-50/month cost

### What You Control (Business Logic)

#### 1. Concept Taxonomy

Define how learning concepts map to code patterns:

```
"Promises" → ["Promise", "async/await", ".then()", "Promise.all", "catch"]
"Decorators" → ["@", "decorator", "functools.wraps", "wrapper"]
```

#### 2. Query Generation

How to phrase searches to Google:

- Expand concepts using taxonomy
- Add language/framework context
- Include difficulty hints (beginner vs advanced)

#### 3. Post-Retrieval Validation

Keyword-based validators from original Phase 1:

```python
PROMISE_VALIDATOR = {
    "must_contain_any": ["new Promise", ".then(", "async ", "await "],
    "must_not_contain": ["def ", "import python"],
    "min_length": 100
}
```

#### 4. Custom Ranking

Score results by:

- Google's relevance score (baseline)
- Keyword validation match
- Code quality indicators (docstrings, error handling)
- Difficulty level alignment (beginner wants simple examples)

#### 5. Metadata Schema

Tag files with custom metadata:

```python
{
    'language': 'javascript',
    'framework': 'express',
    'concepts': ['promises', 'async'],
    'difficulty': 'intermediate',
    'file_type': 'implementation'  # vs test, config
}
```

### Abstraction Layer Design

**Three-Layer Architecture**:

```
┌─────────────────────────────────────────────┐
│ BUSINESS LOGIC LAYER (Your Code)            │
├─────────────────────────────────────────────┤
│ • ConceptToCodeMapper                       │
│ • Concept taxonomy & expansion              │
│ • Validators & ranking logic                │
│ • Query generation                          │
│ • Result filtering & deduplication          │
└──────────────────┬──────────────────────────┘
                   ↓ (Provider-agnostic interface)
┌─────────────────────────────────────────────┐
│ ABSTRACTION LAYER (Swappable)               │
├─────────────────────────────────────────────┤
│ • RetrievalProvider interface               │
│ • CodeChunk domain model                    │
│ • RetrievalQuery domain model               │
└──────────────────┬──────────────────────────┘
                   ↓ (Implementation-specific)
┌─────────────────────────────────────────────┐
│ INFRASTRUCTURE (Outsourced to Google)       │
├─────────────────────────────────────────────┤
│ • GoogleFileSearchProvider                  │
│ • Chunking, embeddings, vector search       │
│ • Can swap: OpenAI, Pinecone, Custom        │
└─────────────────────────────────────────────┘
```

**Key Principle**: Google handles "hard" infrastructure problems. You handle "easy" but business-critical logic that defines product behavior. The abstraction layer ensures you can pivot providers without rewriting business logic.

---

## Main Concerns and Constraints

### Technical Risks (From Original Phase 1 Failure)

**Known Challenge**: Semantic mapping NL concepts → code is fundamentally difficult

- Open-source models failed at 25-35% P@5
- Even with code-specific embeddings (tested in original Phase 1)
- Google may also struggle without proper prompting/metadata

**Mitigation Strategy**:

1. **Phase 1 validation first** (2 days): Test Google before building abstraction
2. **Hybrid approach ready**: If Google gets 50-70%, add your validators to boost accuracy
3. **Scope reduction option**: Fall back to Python-only if multi-language fails
4. **Stop condition**: If Google <50%, acknowledge task is too hard for current technology

### Cost Constraints

**Budget**: ~$10-50/month for production scale

- Google File Search: Free storage, free embeddings, pay only for API calls
- **Free tier**: 1GB storage (sufficient for 100-200 repos)
- **Paid tier**: $10/month for 10GB (1000+ repos)
- Gemini API costs: ~$0.0001/token (minimal for query volume)

**Expected Usage**:

- 100 files × 500 lines = 50K tokens indexing (one-time, free)
- 20 queries/day × 1K tokens = $0.60/month
- **Well within budget**

### Timeline Constraints

**Maximum**: 1 week (7 days)
**Phased Approach**:

- Days 1-2: Phase 1 validation (Google accuracy testing)
- Days 3-4: Phase 2 abstraction layer (if Phase 1 passes)
- Day 5: Phase 3 multi-language testing (if Phase 2 passes)
- Days 6-7: Phase 4 MVP integration (if Phase 3 passes)

**Stop Conditions**:

- Any phase exceeds 2x estimated time
- Phase 1 <50% accuracy
- Combined system <60% accuracy after all optimizations

### Technical Capability

**Developer Level**: Intermediate/Advanced, solo developer
**Strengths**: Successfully built similar RAG system before, comfortable with LlamaIndex/LanceDB patterns
**Gaps**: No prior experience with Google File Search, abstraction layer design is new
**Learning Budget**: 4-6 hours for Google API documentation and testing

---

## Key Design Decisions

### 1. Concept → Code as Primary Mode

**Chosen Approach**: Search-based retrieval (query embeddings at runtime)

**Alternative Considered**: Code → Concepts tagging (pre-tag all files)
**Why Rejected**: Less flexible, requires upfront tagging, can't handle arbitrary queries

**Hybrid Solution**:

- Primary: Real-time Concept → Code search
- Derived: Generate Code → Concepts coverage by running batch queries and caching results

### 2. Abstraction Layer over Direct Integration

**Chosen Approach**: Build provider-agnostic interface, implement Google wrapper

**Alternative Considered**: Use Google API directly
**Why Rejected**: Vendor lock-in risk, can't pivot if Google becomes expensive or limiting

**Trade-offs**:

- **Cost**: 2-3 days setup vs 1 day pure Google
- **Benefit**: Can swap providers, reuse business logic, maintain competitive advantage

### 3. Metadata-Driven Multi-Language Support

**Chosen Approach**: Single vector store, filter by metadata (language, framework)

**Alternative Considered**: Separate vector stores per language
**Why Rejected**: Higher complexity, harder to maintain, limits cross-language queries

**Implementation**: Upload files with auto-generated metadata tags, filter queries by language

---

## Success Criteria

### Minimum Viable Success (Week 1)

- ✅ Google File Search achieves ≥70% P@5 on 20 test concepts (vs 35% open-source)
- ✅ Abstraction layer working with swappable provider interface
- ✅ Original Phase 1 validators integrated and boosting accuracy
- ✅ Working CLI/UI for concept queries
- ✅ Cost analysis confirms production viability (<$50/month)

### Phase-Specific Go/No-Go Criteria

**Phase 1**:

- GO if ≥70% accuracy
- CONDITIONAL if 50-70% (test with validators)
- NO-GO if <50%

**Phase 2**:

- GO if abstraction layer clean and testable
- ITERATE if design issues (max 2 days)

**Phase 3**:

- GO if multi-language works with metadata filters
- REDUCE SCOPE to Python-only if language mixing fails

**Phase 4**:

- DONE if end-to-end system working
- DOCUMENT limitations if performance issues

### Stretch Goals (If Ahead of Schedule)

- Repository coverage analysis functional
- Auto-tagging with Gemini achieving >80% accuracy
- Performance benchmarks (query latency <3 seconds)
- Documentation for future provider implementations

---

## Lessons from Original Phase 1

### What We Learned (Preserved Knowledge)

1. **Concept taxonomy is critical**: "Promises" needs expansion to ["Promise", "async", "await", ".then()"]
2. **Keyword validators work**: Simple must_contain/must_not_contain logic catches false positives
3. **Multi-language is hard**: Need explicit language filtering to avoid confusion
4. **Ranking matters**: Raw similarity scores aren't enough, need quality signals
5. **Task difficulty**: NL→code mapping is fundamentally harder than NL→NL (35% vs expected 70%)

### What We're Reusing

- ✅ Concept taxonomy (20 test concepts)
- ✅ Keyword-based validators (proven in Phase 1)
- ✅ Ranking logic framework (quality scoring)
- ✅ Test dataset (84 code files)
- ✅ Evaluation methodology (P@5 metric)

### What We're Changing

- ❌ Open-source embeddings → Google managed embeddings
- ❌ Manual chunking → Google configurable chunking
- ❌ Local vector DB → Google cloud storage
- ❌ Model selection research → Infrastructure validation testing

---

## Work Style Preferences

### Methodological Approach

- **Evidence-based decisions**: Validate Google in Phase 1 before building abstraction
- **Incremental testing**: Each phase has explicit success criteria
- **Fast failure**: Stop conditions prevent wasting time on broken approaches
- **Pragmatic reuse**: Leverage proven tools (LlamaIndex patterns) where applicable

### Development Priorities

1. **Viability first**: Prove Google works before polishing
2. **Abstraction second**: Prevent vendor lock-in once viability confirmed
3. **Features last**: Only add multi-language, auto-tagging if basics work

### Output Presentation

- **POC stage**: File paths + basic relevance scores acceptable
- **Future**: Code snippet highlighting, syntax coloring, context display
- **Documentation**: Clear explanation of what works, what fails, why

---

## Future Considerations (Beyond Week 1)

### If Project Succeeds

- Add more languages (Java, Go, Rust)
- Improve auto-tagging with fine-tuned prompts
- Build course outline → example code pipeline
- Create UI for repository coverage analysis
- Optimize query performance (<3 second latency)

### If Google Becomes Limiting

- Swap to OpenAI Assistants API (similar managed RAG)
- Swap to custom embeddings + Pinecone (full control)
- Hybrid: Google for indexing, custom ranking
- The abstraction layer makes all these pivots possible

### If Task Remains Too Hard

- Reduce scope to Python-only
- Focus on simpler concepts (avoid abstract patterns)
- Hybrid approach: Keyword search + LLM reranking
- Accept 60% accuracy as "good enough" for educational use

---

## Related Documents

- **PHASED_PLAN.md**: Detailed breakdown of 4 phases with tasks, time estimates, decision criteria
- **CHAT_02.md**: Original diagnostic framework and hypothesis testing for Phase 1 failure
- **CHAT_03.md**: Strategic discussion on abstraction layer design and Google pivot rationale
- **YT_TRANSCRIPT_01.txt**: Technical deep-dive on Google File Search implementation details
- **YT_TRANSCRIPT_02.txt**: Overview of Google File Search benefits and use cases

---

**Last Updated**: December 2025  
**Project Status**: Pivoting to Google File Search after open-source embedding failure (35% P@5)  
**Current Phase**: Pre-Phase 1 (planning complete, ready to begin validation testing)
