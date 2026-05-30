### meta_search_files:
Search for filenames across all projects. Read-only.

Args:
- pattern: (required, str) glob (e.g. "*.md") or substring (e.g. "schema")
- project: (optional, str) limit to a single project_id
- max_results: (optional, int, default 50)

Returns: { "results": [{ "project", "path", "size", "mtime" }, ...], "truncated": bool }

Files under .a0proj/, memory/, and binary patterns (*.png, *.zip, etc.) are NEVER returned.

Usage:
~~~json
{
  "thoughts": ["Find any file named schema.sql across projects."],
  "tool_name": "meta_search_files",
  "tool_args": { "pattern": "schema.sql" }
}
~~~
