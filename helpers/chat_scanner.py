"""Walk usr/chats/, read each chat.json, group by data.project.

Returns a tuple:
    (by_project, orphans, corrupt)
    by_project:  dict[str, list[chat_summary_dict]]
    orphans:     list of chats whose data.project does not exist in known_project_ids
    corrupt:     list of chat dirs where chat.json failed to parse

chat_summary_dict fields:
    id, name, agent_profile, created_at, last_message
    (the full `log` is NOT included — too large; tools fetch it separately)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def scan_chats(
    chats_root: Path,
    known_project_ids: Set[str],
) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Scan *chats_root* and group chats by project.

    Args:
        chats_root: Path to the usr/chats/ directory (or any chats tree).
        known_project_ids: Set of project IDs that are currently known/alive.
            Chats referencing a project ID not in this set are considered orphans.

    Returns:
        A 3-tuple ``(by_project, orphans, corrupt)``:

        * **by_project** – ``dict[project_id, list[chat_summary]]`` for chats
          whose ``data.project`` is in *known_project_ids*.
        * **orphans** – list of chat summaries for chats whose ``data.project``
          is set but not in *known_project_ids*.  Each entry carries an extra
          ``project_referenced`` key with the stale project ID.
        * **corrupt** – list of minimal dicts (``id``, ``status``, ``reason``)
          for chat directories where ``chat.json`` could not be parsed.
    """
    by_project: Dict[str, List[Dict[str, Any]]] = {}
    orphans: List[Dict[str, Any]] = []
    corrupt: List[Dict[str, Any]] = []

    if not chats_root.exists() or not chats_root.is_dir():
        return by_project, orphans, corrupt

    for chat_dir in sorted(chats_root.iterdir()):
        if not chat_dir.is_dir():
            continue
        chat_file = chat_dir / "chat.json"
        if not chat_file.exists():
            continue

        try:
            raw = chat_file.read_text(encoding="utf-8", errors="replace")
            data = json.loads(raw)
        except (json.JSONDecodeError, OSError) as exc:
            corrupt.append({
                "id": chat_dir.name,
                "status": "corrupt",
                "reason": str(exc),
            })
            continue

        project_ref: str | None = (data.get("data") or {}).get("project")
        summary: Dict[str, Any] = {
            "id": data.get("id") or chat_dir.name,
            "name": data.get("name") or "",
            "agent_profile": data.get("agent_profile"),
            "created_at": data.get("created_at"),
            "last_message": data.get("last_message"),
        }

        if not project_ref:
            # Unlinked chat — no data.project; out of scope for this scanner.
            continue

        if project_ref in known_project_ids:
            by_project.setdefault(project_ref, []).append(summary)
        else:
            orphans.append({**summary, "project_referenced": project_ref})

    return by_project, orphans, corrupt
