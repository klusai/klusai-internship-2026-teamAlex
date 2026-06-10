---
name: commit-message
description: Generate well-formed commit messages in Conventional Commits format from a git diff or a plain-English description of a change. Use this whenever the user wants a commit message, asks "what should I commit this as," pastes a diff, describes a change they just made, or mentions feat, fix, chore, refactor, or breaking changes. Also use when squashing or combining changes into a single commit message, or preparing a commit before opening a PR. Trigger even if the user just pastes a diff with no explicit instruction.

---

# Commit Message

Generate a well-formed commit message in Conventional Commits format from either a git diff or a plain-English description of a change.


## Format

Every commit message follows this structure:

​```
type(scope): description

[optional body]

[optional footer]
​```

The header (first line) is required. The body and footer are optional.

### Types

Use exactly one type per commit — the most specific one that fits:

- `feat` — introduces a new feature
- `fix` — patches a bug
- `refactor` — restructures code without changing its behavior
- `chore` — maintenance that doesn't touch application logic (dependency bumps, config, tooling)
- `docs` — documentation only
- `test` — adding or correcting tests
- `perf` — a change made to improve performance
- `style` — formatting or whitespace only, no logic change
- `build` / `ci` — build system or CI configuration changes

When more than one type could apply, prefer the one a reader cares about most: a bug fixed in passing during a refactor is still a `fix`.

### Scope

The scope is optional and names the part of the codebase affected (e.g. `auth`, `api`, `parser`). Include it when you can identify it confidently and it adds clarity; omit it rather than guess. Keep it to a short lowercase noun.

### Description

Write the description in the imperative mood — as if finishing the sentence "This commit will ___": `add`, not `added` or `adds`. Keep it lowercase, with no trailing period, and aim for about 50 characters so it stays readable in `git log`.

These rules exist because git history reads as a list of commands, and tooling parses these lines — the consistency is what keeps the history both machine- and human-readable.

## Breaking changes

A breaking change is any change that breaks backward compatibility for people relying on the code — a removed or renamed API, a changed function signature, a renamed config key, a different default. These matter more than ordinary changes because automated versioning treats them as a major version bump.

Mark a breaking change in two ways, and use both:

1. Add a `!` immediately before the colon in the header: `feat(api)!: remove deprecated v1 endpoints`
2. Add a `BREAKING CHANGE:` footer below the body explaining what broke and how to migrate:

​```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: the /v1/* routes are gone. Use /v2/* instead;
see the migration guide for the request shape changes.

## Handling the input

The input is either a git diff or a plain-English description. Detect which by its shape: a diff has `+`/`-` lines, file paths, and `@@` hunk markers; a description is ordinary prose. Handle each as follows.

### From a diff

Read the actual changed lines, not just the file names — the `+` and `-` content tells you what really happened.

- **Infer the type** from the nature of the change: new functions or capabilities point to `feat`; corrected logic points to `fix`; code moved or renamed with identical behavior is `refactor`; dependency, config, or tooling edits are `chore`.
- **Infer the scope** from the area of the codebase the change sits in (a module or directory name), but translate it into a short, meaningful noun — do not paste raw file paths or extensions into the scope.
- **Watch for breaking changes**: removed or renamed public functions, changed signatures, or altered defaults usually mean the change is breaking even if the diff looks small.

### From a description

This is mostly translation — the person has already told you the intent, so map it to the format.

- Pick the type from the wording: "added/built/introduced" leans `feat`; "fixed/corrected/resolved" leans `fix`; "cleaned up/reorganized" leans `refactor`.
- Take the scope from whatever component they name; omit it if they don't make it clear.
- If they describe something that removes or changes existing behavior, treat it as a breaking change even if they don't use that word.

In both modes, the message describes *what the change accomplishes*, not a literal line-by-line account of the edits.

## Decision rules

### Choosing the type when several could apply

A single commit gets a single type. When a cohesive change touches more than one concern, pick the type that matters most to a reader, using this rough priority:

`feat` > `fix` > `perf` > `refactor` > `docs` / `test` / `style` / `chore`

So a feature that includes a small fix is a `feat`; a refactor that also tidies docs is a `refactor`.

### When the change is really several changes

If the diff spans clearly unrelated concerns — for example a new feature in one area and an unrelated dependency bump in another — this is a sign it should be more than one commit. Write a message for the dominant change so the person has something usable, then note that the change looks like it should be split, and suggest the separate commits it would become. Don't silently bundle unrelated work under one label.

### When intent is ambiguous

If you can't tell the type or scope with confidence, choose the most likely option and state the assumption in one short line alongside the message — don't stop to ask a question. The value of this skill is speed, and a labeled assumption the person can correct is more useful than an interruption.

### Scope, restated

Scope is always optional. Include it only when you can name the affected area confidently and it adds clarity; otherwise leave it out. A wrong or vague scope is worse than none.

## Examples

**Example 1 — feature, from a description**
Input: I added a dark mode toggle to the settings page.
Output:
​```
feat(settings): add dark mode toggle
​```

**Example 2 — bug fix with scope, from a description**
Input: Fixed the crash that happened when the user list was empty.
Output:
​```
fix(users): prevent crash on empty user list
​```

**Example 3 — refactor, from a description**
Input: I split the giant payment handler into smaller functions, no behavior change.
Output:
​```
refactor(payments): break payment handler into smaller functions
​```

**Example 4 — chore, from a description**
Input: Bumped the eslint version and updated the config.
Output:
​```
chore: upgrade eslint and update config
​```

**Example 5 — breaking change, from a description**
Input: I removed the old /v1 API endpoints. People need to move to /v2.
Output:
​```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: the /v1/* routes have been removed. Migrate to
the equivalent /v2/* routes.
​```

**Example 6 — fix, from a diff**
Input:
​```
@@ auth/session.py
-    return user.token
+    if user.token.is_expired():
+        user.refresh_token()
+    return user.token
​```
Output:
​```
fix(auth): refresh expired tokens before returning them
​```

**Example 7 — feature, from a diff**
Input:
​```
@@ api/routes.py
+@router.get("/health")
+def health_check():
+    return {"status": "ok"}
​```
Output:
​```
feat(api): add health check endpoint
​```

**Example 8 — multiple concerns in one diff**
Input:
​```
@@ api/routes.py
+@router.get("/health")
+def health_check():
+    return {"status": "ok"}
@@ package.json
-    "lodash": "^4.17.0"
+    "lodash": "^4.17.21"
​```
Output:
​```
feat(api): add health check endpoint
​```
Note: this diff also bumps a dependency, which is unrelated to the
new endpoint. Consider splitting it into a second commit:
`chore(deps): upgrade lodash`.

**Example 9 — ambiguous input**
Input: changed how the parser handles whitespace
Output:
​```
fix(parser): correct whitespace handling
​```
Note: assumed this corrects a bug. If it's a deliberate behavior
change, `feat(parser): change whitespace handling` may fit better.