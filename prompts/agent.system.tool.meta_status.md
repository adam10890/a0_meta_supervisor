### meta_status:
Get a cross-project status overview. Read-only.

Args:
- project: (optional, str) filter to a single project_id
- include_files: (optional, bool, default false) include top-level file tree per project
- include_chats: (optional, bool, default true) include chat_count and last_activity per project

Returns: { "projects": [...], "orphan_chats": [...] }
Each project: { id, status, title, description, memory_mode, git_url, chat_count?, last_activity?, file_tree? }
Invalid projects (missing or malformed project.json) appear with status: "invalid" and a reason.

Usage:
~~~json
{
  "thoughts": ["I should see what's across all projects."],
  "tool_name": "meta_status",
  "tool_args": {}
}
~~~
