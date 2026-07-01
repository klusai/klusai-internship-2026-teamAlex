# CLAUDE.md — Sample Project

This file is the **project-level** memory for this sample repo. Claude Code loads
it automatically. Anything written here applies to every session opened in this
directory.

## Conventions

- **Indentation: use tabs, not spaces.** This applies to every language in the repo.
- Keep functions small and single-purpose.
- Prefer explicit names over abbreviations.

## TODO precedence

- In this case, project-scope (current file) beats user-scope (from .claude/CLAUDE.md)

## Path-specific rules

Two rule files live under `.claude/rules/`. They scope to subtrees via their
`appliesTo` frontmatter and add constraints on top of these conventions:

- `frontend/**` — see `.claude/rules/frontend.md`
- `backend/**` — see `.claude/rules/backend.md`
