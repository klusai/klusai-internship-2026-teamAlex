# Exercise 4 — Task Responses

## Task 1: Retry loop in extract.py

The loop calls the API, extracts the `tool_use` block, and validates its input against `INVOICE_SCHEMA` using `jsonschema.validate`. On `ValidationError`, it appends the assistant turn and a `tool_result` with `is_error: true` containing the error message, then retries up to `MAX_ATTEMPTS = 3`. Running on `inv_03.txt` returned `tax_id: null` and passed validation.

## Task 2: Nullable field across all invoices

| Invoice | tax_id        |
|---------|---------------|
| inv_01  | US-84-2937561 |
| inv_02  | GB123456789   |
| inv_03  | null          |
| inv_04  | 13-7654321    |
| inv_05  | null          |
| inv_06  | 95-1122334    |

inv_03 and inv_05 correctly returned `null`. No fabrication occurred.

## Task 3: Batch extraction

All 6 invoices submitted as a single batch. 6/6 succeeded. Grand total sum: $10,721.49. Invoices with no tax_id: inv_03, inv_05.

## Task 4: Cost and throughput comparison

The Batches API costs 50% less per token than synchronous calls. For 6 invoices the saving is modest; at scale it becomes significant.

Synchronous calls return in seconds. The Batches API can take up to an hour. Use synchronous extraction when a result is needed immediately. Use the Batches API for bulk processing where latency does not matter and cost does.

## Self-check

**Why validate with jsonschema if the tool input_schema already constrains shape?**
The API does not enforce input_schema at runtime. The model can still return wrong types, missing required fields, or extra fields. jsonschema catches these and feeds errors back through the retry loop.

**Why nullable rather than optional?**
Optional allows the field to be silently absent. Nullable forces an explicit `null`, making downstream handling predictable. If required and non-nullable, inv_03 and inv_05 would always fail validation.
