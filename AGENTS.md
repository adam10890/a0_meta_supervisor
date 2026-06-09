# DOX contract — a0_meta_supervisor

## Purpose

Read-only cross-project supervisor for Agent Zero. It gives a meta agent
operational awareness across `/a0/usr/projects/` while enforcing privacy
boundaries in code.

## Ownership

- Current state is MVP observe mode: stateless and read-only.
- Future act mode depends on a separate act mechanism; do not assume
  `a0_superordinates` exists in this install without checking.
- The file-level privacy boundary is a product asset and must be preserved.

## Local Contracts

- `helpers/security.py` owns path safety, excluded dirs/files, and file-size
  limits.
- `helpers/project_scanner.py` owns project discovery.
- `helpers/search.py` owns safe content search behavior.
- `helpers/chat_scanner.py` owns chat/project grouping.
- `tools/meta_*` wrappers must route filesystem reads through safe helpers.
- The supervisor must not read secrets, project memory, or `.a0proj/` internals
  except allowed `project.json`.

## Work Guidance

- Keep observe work separate from act/container orchestration work.
- For container-per-branch evolution, change transport from local filesystem
  scan to cross-container API/MCP while preserving the same privacy decisions.
- Do not add Docker daemon control directly to this plugin without a hardened
  lifecycle-manager boundary.

## Verification

- Run `pytest usr/plugins/a0_meta_supervisor/tests/ -v` from the
  `agent-zero-2` root when changing behavior.
- At minimum, compile touched Python files.
- Add or update tests for every privacy-rule change.

## Child DOX Index

- `helpers/AGENTS.md` — path safety, project discovery, search, and chat scan
  helpers.
- `tools/AGENTS.md` — read-only `meta_*` Agent Zero tools.
- `tests/AGENTS.md` — privacy and helper behavior tests.
- `prompts/AGENTS.md` — agent-facing tool prompt guidance.
