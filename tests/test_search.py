from pathlib import Path
from helpers import search


def test_search_files_by_substring(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="notes")
    paths = {r["path"] for r in results}
    # demo_valid/notes.md and demo_no_a0proj/notes.md
    assert any("demo_valid" in p and "notes.md" in p for p in paths)
    assert any("demo_no_a0proj" in p and "notes.md" in p for p in paths)


def test_search_files_by_glob(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="*.md")
    # Both notes.md files but not secrets.env
    assert all(r["path"].endswith(".md") for r in results)
    assert len(results) >= 2


def test_search_files_excludes_a0proj_contents(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="secrets")
    # secrets.env lives under .a0proj/ — must NEVER be returned
    assert all("secrets.env" not in r["path"] for r in results)


def test_search_files_excludes_memory(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="private")
    assert all("memory" not in r["path"] for r in results)


def test_search_files_respects_max_results(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="*", max_results=1)
    assert len(results) <= 1


def test_search_content_python_fallback(fake_projects_root, monkeypatch):
    """Force python fallback by pretending ripgrep is missing."""
    monkeypatch.setattr(search, "_HAVE_RIPGREP", False)
    results = search.search_content(fake_projects_root, query="PostgreSQL")
    assert len(results) >= 1
    assert any("PostgreSQL" in r["snippet"] for r in results)
    assert any("notes.md" in r["path"] for r in results)


def test_search_content_excludes_secrets(fake_projects_root, monkeypatch):
    monkeypatch.setattr(search, "_HAVE_RIPGREP", False)
    results = search.search_content(fake_projects_root, query="DO_NOT_LEAK")
    # secrets.env contains DO_NOT_LEAK — search must not find it
    assert results == []


def test_search_content_excludes_memory(fake_projects_root, monkeypatch):
    monkeypatch.setattr(search, "_HAVE_RIPGREP", False)
    results = search.search_content(fake_projects_root, query="private")
    # memory/private.json contains "private" — must be skipped
    assert all("memory" not in r["path"] for r in results)


def test_search_content_skips_oversized_files(tmp_path, monkeypatch):
    monkeypatch.setattr(search, "_HAVE_RIPGREP", False)
    monkeypatch.setattr(search, "MAX_FILE_SIZE", 100)
    big = tmp_path / "big.md"
    big.write_text("PostgreSQL " * 200, encoding="utf-8")
    results = search.search_content(tmp_path, query="PostgreSQL")
    assert results == []
