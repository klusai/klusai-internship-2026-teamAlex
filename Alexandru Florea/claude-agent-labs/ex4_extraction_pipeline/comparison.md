# Cost / throughput comparison

## Cost

The Batches API is 50% off, so running all six invoices through `batch.py` costs
about half as much as calling `extract.py` six times. The retry loop in
`extract.py` can also make it a bit more expensive, because a failed attempt
re-sends the whole conversation on the next try.

## Latency

`extract.py` runs the calls one after another, but you get each result right away
(a few seconds each). The batch is the opposite: you submit once and wait for the
whole thing to finish before you get anything. It usually finishes in a few
minutes but can take up to an hour, and there's no retry for items that fail.

## When to use each

- **`extract.py`** — when you have one invoice or need the answer right now (e.g.
  a user is waiting), or you want the retry loop to fix a bad result on the spot.
- **`batch.py`** — when you have a lot of invoices and don't need them quickly,
  like an overnight job, and you mostly care about saving money.

Short version: few and fast → synchronous, lots and patient → batch.
