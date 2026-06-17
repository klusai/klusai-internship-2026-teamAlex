---
name: pr-description
description: >-
  Generates a complete pull request description from a branch diff plus any
  context the user provides. Use it whenever someone wants to write or improve a
  PR description, prep a PR body, summarize a branch for a pull request, or
  pastes a diff and asks what to write (including short asks like "write the PR"
  or "describe this branch"). Outputs a summary, motivation, what-changed,
  how-to-test, and a breaking-changes section when there is one. Writes the PR
  description only, not commit messages or changelogs.
---

# PR description writer

A diff tells you what changed. A good PR description also covers why, how to
check it, and what might break. The tricky part is the "why", since the diff
doesn't contain it, so pull it from context and commits instead of guessing.

## Steps

1. Get the diff. If the user pasted one, use that. Otherwise pull it from git:

   ```bash
   git diff --stat <base>...HEAD   # overview
   git diff <base>...HEAD          # full diff
   ```

   Base is normally main or master. On big branches, read the --stat output
   first, and keep the raw diff out of the final description.

2. Work out the why. Check the context the user gave you first, then the commit
   messages on the branch (`git log <base>..HEAD`), then any issue numbers in
   the commits or branch name. If none of that explains the reason for the
   change, don't make one up. Use the placeholder under Rules.

3. If the repo has a PR template (`.github/pull_request_template.md`), follow
   that layout instead of the one here.

4. Read through the diff and pull out:
   - what changed, grouped by topic rather than by file
   - anything that breaks compatibility: deleted or renamed public functions,
     changed signatures, removed config keys, flags or env vars, schema or
     migration changes, changed API shapes, changed defaults
   - how someone would test it (the command or steps to confirm it works)
   - whether any user-facing UI changed, since that needs screenshots
   - how big the diff is, so you can flag one that's too large to review well

5. Fill in the template and hand back a markdown block ready to paste.

## Template

```markdown
**Suggested title:** `<type>: <short summary>`

## Summary
One or two sentences on what the PR does.

## Motivation
Why the change is needed.

## What changed
- One bullet per logical change, grouped by topic.

## How to test
- Steps tied to what actually changed.

## Screenshots
(UI changes only. Leave a before/after placeholder, or drop the section.)

## Breaking changes
(Only when something breaks: what it is and how to migrate. Drop it otherwise.)
```

## Rules

Title follows Conventional Commits: feat, fix, refactor, chore, docs, with a
trailing `!` for breaking changes (`feat!:`). One line that says what changed
and why it matters. "fix: stop session cleanup race causing 502s" is useful,
"fix: bug" isn't.

Don't invent a motivation. When nothing explains the why, write this and move on:

```
> _Motivation: needs author input._
```

Keep the summary and the what-changed list from repeating each other. The
summary is the headline, the list is the detail.

Group the changes by topic, not by which files were touched.

Leave out the Screenshots and Breaking changes sections when they don't apply.
For UI work, always add Screenshots with a before/after placeholder.

If the diff is big (somewhere around 400+ changed lines) or covers unrelated
things, add a line at the top saying it might be worth splitting. Still write
the whole description.

Assume the reviewer is new to the project, so spell out internal names and
acronyms instead of relying on them knowing.

Short changes get short descriptions. A one-line fix doesn't need every section.

This writes the PR description and nothing else. Commit messages and changelogs
are separate jobs.

## Examples

Small fix:

```markdown
**Suggested title:** `fix: handle missing timeout in parseConfig`

## Summary
Stop parseConfig from crashing at startup when the config has no timeout key.

## How to test
Start with a config that has no timeout field and confirm it boots using the default.
```

Feature, where the commit mentions issue #214:

```markdown
**Suggested title:** `feat: add user data export endpoint`

## Summary
Adds GET /users/{id}/export, which returns a user's data as JSON.

## Motivation
Closes #214. Users need a way to download their own data ahead of the privacy
compliance work.

## What changed
- New GET /users/{id}/export route and handler returning the user's records.
- Auth check so a user can only export their own data.
- Tests for the success and forbidden cases.

## How to test
curl -H "Authorization: Bearer <token>" localhost:8080/users/42/export returns
200 with the user's JSON; another user's id returns 403. Run pytest
tests/test_export.py.
```
