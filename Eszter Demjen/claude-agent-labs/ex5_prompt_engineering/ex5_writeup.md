# Exercise 5 — Prompt Engineering

## Task 1: Few-shot classification

Zero-shot scored 17/17 on firm tickets. Few-shot scored the same. The only change was ticket 13 flipping from `question` to `feature` after adding a UX-feedback example — the model learned vague usability complaints belong in `feature`.

Tickets 8, 13, and 19 are ambiguous because they sit on category boundaries: ticket 8 is a performance complaint wrapped around a feature request, ticket 13 is UX frustration with no concrete defect or ask, and ticket 19 uses hedged language that reads as either a bug report or a clarification question.

## Task 2: Explicit review criteria

All three planted issues were found in every run, vague and explicit alike — the diff is too small and the issues too prominent for either prompt to miss them. The difference was structural consistency: vague runs varied in ordering and depth each time; explicit runs produced the same sections, the same order, and a summary table every time. Explicit criteria matter most at scale, not on an obvious diff.

## Task 3: Multi-pass review

Both approaches caught SQL injection, bare `except`, and MD5. Multi-pass additionally found IDOR across all three order functions — single-pass missed it entirely because `orders.py` competed with four other files for attention. Multi-pass also surfaced a `dashboard.js` event listener leak and a missing null check that single-pass skipped.

Multi-pass is not worth it for small diffs, latency-sensitive paths, or quick checks. The overhead — 6 API calls versus 1, roughly 5x slower — only pays off on large diffs where per-file focus changes what the model notices.
