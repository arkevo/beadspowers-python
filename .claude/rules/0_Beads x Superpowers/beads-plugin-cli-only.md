# Beads Plugin Has No MCP Layer

**Section:** Task Management

Confirmed 2026-07-03 by reading the installed plugin's own
`.claude-plugin/plugin.json`: the Claude Code beads plugin registers no
MCP server — only skills, commands, and a `bd prime` hook. There is
nothing for `/mcp` to show; a missing beads entry there is expected, not
a broken connection.

A handful of shipped command skills (`show`, `create`, `close`, `init`,
`ready`, `stats`, `search`, `update`, `workflow`, `version`) contain a
stale line saying "use the beads MCP `<verb>` tool" — that tool doesn't
exist anywhere in this plugin build. It's a packaging bug upstream
(`gastownhall/beads`), not something to debug locally.

**Rule:** when a `beads:*` skill says to use an MCP tool, run the
equivalent `bd <verb> ...` command directly in Bash instead — exactly
what the plugin's other command skills (`list`, `blocked`, `label`,
etc.) already instruct outright. That is the plugin's real, working
design; invoking the skill and then running the `bd` command it names
are the same action, not two competing ones.
