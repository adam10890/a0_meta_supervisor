"""meta_chat_summary — group chats by project; surface orphans.

Args:
    project: str | None      # default null = all projects
    limit: int = 10          # per project
    include_text: bool = False  # if True, attach first_line and last_line of log
"""

import json
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
DEFAULT_LIMIT = 10
INCLUDE_TEXT_MAX_CHARS = 500


class MetaChatSummaryTool(Tool):
    """Summarize chats per project + orphans."""

    async def execute(self, **kwargs):
        target = self.args.get("project")
        limit = int(self.args.get("limit") or DEFAULT_LIMIT)
        include_text = bool(self.args.get("include_text", False))

        known_ids = {p["id"] for p in scan_projects(PROJECTS_ROOT) if p["status"] == "ok"}
        by_project, orphans, corrupt = scan_chats(CHATS_ROOT, known_ids)

        if target:
            by_project = {target: by_project.get(target, [])}
            orphans = []

        # Sort each project's chats by last_message desc and cap to limit
        for pid in list(by_project.keys()):
            chats = by_project[pid]
            chats.sort(key=lambda c: c.get("last_message") or "", reverse=True)
            by_project[pid] = chats[:limit]
            if include_text:
                for c in chats[:limit]:
                    _attach_log_preview(c)

        return Response(
            message={
                "by_project": by_project,
                "orphan_chats": orphans,
                "corrupt_chats": corrupt,
            },
            break_loop=False,
        )


def _attach_log_preview(chat_summary: dict):
    """Read chat.json again to extract first and last log entry as short text."""
    chat_file = CHATS_ROOT / chat_summary["id"] / "chat.json"
    if not chat_file.exists():
        return
    try:
        data = json.loads(chat_file.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return
    log = data.get("log") or []
    chat_summary["log_length"] = len(log)
    if not log:
        return
    chat_summary["first_line"] = _shorten(_log_entry_text(log[0]))
    chat_summary["last_line"] = _shorten(_log_entry_text(log[-1]))


def _log_entry_text(entry) -> str:
    if isinstance(entry, dict):
        for key in ("content", "text", "message", "heading"):
            if key in entry and isinstance(entry[key], str):
                return entry[key]
        return json.dumps(entry)[:INCLUDE_TEXT_MAX_CHARS]
    return str(entry)


def _shorten(s: str) -> str:
    s = s.strip()
    return s[:INCLUDE_TEXT_MAX_CHARS]
