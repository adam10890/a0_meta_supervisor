"""Shared pytest fixtures + sys.path setup for the a0_meta_supervisor plugin.

Adds the plugin root to sys.path so tests can import as `from helpers import X`,
matching the runtime import fallback used by Agent Zero tool loader (see
`tools/*.py`).
"""

import json
import sys
from pathlib import Path

import pytest

# Add the plugin root (parent of tests/) to sys.path so `import helpers` works.
_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))


@pytest.fixture
def fake_projects_root(tmp_path):
    """Build a tmp tree with 3 fake projects covering the cases we care about.

    Layout:
      <root>/demo_valid/.a0proj/project.json   (well-formed)
      <root>/demo_valid/notes.md
      <root>/demo_valid/.a0proj/secrets.env    (must NOT be read)
      <root>/demo_valid/memory/private.json    (must NOT be read)
      <root>/demo_invalid/.a0proj/project.json (malformed JSON)
      <root>/demo_no_a0proj/notes.md           (missing .a0proj entirely)
    """
    root = tmp_path / "projects"
    root.mkdir()

    valid = root / "demo_valid"
    (valid / ".a0proj").mkdir(parents=True)
    (valid / ".a0proj" / "project.json").write_text(
        json.dumps({
            "title": "Demo Valid",
            "description": "A clean project for tests.",
            "instructions": "Be useful.",
            "color": "#abcdef",
            "memory": "own",
            "git_url": "https://example.com/demo.git",
        }),
        encoding="utf-8",
    )
    (valid / ".a0proj" / "secrets.env").write_text("API_KEY=DO_NOT_LEAK", encoding="utf-8")
    (valid / "memory").mkdir()
    (valid / "memory" / "private.json").write_text("{\"private\": true}", encoding="utf-8")
    (valid / "notes.md").write_text("# Demo notes\nHello PostgreSQL world", encoding="utf-8")

    invalid = root / "demo_invalid"
    (invalid / ".a0proj").mkdir(parents=True)
    (invalid / ".a0proj" / "project.json").write_text("{ this is not valid JSON ", encoding="utf-8")

    no_a0proj = root / "demo_no_a0proj"
    no_a0proj.mkdir()
    (no_a0proj / "notes.md").write_text("Project without .a0proj", encoding="utf-8")

    return root


@pytest.fixture
def fake_chats_root(tmp_path):
    """Build a tmp tree with chats linked / unlinked / corrupt / orphan."""
    root = tmp_path / "chats"
    root.mkdir()

    def write_chat(chat_id: str, content: dict):
        d = root / chat_id
        d.mkdir()
        (d / "chat.json").write_text(json.dumps(content), encoding="utf-8")

    write_chat("linked_a", {
        "id": "linked_a", "name": "Linked chat A",
        "created_at": "2026-05-01T10:00:00Z",
        "last_message": "2026-05-10T10:00:00Z",
        "agent_profile": "agent0",
        "data": {"project": "demo_valid"},
        "log": [],
    })
    write_chat("linked_b", {
        "id": "linked_b", "name": "Linked chat B",
        "created_at": "2026-05-02T10:00:00Z",
        "last_message": "2026-05-12T10:00:00Z",
        "agent_profile": "agent0",
        "data": {"project": "demo_valid"},
        "log": [],
    })
    write_chat("unlinked", {
        "id": "unlinked", "name": "Unlinked",
        "created_at": "2026-05-03T10:00:00Z",
        "last_message": "2026-05-03T10:00:00Z",
        "agent_profile": "agent0",
        "data": {},
        "log": [],
    })
    write_chat("orphan", {
        "id": "orphan", "name": "Orphan chat",
        "created_at": "2026-05-04T10:00:00Z",
        "last_message": "2026-05-04T10:00:00Z",
        "agent_profile": "agent0",
        "data": {"project": "deleted_project"},
        "log": [],
    })
    corrupt_dir = root / "corrupt"
    corrupt_dir.mkdir()
    (corrupt_dir / "chat.json").write_text("{ broken json", encoding="utf-8")

    return root
