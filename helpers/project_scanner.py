"""Scan usr/projects/, parse each project.json, return a list of dicts.

Returned dict shape (per project):
    {
        "id":           str,    # directory name
        "status":       "ok" | "invalid",
        "reason":       str,    # only present when status != "ok"
        "title":        str,
        "description":  str,    # truncated to 200 chars
        "memory_mode":  "own" | "shared" | None,
        "git_url":      str | None,
        "path":         str,    # absolute project dir
    }

Deliberately omitted: `instructions` (full system prompt — out of scope for
the meta supervisor; leaking it would let the LLM impersonate project agents).
"""

import json
from pathlib import Path
from typing import Any, Dict, List

MAX_DESCRIPTION_CHARS = 200


def scan_projects(projects_root: Path) -> List[Dict[str, Any]]:
    """Walk projects_root and return a list of project dicts.

    Returns an empty list if the root does not exist or is not a directory.
    Entries are sorted by directory name for deterministic output.
    """
    if not projects_root.exists() or not projects_root.is_dir():
        return []

    results = []
    for project_dir in sorted(projects_root.iterdir()):
        if not project_dir.is_dir():
            continue
        results.append(_scan_one(project_dir))
    return results


def _scan_one(project_dir: Path) -> Dict[str, Any]:
    """Scan a single project directory and return a status dict."""
    project_id = project_dir.name
    a0proj = project_dir / ".a0proj"
    project_json = a0proj / "project.json"

    if not project_json.exists():
        return {
            "id": project_id,
            "status": "invalid",
            "reason": "missing .a0proj/project.json",
            "path": str(project_dir),
        }

    try:
        raw = project_json.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {
            "id": project_id,
            "status": "invalid",
            "reason": f"json error: {exc.msg}",
            "path": str(project_dir),
        }
    except OSError as exc:
        return {
            "id": project_id,
            "status": "invalid",
            "reason": f"read error: {exc}",
            "path": str(project_dir),
        }

    description = (data.get("description") or "")[:MAX_DESCRIPTION_CHARS]

    return {
        "id": project_id,
        "status": "ok",
        "title": data.get("title") or project_id,
        "description": description,
        "memory_mode": data.get("memory"),
        "git_url": data.get("git_url") or None,
        "path": str(project_dir),
    }
