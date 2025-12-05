# Session Summary: Phase 1A Validation & Phase 1B Design

**Date:** December 5, 2025
**Session Focus:** Validating Google File Search (Phase 1A) & Designing Ground Truth Tools (Phase 1B)

---

## 1. Phase 1A: Google File Search Validation (Completed)

We started by running a "quick and dirty" test to see if Google File Search was viable enough to proceed.

**The Test:**

- **Corpus:** 21 core files from the Flask library.
- **Queries:** 5 concepts (Context Managers, Decorators, Generators, Async, Metaclasses).
- **Method:** Keyword-based validation of returned chunks.

**The Results:**

- **Success:** 3/5 queries returned valid code chunks (Context Managers, Decorators, Generators).
- **Failure:** 2/5 queries failed (Async, Metaclasses) - likely due to strict keyword matching in our validator rather than retrieval failure.
- **Accuracy:** **60%** (Target was ≥40%).

**The Decision:**

> **PROCEED TO PHASE 1B.**
> Google File Search shows enough promise to warrant a full build. However, to measure _true_ accuracy (and improve that 60%), we need a rigorous "Ground Truth" dataset, not just simple keyword checks.

---

## 2. Strategic Pivot: Tool Engineering vs. Prompt Engineering

To generate this Ground Truth (Phase 1B), we initially considered a standard "System Archaeologist" persona. We identified a critical risk: **LLM Unreliability.**

- **Risk:** Asking an LLM to output raw JSON often leads to syntax errors.
- **Risk:** Asking an LLM to count line numbers (`"lines": [10, 25]`) leads to hallucinations and drift when files change.

**Decision:** We shifted from "Prompt Engineering" (hoping the LLM behaves) to **"Tool Engineering"** (forcing the LLM to use a deterministic interface).

---

## 3. The "Anchor & Extract" Strategy

To solve the line number hallucination problem, we devised the **Anchor & Extract** method:

1.  **The AI's Job (Semantic):** Identify the _concept_ and the _named entity_ implementing it.
    - _Input:_ "I found a Context Manager in `werkzeug/local.py`. It is the class `LocalProxy`."
2.  **The Tool's Job (Deterministic):** Calculate the exact location and extract the code.
    - _Action:_ Parse `werkzeug/local.py` using Python's AST.
    - _Result:_ "Class `LocalProxy` starts on line 45 and ends on line 62."
    - _Storage:_ Save the actual code snippet into the JSON for verification.

---

## 4. Artifacts Designed (Ready for Implementation)

### A. The Tool: `concept_mapper.py`

A Python CLI utility that acts as the **State Manager**. The AI Agent is restricted to using _only_ this tool.

**Key Features:**

- **AST Parsing:** Accepts `--identifier ClassName` and calculates line numbers programmatically.
- **Atomic Writes:** Writes to `.tmp` and uses `os.replace` to prevent corruption.
- **Automatic Backups:** Rotates backups (`.mapper_backups/`) before every write.
- **Schema Enforcement:** Ensures the JSON structure is always valid.
- **Duplicate Detection:** Prevents mapping the same entity twice.

### B. The Persona: `GEMINI.md`

The System Prompt that governs the AI Agent's behavior.

**Key Directives:**

- **Role:** Code Concept Auditor.
- **Constraint:** NEVER write JSON directly. ALWAYS use `concept_mapper.py`.
- **Workflow:**
  1.  `grep`/`find` to discover candidates.
  2.  `cat` to verify logic.
  3.  `python concept_mapper.py add ...` to record findings.
- **Priority:** Prefer **Named Identifiers** (Classes/Functions) over manual line numbers.

---

## 5. The Data Schema (`concepts_map.json`)

We defined the strict schema that the tool will enforce:

```json
{
  "metadata": {
    "project": "flask",
    "last_updated": "2025-12-05T12:30:00",
    "version": "1.1"
  },
  "concepts": {
    "context_managers": {
      "display_name": "Context Managers",
      "definition": "Classes implementing __enter__ and __exit__",
      "implementations": [
        {
          "file_path": "src/werkzeug/local.py",
          "identifier": "LocalProxy",
          "line_start": 45,
          "line_end": 62,
          "code_snippet": "class LocalProxy:\n    def __enter__(self)...",
          "confidence": "high",
          "evidence": "Class defines __enter__ and __exit__ methods"
        }
      ]
    }
  }
}
```

---

## 6. Next Session Plan

**Goal:** Execute Phase 1B (Ground Truth Generation).

1.  **Review & Refine:**
    - Final check of `concept_mapper.py` logic (AST parsing edge cases).
    - Final polish of `GEMINI.md` instructions.
2.  **Implementation:**
    - Save the tool and prompt to the `PLAYGROUND` directory.
    - Initialize the `flask` project map.
3.  **Execution:**
    - Run the Gemini CLI with the new persona.
    - Audit 3-5 concepts (Context Managers, Decorators, Generators) in Flask.
4.  **Validation:**
    - Inspect the generated `concepts_map.json`.
    - Verify that code snippets and line numbers are accurate.

**Status:** Phase 1A passed. Phase 1B design complete. Ready for code generation and execution.
