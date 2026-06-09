# DOX contract - a0_meta_supervisor/helpers

## Purpose

Privacy-safe project discovery, path security, content search, and chat scan
helpers.

## Ownership

- `security.py` owns excluded paths, file-size limits, and safety checks.
- Tools must route filesystem access through helpers.

## Local Contracts

- Do not weaken privacy exclusions without a test and explicit rationale.
- Keep observe mode read-only.

## Work Guidance

- Preserve the same privacy decisions if transport changes to API/MCP later.

## Verification

- Run focused tests under `tests/` for helper changes.
- Run `python -m py_compile` on touched helper files.

## Child DOX Index

No child AGENTS.md files yet.
