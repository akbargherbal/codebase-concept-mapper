# Ground Truth System

This directory contains tools for creating and managing ground truth data for concept-to-code mappings. The ground truth data is used to validate and benchmark the RAG system's accuracy.

## Overview

The ground truth system uses an **AST-based CLI tool** to systematically map programming concepts (like "Context Managers" or "Decorators") to their actual implementations in open-source codebases.

### Why Ground Truth?

- **Validation**: Measure system accuracy (Precision@5, Recall, etc.)
- **Benchmarking**: Compare different retrieval approaches
- **Training Data**: Potentially fine-tune models or improve ranking
- **Quality Assurance**: Ensure mapped examples are truly representative

## Directory Structure

```
ground_truth/
├── README.md              # This file
├── tools/                 # CLI tools for mapping
│   ├── cli.py            # Main CLI entry point
│   ├── concept_mapper.py # Core mapping logic
│   └── validator.py      # State validation
├── tests/                # Unit tests
│   └── test_concept_mapper.py
├── data/                 # Generated state files
│   └── concepts_map.json
└── personas/             # AI agent instructions
    └── GEMINI.md         # System prompt for LLM agents
```

## Quick Start

### 1. Initialize a Project

```bash
# From project root
python -m ground_truth.tools.cli init "flask"
```

This creates `concepts_map.json` in the current directory with project metadata.

### 2. Define Concepts

```bash
python -m ground_truth.tools.cli define "Context Managers" \
  --desc "Classes implementing __enter__ and __exit__ methods"
```

### 3. Map Implementations

Using **identifier** (preferred - AST-based):

```bash
python -m ground_truth.tools.cli add "Context Managers" \
  --file "corpus/flask/src/werkzeug/local.py" \
  --identifier "LocalProxy" \
  --confidence "high" \
  --type "class_implementation" \
  --evidence "Defines __enter__ and __exit__ for context management"
```

Using **line ranges** (fallback):

```bash
python -m ground_truth.tools.cli add "Context Managers" \
  --file "corpus/flask/src/werkzeug/local.py" \
  --lines "45-62" \
  --confidence "medium" \
  --type "class_implementation" \
  --evidence "Manual line range for LocalProxy class"
```

### 4. Check Status

```bash
python -m ground_truth.tools.cli status
```

Output:
```
📊 Project: flask
   Last Updated: 2025-12-05T10:30:00
----------------------------------------
   • Context Managers      [3]
   • Decorators           [5]
   • Async/Await          [2]
----------------------------------------
```

## CLI Commands

### `init`

Initialize a new concept map for a project.

```bash
python -m ground_truth.tools.cli init PROJECT_NAME [--force]
```

- `--force`: Overwrite existing state file

### `define`

Define or update a concept.

```bash
python -m ground_truth.tools.cli define CONCEPT_NAME --desc DESCRIPTION [--update]
```

- `--desc`: Brief description of the concept (required)
- `--update`: Allow updating existing concept definition

### `add`

Map a concept to a code implementation.

```bash
python -m ground_truth.tools.cli add CONCEPT_NAME \
  --file FILE_PATH \
  [--identifier CLASS_OR_FUNC] \
  [--lines START-END] \
  --confidence {high|medium|low} \
  --type PATTERN_TYPE \
  --evidence JUSTIFICATION
```

**Required:**
- `--file`: Path to file containing implementation
- `--confidence`: Confidence level (high/medium/low)
- `--type`: Implementation pattern type
- `--evidence`: Specific justification for mapping

**One of:**
- `--identifier`: Class/function name (preferred - uses AST)
- `--lines`: Manual line range "START-END" (fallback)

### `status`

Display summary of current concept map.

```bash
python -m ground_truth.tools.cli status
```

## Features

### ✅ AST-Based Precision

The tool uses Python's `ast` module to automatically locate class and function definitions:

```python
# You provide identifier
--identifier "ContextManager"

# Tool finds exact lines
Lines 45-62 (includes decorators, docstrings, full body)
```

### ✅ Duplicate Detection

Prevents mapping the same code location multiple times:

```
⚠️  Duplicate detected at file.py:45
   Already mapped to concept 'Context Managers'. Skipping.
```

### ✅ Automatic Backups

Creates timestamped backups before each state change:

```
.mapper_backups/
├── concepts_map_20250105_103000.json
├── concepts_map_20250105_104500.json
└── concepts_map_20250105_110000.json
```

Keeps last 5 backups automatically.

### ✅ Atomic Writes

Uses temp file + atomic rename to prevent corruption:

```python
# Write to temp file
concepts_map.json.tmp

# Atomic replace
os.replace(temp, state_file)
```

### ✅ Schema Validation

Validates state file structure on every load:

```json
{
  "metadata": {
    "project": "flask",
    "created_at": "2025-12-05T10:00:00",
    "last_updated": "2025-12-05T10:30:00",
    "version": "1.1"
  },
  "concepts": {
    "context_managers": {
      "display_name": "Context Managers",
      "definition": "Classes implementing __enter__ and __exit__",
      "implementations": [
        {
          "file_path": "corpus/flask/src/werkzeug/local.py",
          "identifier": "LocalProxy",
          "line_start": 45,
          "line_end": 62,
          "code_snippet": "class LocalProxy:\n    def __enter__(self)...",
          "confidence": "high",
          "pattern_type": "class_implementation",
          "evidence": "Defines __enter__ and __exit__",
          "added_at": "2025-12-05T10:15:00"
        }
      ]
    }
  }
}
```

## Best Practices

### 1. Always Use Identifiers First

```bash
# ✅ GOOD: AST finds exact lines
--identifier "ClassName"

# ❌ BAD: Manual counting prone to errors
--lines "45-62"
```

### 2. Write Specific Evidence

```bash
# ✅ GOOD: Observable code features
--evidence "Class defines __enter__ and __exit__ methods"

# ❌ BAD: Vague statements
--evidence "Looks like a context manager"
```

### 3. Verify Before Mapping

```bash
# 1. Find candidates
grep -rn "class.*__enter__" corpus/flask/

# 2. Read the file
cat corpus/flask/src/werkzeug/local.py

# 3. Confirm it's a definition (not usage)
# 4. Then map it
```

### 4. Use Appropriate Confidence Levels

- **High**: Standard implementation, clear pattern, no ambiguity
- **Medium**: Complex logic, multiple responsibilities, non-standard approach
- **Low**: Ambiguous, partial implementation, requires human review

## Workflow for AI Agents

See `personas/GEMINI.md` for complete system prompt. Key points:

1. **Never edit JSON directly** - always use CLI
2. **Prefer --identifier over --lines** - AST is more accurate
3. **Verify file contents first** - never guess
4. **Check for duplicates** - tool prevents but good to know
5. **Use proper shell escaping** - single quotes for strings with spaces

## Testing

Run unit tests:

```bash
cd ground_truth
python -m pytest tests/ -v
```

Or:

```bash
python -m unittest discover -s ground_truth/tests -p "test_*.py"
```

## Integration with Main System

Ground truth data feeds into:

1. **Accuracy Evaluation** (`scripts/evaluate_accuracy.py`)
   - Compares RAG results against ground truth
   - Calculates Precision@K, Recall, F1

2. **Validation** (`phase1_validation/validators/`)
   - Uses concept definitions to validate retrievals
   - Keyword-based post-filtering

3. **Ranking** (`src/business_logic/rankers.py`)
   - Ground truth examples inform quality scoring
   - Can weight by confidence levels

## Recovery from Corruption

If `concepts_map.json` becomes corrupted:

```bash
# Option 1: Restore from backup
cp .mapper_backups/concepts_map_20250105_110000.json concepts_map.json

# Option 2: Fix manually (for JSON syntax errors)
# Edit concepts_map.json to fix the JSON

# Option 3: Start fresh (LAST RESORT)
rm concepts_map.json
python -m ground_truth.tools.cli init "project_name"
```

## FAQ

**Q: Can I edit concepts_map.json directly?**
A: No! Always use the CLI. Direct edits bypass validation and backups.

**Q: What if AST can't find my identifier?**
A: Use `grep -n "def name" file.py` to find lines, then use `--lines START-END`.

**Q: Can I map the same concept to multiple files?**
A: Yes! That's the goal. Map each unique implementation separately.

**Q: What's the difference between identifier and lines?**
A: `--identifier` uses AST for precision. `--lines` is manual fallback.

**Q: How do I delete a mapping?**
A: Currently not supported via CLI. Restore from backup or start fresh.

## Future Enhancements

- [ ] `remove` command to delete specific mappings
- [ ] `update` command to modify existing mappings
- [ ] `export` command to generate training data formats
- [ ] `validate` command to check all file paths still exist
- [ ] `merge` command to combine multiple concept maps
- [ ] Support for JavaScript/TypeScript AST parsing

## Related Documentation

- `personas/GEMINI.md` - AI agent system prompt
- `tests/test_concept_mapper.py` - Usage examples in tests
- `../docs/NEW_CONTEXT.md` - Project overview and goals