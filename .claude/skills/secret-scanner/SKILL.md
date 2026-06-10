---
name: secret-scanner
description: Scan a file, a set of files, or a git diff for hardcoded secrets — API keys, credentials, tokens, private keys, connection strings, and other sensitive data — before they get committed. Use when the user asks to check for leaked/hardcoded secrets, run a pre-commit secret scan, review staged changes for credentials, or verify a file contains no sensitive data.
argument-hint: [file-or-glob | --staged | --diff]
allowed-tools: Bash(git diff:*), Bash(git status:*), Bash(git ls-files:*), Bash(rg:*), Bash(grep:*), Read, Grep
---

# Secret scanner

Detect credentials, API keys, tokens, private keys, and other sensitive information that may have been hardcoded accidentally — **before** they are committed.

The goal is high signal: report real leaks with enough context to act, and explicitly down-rank placeholders, examples, and test fixtures so the user isn't drowned in false positives.

## What to scan

Pick the target from the argument (`$ARGUMENTS`):

| Argument | Scan target |
|----------|-------------|
| *(empty)* or `--staged` | Staged changes: `git diff --cached` |
| `--diff` | Unstaged working-tree changes: `git diff` |
| `--all` | All tracked files: `git ls-files` |
| a path or glob (e.g. `config.py`, `src/**/*.ts`) | Those specific files |

Default to **staged changes** when no argument is given — this is the pre-commit use case. If there are no staged changes, say so and offer to scan the unstaged diff or the whole tree instead.

When scanning a diff, focus on **added lines** (lines starting with `+`). A secret that was already in the file on a previous commit is a separate (worse) problem worth flagging, but the immediate job is preventing *new* leaks.

## How to scan

1. **Get the target content.** Run the appropriate `git diff` / `git ls-files` command, or `Read` the named files.
2. **Match against the pattern catalogue.** See [patterns.md](patterns.md) for the regexes and what each one means. Use `rg` (ripgrep) where available, falling back to `grep -nE`. Run a broad sweep, then reason about each hit — don't rely on regex alone for the verdict.
3. **Triage each candidate** (see "Reducing false positives" below). Decide: real secret, suspicious, or benign.
4. **Report** in the format below.

Run pattern groups in parallel where you can. Prefer `rg -n` so you get line numbers for `file:line` references.

## Reducing false positives

A regex hit is a *candidate*, not a verdict. Down-rank or drop a candidate when:

- The file is an **example/template**: `.env.example`, `*.sample`, `*.template`, `*.dist`, fixtures, or anything matching the repo's ignored `private/`, `local/`, `scratch/` paths.
- The value is an obvious **placeholder**: `your-api-key-here`, `xxxx`, `changeme`, `<token>`, `example`, `dummy`, `REPLACE_ME`, all-zeros, or repeated single chars.
- It's a **reference, not a value**: reading from `os.environ`, `process.env`, a secrets manager, a config lookup, or interpolation like `${SECRET}` — these are the *correct* pattern, not a leak.
- It's in a **test** with a clearly fake/sample value, or a documented public/sandbox test key (e.g. Stripe's published `sk_test_...` doc examples).
- Low entropy / clearly not a real key (a short English word assigned to `password` in a comment explaining the field).

Conversely, **raise severity** when a high-entropy value sits next to a name like `secret`, `token`, `apikey`, `password`, `private_key`, or when it matches a vendor-specific prefix (those are almost never false positives).

When genuinely unsure, report it as **Suspicious** rather than silently dropping it — let the user judge. False negatives (a missed real secret) are worse than a flagged maybe.

## Report format

Lead with a one-line verdict, then findings highest-severity first.

```
🔴 2 secrets found, 1 suspicious — do not commit

🔴 CRITICAL  AWS secret access key
  team 1 (Alex)/deploy.py:42
  +   aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  → Rotate this key now (assume it is compromised), remove from the file, load
    from the environment, and scrub it from history if already committed.

🔴 CRITICAL  Private key (PEM)
  team 1 (Alex)/id_rsa:1
  → Move to a secrets store; never commit private keys.

🟡 SUSPICIOUS  High-entropy string assigned to `api_token`
  team 1 (Alex)/client.ts:8
  +   const api_token = "8f3b...e21a"
  → Confirm whether this is a real credential; if so, move it to an env var.
```

Severity scale: 🔴 CRITICAL (confirmed/vendor-prefixed secret or private key), 🟠 HIGH (high-entropy value with a secret-y name), 🟡 SUSPICIOUS (uncertain, needs human judgment), ⚪ INFO (down-ranked — placeholder/example, noted for completeness).

If nothing is found, say so plainly: `✅ No secrets detected in <target>.` Note what was scanned and any limits (e.g. binary files skipped).

## Remediation guidance

When a real secret is found, give concrete next steps, not just a flag:

1. **Rotate** the credential — once committed (even locally, even if removed before push), treat it as compromised.
2. **Remove** it from the code; load from an environment variable or secrets manager instead.
3. If already committed, the value persists in git history — scrubbing it requires `git filter-repo` / BFG plus a force-push and coordination with the team.
4. Add the offending path to `.gitignore` if it shouldn't be tracked at all (this repo already ignores `.env.*` except `.env.example`, and `private/`, `local/`, `scratch/`).

Never print a remediation that itself echoes the full secret unnecessarily — truncate long values in the report (show enough to locate it, e.g. first/last 4 chars).

## Notes

- This is a static, best-effort scan — it cannot catch everything (e.g. secrets split across lines, encoded, or in binary blobs). Say so; don't imply a clean result is a guarantee.
- Do not modify files unless the user explicitly asks for the fix to be applied; the default job is to *detect and report*.
