"""Defense-in-depth: helpers must refuse forbidden paths even when called
directly. The LLM agent's rules in agent.system.main.rules.md are secondary.
"""

from helpers import search


def test_filename_search_cannot_surface_secrets_env(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="secrets.env")
    assert results == [], f"BREAK: secrets.env was returned: {results}"


def test_filename_search_cannot_surface_a0proj_files(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="*")
    for r in results:
        assert ".a0proj" not in r["path"], (
            f"BREAK: file under .a0proj was returned: {r['path']}"
        )


def test_filename_search_cannot_surface_memory_files(fake_projects_root):
    results = search.search_files(fake_projects_root, pattern="*")
    for r in results:
        assert "memory" + chr(92) not in r["path"] and "memory/" not in r["path"], (
            f"BREAK: file under memory/ was returned: {r['path']}"
        )


def test_content_search_cannot_read_secrets(fake_projects_root, monkeypatch):
    monkeypatch.setattr(search, "_HAVE_RIPGREP", False)
    results = search.search_content(fake_projects_root, query="DO_NOT_LEAK")
    assert results == [], (
        f"BREAK: secrets.env content was returned: {results}"
    )


def test_content_search_cannot_read_memory(fake_projects_root, monkeypatch):
    monkeypatch.setattr(search, "_HAVE_RIPGREP", False)
    results = search.search_content(fake_projects_root, query="private")
    for r in results:
        # Normalize path for windows backslashes
        normalized = r["path"].replace(chr(92), "/")
        assert "memory/" not in normalized, (
            f"BREAK: memory file content was returned: {r['path']}"
        )
