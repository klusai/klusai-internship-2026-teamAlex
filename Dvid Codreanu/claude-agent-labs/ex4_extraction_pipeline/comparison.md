# Batch vs Synchronous — Cost and Throughput Comparison

## Cost

The Message Batches API charges **50% of the standard token price**.

For the six invoices in this exercise, every token (input + output) costs half as
much when submitted via `batch.py` instead of six sequential calls via `extract.py`.

Example with rough numbers:
- Each invoice call ≈ 800 input tokens + 300 output tokens = ~1 100 tokens
- Six calls total ≈ 6 600 tokens
- Sync cost at $0.80 / M input, $4.00 / M output: ~($0.80×4800 + $4.00×1800) / 1e6 ≈ **$0.011**
- Batch cost: half that ≈ **$0.006**

At lab scale the saving is small, but for millions of documents it compounds directly.

## Latency

| Path | Typical wall time |
|------|-------------------|
| `extract.py` × 6 (sequential) | ~6 × 2–5 s = **12–30 seconds** |
| `batch.py` (one batch, 6 items) | **30 seconds to ~1 hour** (SLA up to 24 h) |

Sequential sync latency is predictable and proportional to document count. Batch
latency is non-deterministic: Anthropic queues and processes the whole batch
asynchronously, so six items might finish in under a minute or take much longer
depending on cluster load.

## Retry behaviour

With sync calls you can implement per-document retry inside the same call (the
`extract_one` loop does this). The Batches API processes each request once — if a
document fails schema validation there is no per-item retry; you note it in
`failures` and resubmit a new batch for those items.

## When to choose each

| Use sync (`extract.py`) when... | Use batch (`batch.py`) when... |
|---------------------------------|-------------------------------|
| A user is waiting for the result | Processing is a background job |
| Single document or a handful | Dozens to millions of documents |
| You need per-doc retry in-session | 50% cost saving matters more than latency |
| Interactive pipeline (chat, API) | Overnight ETL or bulk ingestion |

**Rule of thumb:** if the result needs to be ready in under 30 seconds, use sync.
If the job can wait and cost efficiency matters, use the Batches API.
