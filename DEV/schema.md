### The Official Taxonomy JSON Schema

Each taxonomy file must be a JSON object with the following structure:

```json
{
  "version": "1.0",
  "taxonomy_name": "A descriptive name for this set of concepts",
  "concepts": [
    {
      "name": "Concept Name 1",
      "description": "A clear explanation of Concept 1.",
      "keywords": ["list", "of", "search", "terms"],
      "languages": ["list", "of", "applicable", "languages"],
      "category": "a_grouping_category"
    },
    {
      "name": "Concept Name 2",
      "description": "A clear explanation of Concept 2.",
      "keywords": ["another", "list"],
      "languages": ["language"],
      "category": "another_category"
    }
  ]
}
```

---

### Field-by-Field Breakdown

Here is a detailed explanation of each field:

#### **Top-Level Fields**

| Field           | Type              | Status       | Purpose                                                             |
| :-------------- | :---------------- | :----------- | :------------------------------------------------------------------ |
| `version`       | `string`          | **REQUIRED** | The version of your taxonomy file. Use "1.0" to start.              |
| `taxonomy_name` | `string`          | **REQUIRED** | A human-readable name (e.g., "Python Core Concepts", "Django ORM"). |
| `concepts`      | `list of objects` | **REQUIRED** | A list containing all the concept definitions for this taxonomy.    |

---

#### **Fields within each `concepts` object**

| Field         | Type              | Status       | Purpose & Example                                                                                                                                                                                        |
| :------------ | :---------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`        | `string`          | **REQUIRED** | The official display name of the concept. This is what the AI will use in the `add` command. <br> _Example: `"Context Managers"`_                                                                        |
| `description` | `string`          | **REQUIRED** | A clear, concise definition of the concept. This is for human reference and will be stored in the final output. <br> _Example: `"Classes implementing __enter__ and __exit__ for resource management."`_ |
| `keywords`    | `list of strings` | _OPTIONAL_   | A list of keywords associated with the concept. This will be crucial later for validating RAG results. <br> _Example: `["__enter__", "__exit__", "with"]`_                                               |
| `languages`   | `list of strings` | _OPTIONAL_   | A list of programming languages this concept applies to. Useful for filtering and analysis. <br> _Example: `["python"]`_                                                                                 |
| `category`    | `string`          | _OPTIONAL_   | A category for grouping related concepts. Use snake_case. <br> _Example: `"language_feature"`, `"async_programming"`, `"web_framework"`_                                                                 |

---

### Complete Example: `config/taxonomies/python_core.json`

Here is a complete, real-world example that you can use as a direct reference.

```json
{
  "version": "1.0",
  "taxonomy_name": "Python Core Concepts",
  "concepts": [
    {
      "name": "Context Managers",
      "description": "Classes implementing __enter__ and __exit__ for resource management, typically used with a 'with' statement.",
      "keywords": ["__enter__", "__exit__", "contextmanager", "with"],
      "languages": ["python"],
      "category": "language_feature"
    },
    {
      "name": "Decorators",
      "description": "Functions that modify or enhance other functions or methods, using the '@' syntax.",
      "keywords": ["@", "functools.wraps", "wrapper"],
      "languages": ["python"],
      "category": "language_feature"
    },
    {
      "name": "Generators",
      "description": "Functions that use the 'yield' keyword to produce a sequence of values lazily.",
      "keywords": ["yield", "yield from", "generator"],
      "languages": ["python"],
      "category": "language_feature"
    }
  ]
}
```
