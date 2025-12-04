
## Model Comparison

| Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Device | Decision |
|-------|-----|-----|-----|-----------|----------|--------|----------|
| Alibaba-NLP/gte-multilingual-base | 25.0% | 30.0% | 0.458 | 20.0% | 5.7 | cuda | ❌ NO-GO |
| intfloat/multilingual-e5-large-instruct | 23.0% | 15.0% | 0.275 | 15.0% | 3.2 | cuda | ❌ NO-GO |
| Qwen/Qwen3-Embedding-0.6B | 21.0% | 40.0% | 0.500 | 5.0% | 20.5 | cuda | ❌ NO-GO |
| google/embeddinggemma-300m | 7.0% | 5.0% | 0.104 | 5.0% | 8.6 | cuda | ❌ NO-GO |

### Recommendation

**❌ STOP PROJECT** - Embedding approach not viable

- Best model: `Alibaba-NLP/gte-multilingual-base` at 25.0% P@5
- Threshold: ≥50% for conditional proceed
- Recommendation: Consider alternative approaches or wait for better models
