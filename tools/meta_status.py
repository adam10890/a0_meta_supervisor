"""meta_status — cross-project status summary.

Args:
    project: str | None       # filter to one project
    include_files: bool = False
    include_chats: bool = True

Returns Response.message = dict with keys:
    projects: [...]
    orphan_chats: [...]   # only if include_chats=True
"""

import os
from pathlib import Path

try:
    from ..helpers.project_scanner import scan_projects
    from ..helpers.chat_scanner import scan_chats
except ImportError:
    import sys
    _here = os.path.dirname(os.path.abspath(__file__))
    _parent = os.path.dirname(_here)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    from helpers.project_scanner import scan_projects  # type: ignore
    from helpers.chat_scanner import scan_chats  # type: ignore

from python.helpers.tool import Tool, Response

PROJECTS_ROOT = Path("/a0/usr/projects")
CHATS_ROOT = Path("/a0/usr/chats")


class MetaStatusTool(Tool):
    """Cross-project status — what projects exist, where they live, last activity."""

    async def execute(self, **kwargs):
        target = self.args.get("project")
        include_files = bool(self.args.get("include_files", False))
        include_chats = bool(self.args.get("include_chats", True))

        projects = scan_projects(PROJECTS_ROOT)
        if target:
            projects = [p for p in projects if p["id"] == target]

        if include_chats:
            known_ids = {p["id"] for p in scan_projects(PROJECTS_ROOT) if p["status"] == "ok"}
            by_project, orphans, _corrupt = scan_chats(CHATS_ROOT, known_ids)
            for p in projects:
                chats = by_project.get(p["id"], [])
                p["chat_count"] = len(chats)
                last = [c["last_message"] for c in chats if c.get("last_message")]
                p["last_activity"] = max(last) if last else None
        else:
            orphans = []

        if include_files:
            for p in projects:
                if p["status"] != "ok":
                    continue
                p["file_tree"] = _shallow_file_tree(Path(p["path"]))

        return Response(
            message={
                "projects": projects,
                "orphan_chats": orphans if include_chats else [],
            },
            break_loop=False,
        )


def _shallow_file_tree(project_dir: Path, max_files: int = 50):
    """Return top-level files + first-level dirs only. Excludes .a0proj/memory."""
    if not project_dir.exists():
        return []
    items = []
    for child in sorted(project_dir.iterdir()):
        if child.name in {".a0proj", "memory", ".git"}:
            continue
        items.append({"name": child.name, "is_dir": child.is_dir()})
        if len(items) >= max_files:
            break
    return items
