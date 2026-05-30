from pathlib import Path
from helpers import security


def test_excluded_dirs_constants_present():
    assert ".a0proj" in security.EXCLUDED_DIRS
    assert "memory" in security.EXCLUDED_DIRS
    assert ".git" in security.EXCLUDED_DIRS


def test_excluded_file_patterns_present():
    assert "*.pyc" in security.EXCLUDED_FILE_PATTERNS
    assert "*.png" in security.EXCLUDED_FILE_PATTERNS
    assert "*.zip" in security.EXCLUDED_FILE_PATTERNS


def test_is_safe_path_allows_project_json(tmp_path):
    projects_root = tmp_path / "projects"
    p = projects_root / "demo" / ".a0proj" / "project.json"
    p.parent.mkdir(parents=True)
    p.touch()
    assert security.is_safe_path(p, projects_root) is True


def test_is_safe_path_blocks_secrets_env(tmp_path):
    projects_root = tmp_path / "projects"
    p = projects_root / "demo" / ".a0proj" / "secrets.env"
    p.parent.mkdir(parents=True)
    p.touch()
    assert security.is_safe_path(p, projects_root) is False


def test_is_safe_path_blocks_memory_dir(tmp_path):
    projects_root = tmp_path / "projects"
    p = projects_root / "demo" / "memory" / "anything.json"
    p.parent.mkdir(parents=True)
    p.touch()
    assert security.is_safe_path(p, projects_root) is False


def test_is_safe_path_blocks_path_outside_root(tmp_path):
    projects_root = tmp_path / "projects"
    projects_root.mkdir()
    outside = tmp_path / "other" / "file.txt"
    outside.parent.mkdir()
    outside.touch()
    assert security.is_safe_path(outside, projects_root) is False


def test_is_safe_path_blocks_traversal(tmp_path):
    projects_root = tmp_path / "projects"
    projects_root.mkdir()
    sneaky = projects_root / "demo" / ".." / ".." / "secrets.env"
    assert security.is_safe_path(sneaky, projects_root) is False


def test_is_excluded_file_pattern():
    assert security.is_excluded_file("foo.pyc") is True
    assert security.is_excluded_file("image.PNG") is True  # case-insensitive
    assert security.is_excluded_file("archive.tar.gz") is True
    assert security.is_excluded_file("hello.md") is False
    assert security.is_excluded_file("config.json") is False
