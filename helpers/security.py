"""Path-safety and exclusion rules for the meta supervisor plugin.

All read operations in tools/ MUST route through is_safe_path() before
touching the filesystem. This is defense-in-depth — LLM rules in the
agent profile are secondary.
"""

from pathlib import Path
import fnmatch

EXCLUDED_DIRS = {
    ".a0proj",       # project meta — only project.json is allowed, via explicit reads
    "memory",        # project agent private memory
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
}

EXCLUDED_FILE_PATTERNS = {
    "*.pyc",
    "*.pyo",
    "*.db",
    "*.sqlite",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.zip",
    "*.tar",
    "*.tar.gz",
    "*.tgz",
    "*.gz",
}

MAX_FILE_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_FILES_SCANNED = 2000          # per content search


def is_safe_path(path: Path, projects_root: Path) -> bool:
    """Return True if `path` is safe for a generic file read.

    Specifically: path must be a descendant of projects_root, must not
    traverse into any EXCLUDED_DIRS segment, and the path itself (or any
    parent up to projects_root) must not be `.a0proj` *except* for the
    single allowed file `<project>/.a0proj/project.json`.
    """
    try:
        resolved = path.resolve()
        root_resolved = projects_root.resolve()
        resolved.relative_to(root_resolved)
    except (ValueError, OSError):
        return False

    rel = resolved.relative_to(root_resolved)
    parts = rel.parts

    # Allow exactly the path <project>/.a0proj/project.json
    if len(parts) == 3 and parts[1] == ".a0proj" and parts[2] == "project.json":
        return True

    for segment in parts:
        if segment in EXCLUDED_DIRS:
            return False

    return True


def is_excluded_file(filename: str) -> bool:
    """True if the filename matches any EXCLUDED_FILE_PATTERNS (case-insensitive)."""
    lower = filename.lower()
    for pattern in EXCLUDED_FILE_PATTERNS:
        if fnmatch.fnmatch(lower, pattern.lower()):
            return True
    return False
