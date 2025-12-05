# 🎯 PHASED PLAN: Google RAG Pivot (Concept Mapper)

## 🔄 The Pivot Strategy
**Previous Status:** Phase 1 (Open Source) failed. Accuracy capped at ~35%.
**New Direction:** Leverage **Google Gemini File Search Tool**.
**Why:** Google handles the "Hard" parts (Chunking, Embedding, Vector Indexing) that failed in the open-source attempt.
**The Trade-off:** We accept vendor dependency for *infrastructure* in exchange for immediate viability.
**The Safeguard:** We build a **"Thin Abstraction Layer"** so your business logic (Taxonomy, Validation, Ranking) remains independent. If Google gets too expensive or OpenAI releases something better, you swap the backend, not your logic.

---

## 📊 PROJECT RISK ANALYSIS (Revised)

### Critical Path Dependencies
```
Phase 1: Google Viability Test (The "Sanity Check")
    ↓ (If <70% accuracy → STOP. The concept itself might be flawed.)
Phase 2: The Abstraction Layer (The "Decoupling")
    ↓
Phase 3: The Intelligence Layer (Validation & Ranking)
    ↓
Phase 4: Pipeline Integration (Course Outline → Mapped Code)
```

---

# 🚀 PHASE 1: GOOGLE VIABILITY TEST (Day 1 - 2 Hours)

## Goal
**Answer the question:** "Does Google's 'Black Box' actually solve the retrieval problem that the open-source models couldn't?"

## Success Criteria
- ✅ **GO:** Google returns relevant code chunks for >70% of the test queries (same queries that failed previously).
- ❌ **NO-GO:** Accuracy remains <50%. This implies the problem isn't the model, but the nature of the query/data mismatch.

## Tasks

### 1.1: Setup Google GenAI Environment (30 mins)
```bash
pip install -q -U google-generativeai
export GOOGLE_API_KEY="your_key_here"
```

### 1.2: The "Dirty" Script (1 hour)
Write a single script `test_google_rag.py` that:
1.  **Uploads** the same 20 test files (Flask/React mix) used in the failed Phase 1.
2.  **Waits** for processing (state=`ACTIVE`).
3.  **Runs** the 5 hardest queries from your previous failure (e.g., "Context Managers", "React useEffect").
4.  **Prints** the `grounding_chunks` returned by Gemini.

*Note: We are NOT looking at the generated text answer. We only care about the `grounding_chunks` (the citations).*

### 1.3: Manual Review & Decision (30 mins)
- Look at the file paths and line numbers in the `grounding_chunks`.
- **Decision:**
    - If it finds `flask/ctx.py` for "Context Managers" → **PROCEED**.
    - If it hallucinates or finds unrelated files → **STOP**.

---

# 🏗️ PHASE 2: THE ABSTRACTION LAYER (Day 2)

## Goal
Build the infrastructure that allows you to swap Google out later. This prevents "Spaghetti Code" where Google API calls are mixed with your business logic.

## Tasks

### 2.1: Define the Interface (1 hour)
Create `src/interfaces.py`:
```python
from dataclasses import dataclass
from typing import List

@dataclass
class CodeChunk:
    file_path: str
    content: str
    score: float
    start_line: int = None

class RetrieverInterface:
    def index_repo(self, repo_path: str, repo_name: str) -> str:
        """Uploads code and returns a store_id"""
        pass

    def search(self, query: str, store_id: str, top_k: int=5) -> List[CodeChunk]:
        """Returns raw code chunks based on query"""
        pass
```

### 2.2: Implement Google Provider (3 hours)
Create `src/providers/google_rag.py` implementing the interface above.
- Handle the `upload_file` logic.
- Handle the `files.create` logic.
- Handle the `model.generate_content` call with `tools=[file_search]`.
- **Crucial:** Parse the complex Google response object to extract *only* the `grounding_chunks` and map them to your clean `CodeChunk` object.

## Phase 2 Deliverable
- A working `GoogleRetriever` class.
- A script that uses the *Interface* to search, not the raw Google SDK.

---

# 🧠 PHASE 3: THE INTELLIGENCE LAYER (Day 3)

## Goal
This is where **YOU** add value. Google gives you *candidates*; you determine if they are *correct*. This is the "Concept → Code" logic.

## Tasks

### 3.1: Query Expansion Logic (2 hours)
The user asks for "Context Managers". Google might prefer "with statement".
- Implement a simple helper (using Gemini Flash or just Python logic) to expand concepts.
- *Input:* "Context Managers"
- *Output:* "Context Managers OR __enter__ OR __exit__ OR @contextlib"

### 3.2: The Validator (3 hours)
Google might return a file that *mentions* a context manager in a comment but doesn't *implement* one.
- Create `src/validator.py`.
- **Logic:**
    - Take the `CodeChunk` returned by Google.
    - Check for keywords (e.g., does `__enter__` exist in the chunk?).
    - (Optional) Pass the chunk to a cheap LLM (Gemini Flash) with prompt: *"Does this code snippet IMPLEMENT {concept}? Answer Y/N."*

### 3.3: The Ranker (2 hours)
- Sort validated chunks.
- Prioritize:
    - Files in `src/` over `tests/` or `examples/`.
    - Chunks with higher semantic scores (if Google provides them, otherwise rely on rank order).

## Phase 3 Deliverable
- A pipeline: `Query -> Expand -> Google Search -> Validate -> Rank -> Result`.

---

# 🔌 PHASE 4: PIPELINE INTEGRATION (Day 4)

## Goal
Connect the Course Outline to the Search Engine to generate the final JSON map.

## Tasks

### 4.1: Batch Processor (3 hours)
Create `generate_course_map.py`:
1.  Load `course_outline.json`.
2.  Iterate through every concept.
3.  Run the Phase 3 pipeline.
4.  Aggregate results.

### 4.2: The "Code → Concept" Cache (2 hours)
(For your "Scenario D: Repository Analysis")
- Implement a mechanism to save the results.
- Structure: `{ "repo_name": { "concept_A": [chunks], "concept_B": [chunks] } }`
- This allows you to instantly answer "Does this repo cover Context Managers?" without re-querying Google.

### 4.3: Final Polish (2 hours)
- Add error handling (Google API rate limits).
- Add a simple CLI: `python main.py --repo ./flask --outline python_course.json`

---

# ⏱️ TIME ESTIMATES

| Phase | Focus | Est. Time | Cost |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Validation** | **2 Hours** | Free (Free tier) |
| **Phase 2** | **Abstraction** | **4 Hours** | Free |
| **Phase 3** | **Intelligence** | **7 Hours** | < $1 (Flash calls) |
| **Phase 4** | **Integration** | **5 Hours** | < $1 |
| **Total** | | **~2.5 Days** | **Negligible** |

---

# 🛑 STOP CONDITIONS (The "Kill Switch")

1.  **Phase 1 Failure:** If Google's File Search tool cannot find "Context Managers" in Flask (a known easy target) with >70% accuracy, **STOP**. The issue is likely that "Concepts" are too abstract for RAG without massive fine-tuning.
2.  **Rate Limits:** If the Google Free Tier limits (15 RPM) make development impossible, we must assess if the paid tier is worth it ($/token) or if we need to batch process slower.
3.  **Grounding Quality:** If Google returns the *answer* correctly but fails to provide the specific *grounding chunk* (the code snippet), the tool is useless for our mapping purpose.

---

# 📝 IMMEDIATE NEXT STEP

**Execute Phase 1.2 (The Dirty Script).**
Do not write the abstraction layer yet. Do not worry about validators.
Just take your 20 test files, upload them to Google AI Studio or via script, and see if it finds the code.