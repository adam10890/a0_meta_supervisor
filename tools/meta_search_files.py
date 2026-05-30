"""meta_search_files — find filenames matching a glob or substring.

Args:
    pattern: str        # required
    project: str | None # optional — limit to one project
    max_results: int = 50
"""

import os
from pathlib import Path

try:
    from ..helpers.search import search_files
except ImportError:
    import sys
    _here = os.path.dirname(os.path.abspath(__file__))
    _parent = os.path.dirname(_here)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    from helpers.search import search_files  # type: ignore

from python.helpers.tool import Tool, Response

PROJECTS_ROOT = Path("/a0/usr/projects")
DEFAULT_MAX = 50


class MetaSearchFilesTool(Tool):
    """Find files by name across projects."""

    async def execute(self, **kwargs):
        pattern = self.args.get("pattern")
        if not pattern:
            return Response(
                message={"error": "pattern is required"},
                break_loop=False,
            )

        target = self.args.get("project")
        max_results = int(self.args.get("max_results") or DEFAULT_MAX)

        root = PROJECTS_ROOT / target if target else PROJECTS_ROOT
        if not root.exists():
            return Response(
                message={"results": [], "truncated": False, "note": f"path not found: {root}"},
                break_loop=False,
            )

        results = search_files(root, pattern=pattern, max_results=max_results + 1)
        truncated = len(results) > max_results
        results = results[:max_results]

        # Attach project id (derived from path)
        for r in results:
            try:
                rel = Path(r["path"]).relative_to(PROJECTS_ROOT)
                r["project"] = rel.parts[0] if rel.parts else None
            except ValueError:
                r["project"] = None

        return Response(
            message={"results": results, "truncated": truncated},
            break_loop=False,
        )
