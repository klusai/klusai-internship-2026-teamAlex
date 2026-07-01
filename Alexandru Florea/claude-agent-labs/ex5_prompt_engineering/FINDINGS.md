# Exercise 5 — findings (tasks 2 & 3)

Model: `claude-opus-4-8`. Both scripts run against `big_diff.txt`.

## The three planted issues

| # | Issue | Primary site | Second site |
|---|-------|--------------|-------------|
| 1 | SQL injection | `api/auth.py` `verify_login` — `username` concatenated into `WHERE username = '...'` | `api/orders.py` `search_orders` — f-string `{column} = '{value}'` (column *and* value injectable) |
| 2 | Bare `except` | `api/orders.py` `cancel_order` — `except: pass`, still returns `True` | `api/utils.py` `parse_int` — `except: pass` |
| 3 | Unsalted MD5 | `api/auth.py` `hash_password` — `hashlib.md5(...)` for passwords | `api/utils.py` `api_key_fingerprint` — MD5 over an API key |

Bonus latent bug both techniques surfaced: `api/utils.py` uses `hashlib` but never imports it → `NameError` at call time.

## Task 2 — vague vs. explicit criteria

`CRITERIA` now names SQL injection, bare `except`, weak password hashing, plus secrets/PII
handling and input validation (column allowlisting).

- **Explicit ×3:** found all three planted issues (both sites each) on every run. Output is
  stable and predictable — a criterion-by-criterion table, each verdict cites file + line.
  Easy to diff between runs.
- **Vague ×3:** coverage was actually good here too (the diff is small and the issues are
  blatant), but **what varies is structure and emphasis**: severity buckets differ run to
  run, ordering shifts, and the set of "extra" findings drifts (dashboard.js listener leak,
  forgeable session token, non-constant-time compare appear in some runs and not others).
  You cannot rely on a vague prompt hitting a specific required item — it happens to here
  because the planted issues are loud.

**Takeaway:** explicit criteria buy *consistency and auditability*, not just raw coverage.
The value grows as issues get subtler and the diff gets larger.

## Task 3 — single-pass vs. multi-pass

`split_into_chunks` splits per `diff --git` (5 chunks); synthesis merges, dedupes, and ranks
by severity.

| | Single-pass | Multi-pass |
|---|---|---|
| Planted issues found | All 3 | All 3 |
| Second sites | Caught both MD5 + both bare-except | Caught both MD5 + both bare-except |
| Total findings | ~9, **output truncated at `max_tokens`** (cut off mid-issue #9) | 14, ranked Critical→Informational, deduplicated |
| API calls | 1 | 6 (5 chunk reviews + 1 synthesis) |
| Cost / tokens | ~1× | ~6× (per-file context re-sent + synthesis) |
| Latency | 1 round-trip | 6 sequential round-trips (≈6×; parallelizable — stretch goal) |

**What multi-pass surfaced that single-pass glossed over:** single-pass ran out of output
budget — its report was truncated mid-finding, so the resource/connection issues at the tail
were lost. Multi-pass gives each file its own budget, so nothing gets squeezed out, and the
synthesis step produces a clean severity ranking. Both *detected* the three planted issues;
the difference is multi-pass reports completely and consistently on a long diff.

**When multi-pass is not worth it:** small diffs that fit comfortably in one response, and
latency-sensitive paths (it's ~6× the round-trips here). The win shows up when the diff is
long enough that a single response either truncates or starts skimming.
