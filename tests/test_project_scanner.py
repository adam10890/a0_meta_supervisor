from helpers import project_scanner


def test_scan_projects_returns_valid_project(fake_projects_root):
    result = project_scanner.scan_projects(fake_projects_root)
    by_id = {p["id"]: p for p in result}

    assert "demo_valid" in by_id
    p = by_id["demo_valid"]
    assert p["title"] == "Demo Valid"
    assert p["status"] == "ok"
    assert p["memory_mode"] == "own"
    assert p["git_url"] == "https://example.com/demo.git"


def test_scan_projects_marks_malformed_json(fake_projects_root):
    result = project_scanner.scan_projects(fake_projects_root)
    by_id = {p["id"]: p for p in result}

    assert "demo_invalid" in by_id
    assert by_id["demo_invalid"]["status"] == "invalid"
    assert "json" in by_id["demo_invalid"]["reason"].lower()


def test_scan_projects_marks_missing_a0proj(fake_projects_root):
    result = project_scanner.scan_projects(fake_projects_root)
    by_id = {p["id"]: p for p in result}

    assert "demo_no_a0proj" in by_id
    assert by_id["demo_no_a0proj"]["status"] == "invalid"
    assert "project.json" in by_id["demo_no_a0proj"]["reason"]


def test_scan_projects_truncates_long_description(fake_projects_root):
    # Add a project with a very long description
    long_desc = "x" * 1000
    long_dir = fake_projects_root / "demo_long"
    (long_dir / ".a0proj").mkdir(parents=True)
    (long_dir / ".a0proj" / "project.json").write_text(
        '{"title":"Long","description":"' + long_desc + '"}',
        encoding="utf-8",
    )
    result = project_scanner.scan_projects(fake_projects_root)
    by_id = {p["id"]: p for p in result}
    assert len(by_id["demo_long"]["description"]) <= 200


def test_scan_projects_never_returns_instructions_field(fake_projects_root):
    # The full system prompt of a project must NOT leak into meta_status
    result = project_scanner.scan_projects(fake_projects_root)
    for p in result:
        assert "instructions" not in p


def test_scan_projects_handles_empty_root(tmp_path):
    empty = tmp_path / "empty_projects"
    empty.mkdir()
    assert project_scanner.scan_projects(empty) == []


def test_scan_projects_handles_missing_root(tmp_path):
    missing = tmp_path / "does_not_exist"
    assert project_scanner.scan_projects(missing) == []
