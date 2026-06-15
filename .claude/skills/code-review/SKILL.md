---
name: code-review
description: Review a pull request diff and surface issues across logic, security, readability, maintainability, tests, and project patterns. Use this whenever the user asks for a PR review, code review, review of a diff, review comments, or wants to know what problems exist before merging. Output structured feedback with severity levels: blocking, suggestion, and nit.
---

# Code Review

Review a pull request diff and produce structured feedback that helps reviewers triage issues quickly.

The review should focus on correctness, security, readability, maintainability, test coverage, and adherence to the existing project patterns.

## Input

The input may be:

- a git diff
- a pull request diff
- a patch
- a pasted code change
- a plain-English description of changed files
- a request such as "review this PR" or "check this diff"

If a diff is provided, review the actual changed lines and their surrounding context. Do not rely only on file names.

If only a description is provided, review based on the described behavior and clearly state any assumptions.

## Output Format

Always structure the review like this:

```md
## Review Summary

Short 1-3 sentence summary of the overall risk and quality of the change.

## Findings

### Blocking

- [file/path.ext:line] Clear description of the issue.
  Impact: explain why this could break behavior, security, data integrity, or user experience.
  Suggested fix: explain the concrete change needed.

### Suggestions

- [file/path.ext:line] Clear description of the improvement.
  Impact: explain the maintainability, readability, or reliability concern.
  Suggested fix: explain the recommended improvement.

### Nits

- [file/path.ext:line] Small style, naming, wording, or consistency issue.
  Suggested fix: give the small cleanup.

## Tests

Mention what tests are missing, what should be added, or what existing tests should be run.

## Verdict

Use one of:
- Block merge until fixed.
- Safe to merge after suggestions.
- Safe to merge.
```

If there are no issues in a category, write:

```md
No blocking issues found.
```

Do not invent line numbers. If line numbers are unavailable, use the closest available identifier, such as the function name, component name, or changed block.

## Severity Levels

Use exactly these severity levels:

- `blocking` — must be fixed before merge because it can cause incorrect behavior, security issues, data loss, crashes, broken builds, broken tests, or serious regressions.
- `suggestion` — should be considered because it improves maintainability, reliability, readability, performance, or alignment with project patterns, but does not necessarily block merge.
- `nit` — small cleanup related to naming, formatting, comments, wording, or minor consistency.

Do not mark style-only issues as blocking.

Do not mark personal preference as a suggestion unless it connects to project consistency, readability, or maintainability.

## What To Check

### Logic and Correctness

Look for:

- incorrect conditions
- missing edge cases
- off-by-one errors
- null or undefined handling problems
- incorrect async behavior
- race conditions
- incorrect error handling
- broken state updates
- invalid assumptions about input data
- changes that break existing behavior

### Security

Look for:

- leaked secrets, tokens, passwords, or API keys
- unsafe use of user input
- injection risks
- missing authorization or authentication checks
- unsafe file access
- insecure defaults
- exposing sensitive data in logs or responses

Security issues are usually blocking unless the risk is clearly theoretical or unreachable.

### Readability and Maintainability

Look for:

- overly complex logic
- unclear naming
- duplicated code
- dead code
- unnecessary abstractions
- comments that disagree with the code
- code that does not match nearby project style
- changes that make future modifications harder

### Project Patterns

Respect the existing codebase style.

Check whether the change:

- follows existing naming conventions
- uses existing helper functions or utilities
- keeps files in the expected folders
- matches the existing architecture
- avoids unrelated refactors
- avoids changing public behavior accidentally

### Tests

Check whether the change needs tests.

Ask for tests when:

- business logic changed
- bug fixes need regression coverage
- security-sensitive behavior changed
- edge cases were added
- parsing, validation, or data transformation changed
- UI behavior changed in a user-visible way

Do not request excessive tests for tiny documentation or formatting-only changes.

## Review Rules

- Prioritize real bugs and risks over style comments.
- Be specific and actionable.
- Explain the impact of every finding.
- Prefer fewer, stronger findings over many weak comments.
- Do not rewrite the entire solution unless the change is fundamentally flawed.
- Do not approve code that has a blocking issue.
- Do not mention issues that are not visible in the diff unless they are directly implied by the change.
- If the code is good, say so clearly.
- If the diff mixes unrelated changes, mention that it may be better to split the PR.

## Examples

### Example 1 - Blocking logic issue

Input:

```diff
@@ auth.js
- if (user.role === "admin") {
+ if (user.role = "admin") {
    allowAccess();
  }
```

Output:

```md
## Review Summary

The change introduces a blocking authorization bug.

## Findings

### Blocking

- [auth.js] The condition assigns `"admin"` to `user.role` instead of comparing it.
  Impact: this can allow access incorrectly and corrupt the user role value.
  Suggested fix: use a comparison operator, such as `user.role === "admin"`.

### Suggestions

No suggestions found.

### Nits

No nits found.

## Tests

Add or run an authorization test that verifies non-admin users cannot access admin-only behavior.

## Verdict

Block merge until fixed.
```

### Example 2 - Suggestion

Input:

```diff
@@ users.js
+ const result = users.filter(u => u.active === true).map(u => u.email);
```

Output:

```md
## Review Summary

The change is functionally reasonable, with one readability improvement.

## Findings

### Blocking

No blocking issues found.

### Suggestions

- [users.js] The chained expression combines filtering and mapping in one dense line.
  Impact: it is still correct, but it may become harder to read as the logic grows.
  Suggested fix: split the filtering and mapping into named intermediate variables if this logic becomes more complex.

### Nits

No nits found.

## Tests

Run the existing user filtering tests. Add one if active-user email extraction is new behavior.

## Verdict

Safe to merge after suggestions.
```

### Example 3 - Clean review

Input:

```diff
@@ api/health.js
+ export function healthCheck() {
+   return { status: "ok" };
+ }
```

Output:

```md
## Review Summary

The change is small, clear, and low risk.

## Findings

### Blocking

No blocking issues found.

### Suggestions

No suggestions found.

### Nits

No nits found.

## Tests

A simple endpoint or function test would be useful if this health check is part of public API behavior.

## Verdict

Safe to merge.
```