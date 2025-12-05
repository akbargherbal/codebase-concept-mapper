To execute **Phase 1 (Google Viability Test)** effectively and avoid wasting time, you need to have your "ingredients" ready before you start cooking.

Here is the checklist of resources, data, and documentation you need to prepare **before** writing the `test_google_rag.py` script.

### 1. 🔑 Accounts & Credentials

You cannot proceed without access to the Gemini API.

- **Google AI Studio Account:** Go to [aistudio.google.com](https://aistudio.google.com/).
- **API Key:** Create a **new** API key specifically for this project.
- **Billing Check:** Ensure you are on the **Free Tier** (Pay-as-you-go is optional but recommended if you hit rate limits).
  - _Note:_ The Free Tier allows 1,500 requests/day, which is plenty for Phase 1 validation.

### 2. 📂 The Data (The "Haystack")

You need the raw code files to upload. Do not use your entire hard drive; use a controlled dataset.

- **Target Repositories:** Clone the specific versions of the libraries you used in your failed Phase 1 (to ensure a fair comparison).
  - `git clone https://github.com/pallets/flask.git`
  - `git clone https://github.com/expressjs/express.git`
- **File Selection:** Isolate the **20 specific files** you used previously, or a small subset (e.g., `src/` folders only).
  - _Preparation:_ Create a folder named `test_corpus/` and copy the relevant `.py` and `.js` files there. **Do not** upload the entire `node_modules` or `.git` folder to Google; it will waste your token limit.

### 3. 🧪 The Test Set (The "Needles")

You need to know exactly what you are looking for to measure success.

- **The List of 20 Concepts:** Have a simple JSON or Python list ready with your queries.
  ```python
  # test_queries.py
  TEST_CASES = [
      {"concept": "Context Managers", "language": "python", "expected_keyword": "__enter__"},
      {"concept": "React useEffect", "language": "javascript", "expected_keyword": "useEffect"},
      # ... rest of your 20 concepts
  ]
  ```
- **The Validators (From Phase 1):** You mentioned you have "keyword-based validators." Locate this code. You will need it to programmatically check if Google's result is a "Hit" or a "Miss."

### 4. 📚 Documentation Bookmarks

Don't search for these while coding. Open these tabs now:

1.  **Official File Search Guide:** [Google Gemini File Search Docs](https://ai.google.dev/gemini-api/docs/file-search)
    - _Look for:_ The code snippet for `media.upload` and `tools=[file_search]`.
2.  **Python SDK Reference:** [google-generativeai PyPI](https://pypi.org/project/google-generativeai/)
    - _Look for:_ How to parse the `grounding_chunks` object. This is the trickiest part.
3.  **Pricing/Limits Page:** [Gemini API Pricing](https://ai.google.dev/pricing)
    - _Keep an eye on:_ "RPM" (Requests Per Minute). The free tier is 15 RPM. You will need to add `time.sleep(4)` in your loop.

### 5. 🛠️ Development Environment

Set up a clean environment so you don't have dependency conflicts.

- **Python 3.10+**
- **Virtual Environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  ```
- **Install SDK:**
  ```bash
  pip install -U google-generativeai python-dotenv
  ```

### 6. 🧠 Mental Prep: The "Ground Truth"

Before you run the script, you must know the answer to **one** question for your top 5 queries:

- _Query:_ "Context Managers" -> _Where is it actually defined in Flask?_
- _Answer:_ You need to know it's in `werkzeug/local.py` (or similar).
- **Why:** If Google returns a file, you need to know _instantly_ if it's right without reading 500 lines of code. Write down the "Correct File Path" for your top 5 queries on a sticky note.

---

### Summary Checklist

- [ ] API Key generated & saved in `.env`.
- [ ] `test_corpus/` folder created with ~20-50 code files.
- [ ] `test_queries.json` created with your 20 concepts.
- [ ] Old Validator code located.
- [ ] Google "File Search" documentation tab open.
- [ ] "Ground Truth" file paths written down for top 5 queries.

Once you have these, you are ready to write `test_google_rag.py`.

---

All URLs have been verified as active and correct. Here is the confirmed list of resources you will need:

### 1. 🔑 Accounts & Access

- **Google AI Studio:** [https://aistudio.google.com/](https://aistudio.google.com/)
  - _Status:_ Active. This is where you generate your API key.
- **Pricing & Limits:** [https://ai.google.dev/pricing](https://ai.google.dev/pricing)
  - _Status:_ Active. Check the "Gemini 1.5 Flash" column for the Free Tier limits (currently 15 RPM).

### 2. 📚 Documentation (Keep these open)

- **Official File Search Guide:** [https://ai.google.dev/gemini-api/docs/file-search](https://ai.google.dev/gemini-api/docs/file-search)
  - _Status:_ Active. This is the "Bible" for this project.
- **Python SDK (Newer Unified SDK):** [https://pypi.org/project/google-genai/](https://pypi.org/project/google-genai/)
  - _Note:_ Google recently released this unified SDK (`pip install google-genai`). It is the preferred way to use File Search now.
- **Python SDK (Legacy):** [https://pypi.org/project/google-generativeai/](https://pypi.org/project/google-generativeai/)
  - _Note:_ This is the older library. If you see tutorials using `import google.generativeai as genai`, they are using this one.

### 3. 📂 Target Repositories (The Data)

- **Flask (Python):** [https://github.com/pallets/flask](https://github.com/pallets/flask)
  - _Status:_ Active.
- **Express (JavaScript):** [https://github.com/expressjs/express](https://github.com/expressjs/express)
  - _Status:_ Active.

### ⚠️ Important SDK Note

Google is currently transitioning between two Python SDKs.

1.  **`google-generativeai`** (Old): Used in most 2024 tutorials.
2.  **`google-genai`** (New, v1.0+): The "Unified" SDK released late 2024.

**Recommendation:** Stick to the **newer `google-genai`** SDK if possible, as the File Search documentation now defaults to it. The code snippets in your plan should be updated to reflect this if they aren't already.
