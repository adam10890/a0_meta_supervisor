"""Filename + content search across projects.

search_files: walks the tree, matches glob or substring against file names.
search_content: greps file contents. Prefers ripgrep if on PATH, else python re.

All searches respect security.EXCLUDED_DIRS, EXCLUDED_FILE_PATTERNS,
MAX_FILE_SIZE. The .a0proj/project.json exception is NOT extended to content
search — project.json is read by project_scanner directly, not by grep.
"""

import fnmatch
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from . import security

MAX_FILE_SIZE = security.MAX_FILE_SIZE
MAX_FILES_SCANNED = security.MAX_FILES_SCANNED

_HAVE_RIPGREP = shutil.which("rg") is not None


def _is_dir_excluded(dirname: str) -> bool:
    return dirname in security.EXCLUDED_DIRS


def _walk(root: Path):
    """Yield (path, name) for every file under root, skipping excluded dirs."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _is_dir_excluded(d)]
        for fn in filenames:
            yield Path(dirpath) / fn, fn


def search_files(
    projects_root: Path,
    pattern: str,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """Search filenames by glob (if pattern contains * or ?) or substring."""
    results: List[Dict[str, Any]] = []
    is_glob = any(ch in pattern for ch in "*?[")
    pat_lower = pattern.lower()

    for path, name in _walk(projects_root):
        if security.is_excluded_file(name):
            continue
        if is_glob:
            if not fnmatch.fnmatch(name.lower(), pat_lower):
                continue
        else:
            if pat_lower not in name.lower():
                continue
        try:
            stat = path.stat()
        except OSError:
            continue
        results.append({
            "path": str(path),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        })
        if len(results) >= max_results:
            break
    return results


def search_content(
    projects_root: Path,
    query: str,
    file_glob: Optional[str] = None,
    max_results: int = 30,
    regex: bool = False,
) -> List[Dict[str, Any]]:
    """Search file contents. Returns [{path, line, snippet}, ...]."""
    if _HAVE_RIPGREP:
        try:
            return _search_content_ripgrep(projects_root, query, file_glob, max_results, regex)
        except (subprocess.SubprocessError, OSError):
            pass  # fall through to python
    return _search_content_python(projects_root, query, file_glob, max_results, regex)


def _search_content_python(
    projects_root: Path,
    query: str,
    file_glob: Optional[str],
    max_results: int,
    regex: bool,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    scanned = 0
    pat = re.compile(query if regex else re.escape(query), re.IGNORECASE)

    for path, name in _walk(projects_root):
        if scanned >= MAX_FILES_SCANNED:
            break
        if security.is_excluded_file(name):
            continue
        if file_glob and not fnmatch.fnmatch(name.lower(), file_glob.lower()):
            continue
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1

        for i, line in enumerate(text.splitlines(), start=1):
            if pat.search(line):
                results.append({
                    "path": str(path),
                    "line": i,
                    "snippet": line[:200],
                })
                if len(results) >= max_results:
                    return results
    return results


def _search_content_ripgrep(
    projects_root: Path,
    query: str,
    file_glob: Optional[str],
    max_results: int,
    regex: bool,
) -> List[Dict[str, Any]]:
    cmd = ["rg", "--no-heading", "--line-number", "--color", "never", "-i"]
    if not regex:
        cmd.append("--fixed-strings")
    for excluded in security.EXCLUDED_DIRS:
        cmd += ["--glob", f"!{excluded}/"]
    for pat in security.EXCLUDED_FILE_PATTERNS:
        cmd += ["--glob", f"!{pat}"]
    if file_glob:
        cmd += ["--glob", file_glob]
    cmd += ["--max-count", str(max_results)]
    cmd += ["--max-filesize", f"{MAX_FILE_SIZE}"]
    cmd += [query, str(projects_root)]

    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
    if proc.returncode not in (0, 1):  # 1 = no matches
        raise subprocess.SubprocessError(f"rg exited {proc.returncode}: {proc.stderr[:200]}")

    results: List[Dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        path, line_no, snippet = parts
        try:
            line_no_int = int(line_no)
        except ValueError:
            continue
        results.append({
            "path": path,
            "line": line_no_int,
            "snippet": snippet[:200],
        })
        if len(results) >= max_results:
            break
    return results
