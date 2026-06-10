# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

Internal engineering training programme run by KlusAI (2026 cohort). The repo is a shared workspace where participants commit code and exercises produced during the programme.

## Folder structure

Work is organised by team and participant:

```
team 1 (Alex)/     — Team 1, coordinated by Alex Ghiurau
team 2 (Jonathan)/ — Team 2, coordinated by Jonathan Necea
seniors/           — Senior engineers (Paul Ivan, Stefan Farcas, Eduard Pauliuc, Cosmin Bucur)
extras/            — Additional participants (Antonio Neculaescu, David Doroga)
```

Each named subfolder belongs to one participant. Code, notebooks, and exercises go inside the relevant person's folder. Participants should not modify folders that belong to others.

## Skills

Project skills live in `.claude/skills/<name>/SKILL.md` and are shared with everyone who clones the repo.

- `secret-scanner` — scans a file, a glob, or a git diff for hardcoded secrets (API keys, credentials, tokens, private keys, connection strings) before commit. Defaults to staged changes; pass a path, `--diff`, or `--all` to widen scope. Detection patterns live in `.claude/skills/secret-scanner/patterns.md`.

## Key .gitignore rules

`.gitignore` covers Python, Node/TypeScript, and Jupyter artefacts. A few intentional exclusions worth noting:

- `private/`, `local/`, `scratch/` directories and `*.local` files are always ignored — use these for throwaway work that should never be committed.
- `.env.*` files are ignored except `.env.example` — commit only example env files.
- `.claude/local/` and `.claude/state/` are ignored; `.claude/settings.local.json` is not (project-level MCP server config lives there).
