# Exercise 2 — Claude Code Configuration: Self-Check

## Task 1: Precedence Hierarchy

From broadest authority to narrowest applicability:

1. Enterprise policy — set by org admins, overrides everything below it
2. Project `CLAUDE.md` — scoped to this repo, overrides user-level defaults
3. User `~/.claude/CLAUDE.md` — personal defaults across all projects
4. Path-specific rules (`.claude/rules/*.md`) — add constraints on top of project conventions within their `appliesTo` subtree only

The governing principle is that narrower scope wins over broader scope. Path-specific rules do not override project conventions globally; they specialize them within a subtree.

## Task 2: Tabs vs. Spaces Conflict

**Tabs apply in this project.** The project-level `CLAUDE.md` is more specific in scope than the user-level `~/.claude/CLAUDE.md` and explicitly states it wins when the two disagree. The user-level preference ("4 spaces") is a global default that yields to any project that overrides it. Outside this repo, the user-level default applies normally.

## Task 3: Path-Specific Rules

`frontend/app.js` was reviewed and the `console.log` on line 2 was flagged as a blocking issue, citing `.claude/rules/frontend.md`. No type-hint complaint was raised.

`backend/service.py` was reviewed and the missing type annotations on `add()` were flagged as a blocking issue, citing `.claude/rules/backend.md`. No console.log complaint was raised.

Each rule fired only inside its own `appliesTo` subtree. Moving a `console.log` into `backend/` would not trigger the frontend rule because path matching is based on file location, not file content.

## Task 4: Skill Frontmatter

Two keys were added to `.claude/skills/generate-endpoint/SKILL.md`:

```
context: fork
allowed-tools: [Read, Write]
```

`context: fork` isolates the skill's execution so it cannot affect the main conversation state. `allowed-tools: [Read, Write]` restricts the skill to file operations only. Bash is excluded. When asked to run `pytest` or `echo hello` within the skill, Claude Code refused both times, explicitly citing that `Bash` is not present in the allowed-tools list.

## Task 5: MCP Server

The filesystem MCP server was registered at project scope:

```
claude mcp add filesystem -s project -- node \
  C:\Users\TUF\AppData\Roaming\npm\node_modules\@modelcontextprotocol\server-filesystem\dist\index.js \
  <project-root>
```

This wrote an entry to `.mcp.json`. On the next session start, `/mcp` showed:

```
Project MCPs (.mcp.json)
  filesystem   connected   14 tools
```

Evidence saved to `mcp-evidence.md` in the project folder.
