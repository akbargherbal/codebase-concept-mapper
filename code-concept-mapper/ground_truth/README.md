# Ground Truth Concept Mapper

A robust, AST-based CLI tool for systematically mapping abstract programming concepts to concrete code implementations.

This tool is designed to create high-quality, structured ground-truth datasets, perfect for machine learning, code analysis, and educational projects. It is built to be driven by an AI agent or used manually, with safety features like automatic backups and atomic writes to ensure data integrity.

---

## 🚀 Features

- **AST-Based Precision:** Uses Python's Abstract Syntax Tree (`ast`) module to find the precise start and end lines of classes and functions, eliminating manual guesswork.
- **Taxonomy-Driven:** The workflow is controlled by user-defined JSON "taxonomy" files, ensuring consistency and repeatability across different codebases and audit sessions.
- **Data Integrity:**
  - **Atomic Writes:** Uses a temp-file-and-rename strategy to prevent the state file from becoming corrupted during saves.
  - **Automatic Backups:** Creates a timestamped backup of the state file before every change and automatically rotates the last 5 backups.
  - **Duplicate Detection:** Prevents the same code implementation from being mapped to a concept more than once.
- **Rich Metadata:** The output file is enriched with metadata from the taxonomy, such as keywords, languages, and categories, creating a powerful dataset for downstream analysis.
- **AI-Ready:** Designed with a simple, strict command set that is ideal for being driven by an LLM-based AI agent.

---

## ⚙️ Prerequisites

- Python 3.8+ (required for `end_lineno` support in the `ast` module).

---

## workflow

Using the `concept_mapper` follows a strict, four-step process that ensures consistency and data quality.

### Step 1: Author a Concept Taxonomy

Before you begin, you must define the concepts you want to map. Create a JSON file (e.g., `python_core.json`) that follows the schema defined in the [Input Taxonomy Format](#input-taxonomy-format) section below.

This file is your single source of truth for what the agent will search for.

### Step 2: Initialize the Project

Navigate to your project root and run the `init` command. This creates the main state file (`ground_truth/data/concepts_map.json`) where all mappings will be stored.

```bash
concept_mapper init "flask-audit"
```

### Step 3: Load the Concept Taxonomy

Next, load the concepts from your JSON file into the state. This is a mandatory step before you can begin mapping.

```bash
concept_mapper load-concepts config/taxonomies/python_core.json
```

The tool will read your file, validate it, and populate the state with the concepts you've defined.

### Step 4: Map Implementations

This is the core task. Use the `add` command to link a specific piece of code to a concept you loaded in the previous step.

```bash
concept_mapper add "Decorators" \
    --file "corpus/flask/src/flask/app.py" \
    --identifier "route" \
    --confidence "high" \
    --type "decorator_factory" \
    --evidence "Function is used with @app.route() syntax."
```

### Step 5: Check Progress

At any time, use the `status` command to see a summary of which concepts are loaded and how many implementations have been mapped for each.

```bash
concept_mapper status
```

---

## 📖 Command Reference

#### `init`

Initializes a new project state file.

```bash
concept_mapper init <PROJECT_NAME> [--force]
```

- `<PROJECT_NAME>`: The name of the project being audited (e.g., "flask").
- `--force`: (Optional) Overwrite an existing state file.

#### `load-concepts`

Loads concept definitions from a user-provided JSON taxonomy file.

```bash
concept_mapper load-concepts <PATH_TO_TAXONOMY_JSON>
```

- `<PATH_TO_TAXONOMY_JSON>`: The relative or absolute path to your concepts file.

#### `add`

Maps a code implementation to a pre-loaded concept.

```bash
concept_mapper add <CONCEPT_NAME> --file <FILE_PATH> [options]
```

- `<CONCEPT_NAME>`: The name of the concept (must match a name from the loaded taxonomy).
- `--file <FILE_PATH>`: **(Required)** The path to the source code file.
- `--identifier <NAME>`: The name of the class or function. **This is the preferred method.**
- `--lines <START-END>`: A manual line range (e.g., "45-62"). Use only as a fallback if `--identifier` fails.
- `--confidence <LEVEL>`: **(Required)** Confidence level: `high`, `medium`, or `low`.
- `--type <TYPE>`: **(Required)** A category for the implementation pattern (e.g., "class_definition", "function_decorator").
- `--evidence <TEXT>`: **(Required)** A brief, factual justification for the mapping.

#### `status`

Displays a summary of the current project state.

```bash
concept_mapper status
```

---

## 📥 Input Taxonomy Format

Your concept taxonomy files must be a JSON object with the following structure.

```json
{
  "version": "1.0",
  "taxonomy_name": "Python Core Concepts",
  "concepts": [
    {
      "name": "Context Managers",
      "description": "Classes implementing __enter__ and __exit__ for resource management.",
      "keywords": ["__enter__", "__exit__", "with"],
      "languages": ["python"],
      "category": "language_feature"
    }
  ]
}
```

- `name` (string, **required**): The official display name of the concept.
- `description` (string, **required**): A clear explanation of the concept.
- `keywords` (list of strings, _optional_): Search terms associated with the concept.
- `languages` (list of strings, _optional_): Applicable programming languages.
- `category` (string, _optional_): A grouping category (e.g., "web_framework").

---

## 📤 Output State File Format

The tool generates a `concepts_map.json` file that stores all the collected data in a structured format.

```json
{
  "metadata": {
    "project": "flask-audit",
    "version": "1.1",
    "last_updated": "..."
  },
  "concepts": {
    "context_managers": {
      "display_name": "Context Managers",
      "definition": "Classes implementing __enter__ and __exit__...",
      "keywords": ["__enter__", "__exit__", "with"],
      "languages": ["python"],
      "category": "language_feature",
      "implementations": [
        {
          "file_path": "corpus/flask/src/werkzeug/local.py",
          "identifier": "LocalProxy",
          "line_start": 45,
          "line_end": 62,
          "code_snippet": "class LocalProxy:\\n...",
          "confidence": "high",
          "pattern_type": "class_implementation",
          "evidence": "Defines __enter__ and __exit__ methods.",
          "added_at": "..."
        }
      ]
    }
  }
}
```

---

## ✅ Best Practices

1.  **Always Prefer `--identifier`**: The AST-based lookup is far more accurate and reliable than manually specifying line numbers.
2.  **Write Factual Evidence**: Evidence should be based on observable code features (e.g., "Implements the `__iter__` method"), not subjective opinions (e.g., "Looks like an iterator").
3.  **Verify Before You Map**: Use `cat` or `grep` to read the source code and confirm that a candidate is a true implementation of a concept before running the `add` command.

---

## 🧪 Testing

To run the built-in test suite, navigate to the project root and execute `pytest`.

```bash
pytest --cov=src --cov=ground_truth/tools -v
```
