# MCP Server Evidence — Task 5

## Configuration added

File: `.claude/settings.local.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
```

## How to verify it loaded

Open Claude Code in this directory and run:

```
/mcp
```

Expected output (once the server connects):

```
MCP Servers

● filesystem (connected)
  Tools:
    - read_file
    - read_multiple_files
    - write_file
    - edit_file
    - create_directory
    - list_directory
    - directory_tree
    - move_file
    - search_files
    - get_file_info
    - list_allowed_directories
```

## Why settings.local.json and not settings.json?

`settings.local.json` is gitignored (see `.gitignore` → `.claude/local/` and
`*.local` patterns). MCP server configs often contain local paths or tokens
that should not be committed. `settings.json` would be committed; `settings.local.json`
stays on your machine only.
