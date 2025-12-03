# Embedding Model Research Query

Use this query with Gemini Deep Research or similar tools to identify the best embedding models for Phase 1 testing.

---

## Primary Research Query

```
Task: Identify the top 3 embedding models for semantic code search (as of early 2025)

Requirements:
1. Natural language → code mapping capability
   - Must handle queries like "promises in JavaScript" → find async/await implementations
   - Should understand programming concepts, not just keyword matching

2. Local CPU execution
   - No GPU required for inference
   - Reasonable inference speed (<10 sec for 20 queries on 100 files)
   - Model size <1GB preferred

3. Installation & Usage
   - Available via pip or Hugging Face
   - Compatible with sentence-transformers library OR provide alternative usage
   - Clear documentation with examples

4. Proven Performance
   - Public benchmarks on code retrieval tasks
   - >60% retrieval accuracy on semantic search
   - Active maintenance (updated in last 6 months)

5. Multi-language Support
   - Handles both Python and JavaScript/TypeScript
   - OR separate recommendations for language-specific models

Search Focus Areas:
- Academic papers on code embeddings (2023-2025)
- GitHub repositories with code search implementations
- Hugging Face model benchmarks for code tasks
- Developer blog posts comparing embedding models for code

For Each Model, Provide:
1. Model Name & Identifier
   - Full name (e.g., "nomic-ai/nomic-embed-text-v1.5")
   - HuggingFace or pip package name

2. Technical Specs
   - Model size (MB/GB)
   - Parameter count
   - CPU vs GPU requirements
   - Expected inference speed

3. Installation
   - Exact pip install command
   - Any additional dependencies
   - Compatibility notes (Python version, OS)

4. Usage Example
   - Code snippet showing how to load model
   - Example of embedding text
   - Example of similarity calculation

5. Benchmark Results
   - Performance on code retrieval tasks
   - Comparison to baseline models
   - Links to papers/documentation

6. Strengths & Weaknesses
   - What this model is optimized for
   - Known limitations
   - Best use cases

Expected Candidates (verify current status):
- nomic-ai/nomic-embed-text-v1.5 (general, code-capable)
- BAAI/bge-small-en-v1.5 (semantic search)
- sentence-transformers/all-MiniLM-L6-v2 (baseline)
- microsoft/codebert-base (code-specific)
- Salesforce/codet5-base (code understanding)
- Other 2024-2025 code embedding models

Prioritize:
1. Models with published benchmarks on code search
2. Recent releases (2024-2025) with architecture improvements
3. Models used in production code search tools
4. Open-source with permissive licenses

Output Format:
Return a comparison table with:
| Model | Size | CPU-Only | Benchmark P@5 | Install | Rec. Priority |

Then provide detailed profiles for top 3 recommendations.
```

---

## Follow-Up Queries (If Needed)

### If Primary Query Returns GPU-Only Models:

```
Find CPU-compatible alternatives to [GPU_MODEL_NAME] for code semantic search.

Requirements:
- Explicitly CPU-only inference
- Distilled or quantized versions acceptable
- Performance within 20% of full model
- Installation via pip or HuggingFace

Include:
- Quantized model versions (e.g., ONNX, INT8)
- Distilled student models
- Smaller architecture variants
```

### If No Code-Specific Models Found:

```
Compare general-purpose embedding models for code semantic search:

Test scenario: 
- Query: "async programming patterns"
- Corpus: Mixed Python and JavaScript files
- Expected: Retrieve files with async/await, Promises, asyncio

Models to compare:
1. General semantic search models (all-MiniLM, BGE)
2. Instruction-tuned embeddings (e5, instructor)
3. Multi-task embeddings (nomic-embed)

Provide:
- Performance on code vs. natural language text
- Transfer learning capability (trained on text, used for code)
- Real-world usage examples in code search tools
```

### If Multi-Language Support Unclear:

```
Evaluate language-specific vs. multilingual embedding models for code:

Scenario: Support Python AND JavaScript in single RAG system

Options:
A) Single multilingual model (e.g., polyglot embeddings)
B) Separate models per language (Python-specific + JS-specific)
C) General model with language hints in queries

Compare:
- Accuracy: Cross-language query accuracy
- Complexity: System architecture differences
- Performance: Speed/memory trade-offs
- Maintenance: Updating embeddings for new languages

Recommend best approach with justification.
```

---

## Evaluation Checklist

After receiving research results, verify:

- [ ] At least 3 models identified
- [ ] All models have exact installation commands
- [ ] CPU-only inference confirmed (not just "can run on CPU with slowdown")
- [ ] Model size <1GB (or justified if larger)
- [ ] Usage examples provided (not just model names)
- [ ] Benchmark data available (even if informal)
- [ ] Models are actively maintained (check GitHub/HF last update)
- [ ] License is compatible (MIT, Apache 2.0, or similar)

---

## Using Research Results

1. **Select top 3 models** based on:
   - Best benchmark performance (if available)
   - Smallest size (for speed)
   - Most recent updates (for improved architectures)

2. **Update `test_embeddings.py`:**
   ```python
   models_to_test = [
       "sentence-transformers/all-MiniLM-L6-v2",  # Baseline
       "model-from-research-1",
       "model-from-research-2",
   ]
   ```

3. **Update `requirements.txt`** if needed:
   ```
   # If models require additional libraries
   transformers>=4.30.0
   nomic>=1.0.0
   ```

4. **Document model selection** in `docs/DECISIONS.md`:
   ```markdown
   ## Phase 1: Model Selection
   
   Selected models:
   1. [Model Name] - [Reason]
   2. [Model Name] - [Reason]
   3. [Model Name] - [Reason]
   
   Research date: YYYY-MM-DD
   Research source: [Link or query used]
   ```

---

## Expected Timeline

- **Research query execution:** 30-60 minutes (automated)
- **Review & selection:** 30 minutes
- **Installation testing:** 30 minutes
- **Update scripts:** 15 minutes

**Total:** 2-3 hours before starting Phase 1 tests

---

## Fallback Plan

If research returns no suitable models:

1. **Start with baseline:**
   ```python
   models_to_test = [
       "sentence-transformers/all-MiniLM-L6-v2",
   ]
   ```

2. **Run Phase 1 tests** with baseline only

3. **If baseline achieves ≥50% P@5:**
   - Conditional GO
   - Research can continue in parallel with Phase 2

4. **If baseline <50% P@5:**
   - NO-GO decision confirmed
   - Stronger research emphasis or project pivot

---

## Notes

- **Don't skip research** - choosing wrong models wastes 6+ hours
- **Prioritize proven models** - avoid experimental architectures
- **CPU requirement is non-negotiable** - GPU models break local-first goal
- **Size matters** - 5GB models won't download quickly or run smoothly
- **Recent is better** - 2024-2025 models use improved architectures

---

Ready to research? Copy the Primary Research Query and run it through:
- Gemini Deep Research
- ChatGPT with browsing
- Claude with web search
- Manual search of Hugging Face Model Hub + Papers with Code

Document findings before proceeding to Phase 1 testing.
