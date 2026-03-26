# hitl_sensitive_action

**Level:** Advanced (human-in-the-loop / **tool confirmation**).

**Goal:** `FunctionTool(..., require_confirmation=True)` pauses until the user **approves** or **rejects** the call in ADK Web (see [tool confirmation](https://google.github.io/adk-docs/tools/confirmation/)).

**Try:** “Delete all data for customer_id=acme-42 because of a GDPR request.” Approve or reject in the UI.

**YAML-first variant:** [tool_human_in_the_loop_config](https://github.com/google/adk-python/tree/main/contributing/samples/tool_human_in_the_loop_config).
