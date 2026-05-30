# a0_meta_supervisor

Read-only cross-project supervisor for Agent Zero. Provides four tools and an
agent profile that together give you situational awareness across every project
under `/a0/usr/projects/` without impersonating any project agent or leaking
secrets.

## Status

MVP — stateless, read-only. See `FUTURE.md` for deferred scope (Act Mode via
`a0_superordinates`, WebUI sidebar panel, SharedBrain integration, summary cache).

## Install

1. Copy this directory into `/a0/usr/plugins/a0_meta_supervisor/` (already there if
   you cloned in place).
2. Ensure `.toggle-1` is present (presence-toggle the plugin to "on").
3. Restart the Agent Zero framework.
4. In the chat UI, create a new chat and pick the `meta_supervisor` agent profile.

## Tools

| Tool | What it does |
|---|---|
| `meta_status` | Overview of all projects (id, title, memory mode, chat count, last activity) |
| `meta_search_files` | Filename glob/substring across all projects |
| `meta_search_content` | Grep file contents across all projects (uses ripgrep if available) |
| `meta_chat_summary` | Chats grouped by their linked project; surfaces orphans |

All four tools are stateless. They scan the filesystem on every call.

## Boundaries (enforced in code, not just prompt)

- `secrets.env` — never read.
- `memory/` — never read.
- `.a0proj/` contents other than `project.json` — never read.
- Files > 5 MB — skipped.
- Binary patterns (`*.png`, `*.zip`, `*.db`, ...) — skipped.

## Run the tests

From the repo root:

```bash
pytest usr/plugins/a0_meta_supervisor/tests/ -v
```

All tests use temporary fixtures — they do not touch live `usr/projects/`.

## Smoke test inside Agent Zero

After restart, create a chat with profile `meta_supervisor` and ask:

- "מה מצב הפרויקטים?" → expect `meta_status` output covering every project under `usr/projects/`.
- "find schema in any file" → expect `meta_search_files` results.
- "find PostgreSQL in markdown" → expect `meta_search_content` results.
- "show chats of smart_routing_system" → expect `meta_chat_summary` with the linked chats and any orphans.

## Comparison with a0_superordinates

This plugin is the **horizontal** complement to the **vertical** `a0_superordinates`
plugin. Both can be installed together — they do not overlap.

| | `a0_superordinates` | `a0_meta_supervisor` |
|---|---|---|
| Axis | Vertical (parent ↔ child) | Horizontal (cross-project) |
| Direction | Spawns new agents | Reads existing state |
| State | Persistent via context.data | Stateless |
| Writes | Yes — creates chats | No — read-only |

If you want the meta supervisor to also *act* inside a project, install
`a0_superordinates` and see `FUTURE.md` for the planned integration.
