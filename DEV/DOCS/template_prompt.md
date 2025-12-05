Generate a JSON taxonomy for **{target}** following this exact schema:

```json
{
  "version": "1.0",
  "taxonomy_name": "Descriptive name",
  "concepts": [
    {
      "name": "Concept Name",
      "description": "Clear explanation (1-2 sentences).",
      "keywords": ["search", "terms"],
      "languages": ["applicable_languages"],
      "category": "snake_case_category"
    }
  ]
}
```

**Requirements:**
- 12-20 core concepts covering fundamental to intermediate features
- `name` + `description` are REQUIRED for each concept
- `keywords`: 3-6 relevant search terms per concept
- `category`: Group related concepts (3-8 per category)
- Descriptions: Concise (under 150 chars), focus on purpose

**Categories**: Use snake_case like `language_feature`, `async_programming`, `web_framework`, `orm_features`

**Output ONLY valid JSON** (no code blocks, no explanatory text).