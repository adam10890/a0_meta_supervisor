"""meta_search_content — grep across all projects.

Args:
    query: str           # required
    project: str | None  # optional
    file_glob: str|None  # optional, e.g. "*.md"
    max_results: int = 30
    regex: bool = False
"""

import os
from pathlib import Path

try:
    from ..helpers.search import search_content
except ImportError:
    import sys
    _here = os.path.dirname(os.path.abspath(__file__))
    _parent = os.path.dirname(_here)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    from helpers.search import search_content  # type: ignore

from python.helpers.tool import Tool, Response

PROJECTS_ROOT = Path("/a0/usr/projects")
DEFAULT_MAX = 30


class MetaSearchContentTool(Tool):
    """Grep across project file contents (excluding secrets, memory, binaries)."""

    async def execute(self, **kwargs):
        query = self.args.get("query")
        if not query:
            return Response(
                message={"error": "query is required"},
                break_loop=False,
            )

        target = self.args.get("project")
        file_glob = self.args.get("file_glob")
        max_results = int(self.args.get("max_results") or DEFAULT_MAX)
        regex = bool(self.args.get("regex", False))

        root = PROJECTS_ROOT / target if target else PROJECTS_ROOT
        if not root.exists():
            return Response(
                message={"results": [], "truncated": False, "note": f"path not found: {root}"},
                break_loop=False,
            )

        results = search_content(
            root,
            query=query,
            file_glob=file_glob,
            max_results=max_results + 1,
            regex=regex,
        )
        truncated = len(results) > max_results
        results = results[:max_results]

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
