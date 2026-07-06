# Batch vs Synchronous Extraction — Cost and Throughput Comparison

## Cost

The Message Batches API charges 50% of the standard token price. For 6 invoices,
the synchronous approach makes 6 separate API calls at full price. The batch
submits all 6 in one request and halves the token cost across all of them. The
savings scale linearly — 600 invoices overnight would cost half as much via batch
as 600 sequential synchronous calls.

## Latency

Synchronous calls return in seconds each. Running 6 in sequence takes roughly
6–15 seconds total depending on response size and network.

The Batches API can take up to an hour to process, though small batches often
finish in a few minutes. There is no streaming and no per-item result until the
whole batch ends. The polling loop in `batch.py` checks every 10 seconds, so
there is always some wait even for fast batches.

## When to use each

Use synchronous extraction (`extract.py`) when:
- A user is waiting for the result interactively
- You need the data immediately to drive the next step in a workflow
- You are processing a single document on demand

Use the Batches API (`batch.py`) when:
- You are processing many documents at once and cost matters
- Latency is not a concern (e.g. overnight ETL, end-of-day report ingestion)
- You want to avoid rate-limit pressure from many rapid sequential calls

## Self-check answers

**Why validate with jsonschema when the tool input_schema already constrains shape?**
The input_schema tells the model what shape to produce, but the API does not
reject a tool call whose input violates that schema. The model can still return
wrong types, missing required fields, or extra fields. jsonschema catches these
at runtime and lets the retry loop feed the error back.

**Why is tax_id nullable rather than just optional?**
Optional means the field can be absent entirely. Nullable means it must be
present but can be null. Making it nullable forces the model to explicitly
acknowledge the absence of a tax ID rather than silently omitting the field,
which makes downstream handling predictable — consumers always check
`data["tax_id"] is None` rather than `"tax_id" not in data`. If it were
required (non-nullable), inv_03 and inv_05 would always fail validation unless
the model invented a value.
