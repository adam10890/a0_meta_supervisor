from helpers import chat_scanner


def test_groups_chats_by_project(fake_chats_root):
    known_ids = {"demo_valid", "demo_invalid", "demo_no_a0proj"}
    by_project, orphans, corrupt = chat_scanner.scan_chats(
        fake_chats_root, known_project_ids=known_ids
    )
    assert "demo_valid" in by_project
    assert len(by_project["demo_valid"]) == 2
    chat_ids = {c["id"] for c in by_project["demo_valid"]}
    assert chat_ids == {"linked_a", "linked_b"}


def test_surfaces_orphan_chats(fake_chats_root):
    known_ids = {"demo_valid", "demo_invalid", "demo_no_a0proj"}
    _, orphans, _ = chat_scanner.scan_chats(
        fake_chats_root, known_project_ids=known_ids
    )
    assert len(orphans) == 1
    assert orphans[0]["id"] == "orphan"
    assert orphans[0]["project_referenced"] == "deleted_project"


def test_skips_unlinked_chats(fake_chats_root):
    known_ids = {"demo_valid"}
    by_project, orphans, _ = chat_scanner.scan_chats(
        fake_chats_root, known_project_ids=known_ids
    )
    # "unlinked" has no data.project; it should appear in neither
    all_chat_ids = {c["id"] for chats in by_project.values() for c in chats}
    all_chat_ids.update(o["id"] for o in orphans)
    assert "unlinked" not in all_chat_ids


def test_records_corrupt_chats(fake_chats_root):
    _, _, corrupt = chat_scanner.scan_chats(
        fake_chats_root, known_project_ids=set()
    )
    assert len(corrupt) == 1
    assert corrupt[0]["id"] == "corrupt"


def test_chat_summary_has_expected_fields(fake_chats_root):
    by_project, _, _ = chat_scanner.scan_chats(
        fake_chats_root, known_project_ids={"demo_valid"}
    )
    chat = by_project["demo_valid"][0]
    for key in ("id", "name", "agent_profile", "created_at", "last_message"):
        assert key in chat
    # The full log is NOT included by default
    assert "log" not in chat


def test_handles_missing_chats_root(tmp_path):
    missing = tmp_path / "does_not_exist"
    by_project, orphans, corrupt = chat_scanner.scan_chats(
        missing, known_project_ids=set()
    )
    assert by_project == {}
    assert orphans == []
    assert corrupt == []
