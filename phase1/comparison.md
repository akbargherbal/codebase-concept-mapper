
## Model Comparison

| Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Decision |
|-------|-----|-----|-----|-----------|----------|----------|
| BAAI/bge-small-en-v1.5 | 48.0% | 35.0% | 0.571 | 45.0% | 5.2 | ❌ NO-GO |
| nomic-ai/nomic-embed-text-v1.5 | 38.0% | 45.0% | 0.600 | 25.0% | 129.1 | ❌ NO-GO |
| nomic-ai/CodeRankEmbed | 31.0% | 35.0% | 0.510 | 15.0% | 214.4 | ❌ NO-GO |

### Recommendation

**❌ STOP PROJECT** - Embedding approach not viable

- Best model: `BAAI/bge-small-en-v1.5` at 48.0% P@5
- Threshold: ≥50% for conditional proceed
- Recommendation: Consider alternative approaches or wait for better models
