### meta_chat_summary:
List chats grouped by their linked project. Read-only.

Args:
- project: (optional, str) filter to one project
- limit: (optional, int, default 10) max chats per project
- include_text: (optional, bool, default false) attach first_line and last_line previews

Returns: {
  "by_project": { "<project_id>": [{ id, name, agent_profile, created_at, last_message, log_length?, first_line?, last_line? }] },
  "orphan_chats": [{ id, name, project_referenced, last_message }],
  "corrupt_chats": [{ id, status, reason }]
}

A chat is "orphan" if its data.project points to a project that no longer exists.
Always surface orphans; do not hide them.

Usage:
~~~json
{
  "thoughts": ["Show recent chats of smart_routing_system."],
  "tool_name": "meta_chat_summary",
  "tool_args": { "project": "smart_routing_system" }
}
~~~
