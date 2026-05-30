### meta_search_content:
Grep file contents across all projects. Read-only.

Args:
- query: (required, str) substring, or regex if regex=true
- project: (optional, str)
- file_glob: (optional, str, e.g. "*.md")
- max_results: (optional, int, default 30)
- regex: (optional, bool, default false)

Returns: { "results": [{ "project", "path", "line", "snippet" }, ...], "truncated": bool }

NEVER reads secrets.env, memory/, .a0proj/ (other than project.json which is not grepped),
or files larger than 5MB. Skips binaries.

Usage:
~~~json
{
  "thoughts": ["Find any mention of PostgreSQL in markdown files."],
  "tool_name": "meta_search_content",
  "tool_args": { "query": "PostgreSQL", "file_glob": "*.md" }
}
~~~
