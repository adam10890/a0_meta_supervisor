# FUTURE — Deferred Scope for a0_meta_supervisor

**None of the items below are part of MVP.** MVP does not import, require, or
detect `a0_superordinates`, `llm_wiki`, or any other plugin.

Listed in suggested order of value.

## 1. Act Mode via `a0_superordinates` (first FUTURE phase)

Instead of inventing A2A, declare a soft, optional dependency on the
[`a0_superordinates`](https://github.com/neurocis/a0_superordinates) plugin.
When the user asks the meta supervisor to do work inside a project, the
supervisor calls `superordinate_spawn` with the target project's
`instructions` and a fresh `AgentContext`. The spawned agent runs as a visible
sidebar chat with the project's identity; the supervisor reads results back via
`superordinate_message`. No protocol invention required.

Graceful degradation: if `a0_superordinates` is not installed, the meta supervisor
tells the user to switch chat manually.

### Implementation sketch

Add `tools/meta_delegate.py` that:
1. Looks up the project by id via `project_scanner`.
2. Imports `superordinate_spawn` lazily; if the import fails, returns a friendly
   error message describing the missing dependency.
3. Spawns with the project's `instructions` and `agent_profile`.
4. Returns the new `superordinate_id` plus a short confirmation.

## 2. WebUI sidebar panel

Add `webui/` with an extension hook at `sidebar-chats-list-end` (the hook
`a0_superordinates` already uses) showing a live "Projects Overview" tree:
project name, chat count, last activity, status indicator.

Refresh interval ~5s via an Alpine store; on click, navigate to the most recent
chat of that project.

## 3. SharedBrain integration (exporter to llm_wiki)

Add an optional `tools/meta_export_to_wiki.py` that writes `meta_status` output
to a new wiki named `projects` under `SharedBrain/wikis/`. Requires:
- Registering the wiki in `SharedBrain/registry.yaml`.
- Granting `agent_zero` write access.

Benefits: Claude Code and other agents that read SharedBrain see the project
landscape via the existing `llm_wiki` plugin.

## 4. LLM-generated summaries with mtime-based cache

Per project, generate a one-paragraph summary from recent chats. Cache to
`/a0/usr/plugins/a0_meta_supervisor/data/summaries/` keyed by `(project_id, max(mtime))`.
Invalidate when any file under the project changes mtime.

## 5. Cached registry — only if responsiveness becomes a problem

At >=30 projects or >=1000 chats, consider a SQLite cache under `data/registry.db`.
Tool interfaces unchanged; only helpers change. Sync on `agent_init` extension
hook.

## 6. Cross-installation supervision

For users running multiple Agent Zero installs (e.g., dev + prod containers),
support registering remote installs by URL+auth and merging their `meta_status`
into a single view. Far future.
