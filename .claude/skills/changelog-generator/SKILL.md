---
name: changelog-generator
description: Generate or update CHANGELOG.md from git commit history for a named release. Use when the user says "generate changelog", "write the changelog for vX.Y.Z", "document this release", or any time a version is being cut and the history needs summarising. Assumes commits follow the commit-message skill (Conventional Commits format). Always runs secret-scanner first as a precondition.
---

# Changelog Generator

Announce at the start: "I'm using the changelog-generator skill."

Commits in this repo follow the `commit-message` skill — Conventional Commits format with well-formed types, optional scopes, and breaking changes marked via both `!` and `BREAKING CHANGE:` footer. You can rely on this structure; no need to defensively handle malformed subjects.

---

## Precondition — Secret Scan

Before touching git history, run the `secret-scanner` skill on staged changes:

```bash
git diff --cached
```

Pass the staged diff to the `secret-scanner` skill. If it reports any CRITICAL or HIGH findings, **stop**. Tell the user:

> "Secret-scanner found issues in staged changes. Resolve these before generating the changelog — a release should never include committed secrets."

Only proceed when the scan is clean (or there are no staged changes).

---

## Step 1 — Gather Inputs

You need two things from the user: a **version name** and a **commit range**.

### Version name
Ask if not provided. Examples: `v2.1.0`, `1.4.0`, `2026-06-release`.

### Commit range
Try in order:

1. **Explicit range from user** — use it directly (`abc123..HEAD`, `v2.0.0..HEAD`)
2. **Last git tag** — if the user didn't provide a range, check:
   ```bash
   git describe --tags --abbrev=0
   ```
   If a tag exists, use `<last-tag>..HEAD`.
3. **Full history** — if no tags exist, use `HEAD`.

Tell the user which range you're using before continuing.

---

## Step 2 — Collect Commits

Run two queries against the range in parallel:

~~~bash
# Use record/field separators so multi-line commit bodies remain parseable.
# Record separator: 0x1e, field separator: 0x1f
git log "$RANGE" --merges --pretty=format:"%s%x1f%H%x1e"

git log "$RANGE" --no-merges --pretty=format:"%s%x1f%B%x1f%H%x1e"
~~~

Each non-merge record: `subject␟body␟hash␞` (US=0x1f, RS=0x1e)
- `subject` → conventional commit header (e.g. `feat(auth): add OAuth2`)
- `body` → full commit body; may contain `BREAKING CHANGE:` and newlines
- `hash` → full SHA for traceability

---

## Step 3 — Fetch PR Descriptions (optional)

This step only runs if `GITHUB_TOKEN` is set in the environment. If not, skip to Step 4 in commit-only mode.

### Why
Merge commit messages carry almost no information (`Merge pull request #42 from feature/auth`). The PR description, written using the `pr-description` skill, contains the human-readable summary, motivation, and any breaking changes that is required to be documented before approving.

### Extract PR numbers
For each merge commit subject, extract the PR number:
```
"Merge pull request #42 from feature/auth"  →  PR #42
```
Pattern: `#(\d+)`. If a merge commit doesn't match, skip it silently.

### Get repo owner/name
```bash
git remote get-url origin
```
Parse both HTTPS (`https://github.com/owner/repo.git`) and SSH (`git@github.com:owner/repo.git`) formats.

### Fetch each PR description
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
```
Extract the `body` field. If the call fails or returns empty, skip that PR and fall back to its merge commit subject.

### Map PR description sections to changelog sections
PR descriptions produced by the `pr-description` skill use structured sections. Map them:

| PR description section | Changelog section |
|---|---|
| Summary / Overview | Entry text |
| Breaking Changes | ### Breaking Changes |
| What Changed | ### Added / Fixed / Changed (infer from content) |

If the body doesn't follow this structure (written manually), use the first non-empty paragraph as the entry text.

### Deduplication
When PR mode is active, commits inside a merged PR should **not** appear as separate entries — they are already captured by the PR description. Find them with:

```bash
git log <base-sha>...<merge-sha> --no-merges --pretty=format:"%H"
```

Collect these SHAs into an exclusion set. In Step 4, skip any non-merge commit whose hash is in this set. Commits pushed directly to main (no PR) are not in the exclusion set and should still appear individually.

---

## Step 4 — Classify and Write Entries

### Commit classification (Conventional Commits)

| Type | Section |
|---|---|
| `feat` | ### Added |
| `fix` | ### Fixed |
| `refactor`, `perf` | ### Changed |
| `docs` | ### Documentation |
| `test`, `chore`, `build`, `ci`, `style` | *(skip — not user-facing)* |
| Subject contains `!` or body contains `BREAKING CHANGE:` | ### Breaking Changes |

For breaking changes: if the body has `BREAKING CHANGE: <text>`, use that text as the entry — it explains the migration. If only `!` is present with no body, use the subject description and note it is breaking.

### Entry text
Rewrite commit subjects into user-facing language:
- `feat(auth): add OAuth2 support` → `Add OAuth2 authentication support (auth)`
- `fix(api): handle null ptr in getUser` → `Fix crash when user lookup returns null`

Include the scope in parentheses where it helps readers orient; omit it if it adds noise.

### Omit empty sections
Only write sections that have at least one entry.

---

## Step 5 — Write CHANGELOG.md

```markdown
## [VERSION] - YYYY-MM-DD

### Breaking Changes
- <description>

### Added
- <description> (#42)

### Fixed
- <description>

### Changed
- <description>

### Documentation
- <description>
```

Where a PR number is known, append it to the entry (`(#42)`).

Use today's date:
- Bash: `date +%Y-%m-%d`
- PowerShell: `Get-Date -Format yyyy-MM-dd`

### Updating the file
- **CHANGELOG.md exists** → prepend the new block immediately after the `# Changelog` header. Keep all existing entries intact.
- **CHANGELOG.md does not exist** → create it:

```markdown
# Changelog

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [VERSION] - YYYY-MM-DD
...
```

Newest version always goes at the top.

---

## Breaking Change Convention (enforced by code-review skill)

The `code-review` skill uses three severity levels:

| Severity | Verdict | Effect |
|---|---|---|
| `blocking` | "Block merge until fixed" | PR cannot be merged |
| `suggestion` | "Safe to merge after suggestion" | PR can merge |
| `nit` | "Safe to merge" | PR can merge |

When code-review skill identifies a breaking change, they raise it as **blocking**. The verdict is "Block merge until fixed" — the PR is held until the commit footer is updated (`BREAKING CHANGE:`) or the PR description is updated with the breaking change details.

**This means:** any commit that reaches main has already passed code-review's gate. If a breaking change exists, it is documented either in the commit footer or the PR description before the merge happened. The changelog reads from those sources — it does not need to fetch review comments.

---

## Quick Reference

| Situation | Range |
|---|---|
| Since last tag | `$(git describe --tags --abbrev=0)..HEAD` |
| Between two tags | `v1.0.0..v1.1.0` |
| Full history (no tags) | `HEAD` |
| Explicit SHAs | `abc123..def456` |

| Mode | When |
|---|---|
| PR-first (rich) | `GITHUB_TOKEN` is set |
| Commit-only (fallback) | No token, or API call fails |

## Common Mistakes

**Listing commits that are inside a merged PR**
Use the exclusion set from Step 3 to avoid double-counting.

**Copying commit subjects verbatim**
`fix(api): handle null ptr` → rewrite as `Fix crash when user lookup returns null`.

**Putting the new block at the bottom**
Newest version always goes at the top, below the file header.

**Including chore/test/ci commits**
Not user-facing. Skip them.

**Missing breaking changes buried in commit bodies**
Always scan the full `body` field for `BREAKING CHANGE:`, not just the subject line.
