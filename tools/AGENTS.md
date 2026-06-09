# DOX contract - a0_meta_supervisor/tools

## Purpose

Read-only `meta_*` tools exposed to Agent Zero.

## Ownership

- Tools own argument parsing and agent response shape.
- Filesystem reads must route through safe helpers.

## Local Contracts

- Do not add write/delete/execute actions in observe-mode tools.
- Do not expose secrets, memory, or `.a0proj/` internals beyond allowed
  metadata.

## Work Guidance

- Keep tool outputs compact and source-attributed.

## Verification

- Run `pytest usr/plugins/a0_meta_supervisor/tests/ -v` from `agent-zero-2`
  when behavior changes.
- Run `python -m py_compile` on touched tool files.

## Child DOX Index

No child AGENTS.md files yet.
