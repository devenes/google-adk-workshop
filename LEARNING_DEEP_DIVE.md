# Deep-dive topics (callbacks, memory, streaming)

Short pointers for presenters and self-study; full detail lives in [ADK documentation](https://google.github.io/adk-docs/).

## Callbacks

- **Lifecycle hooks** (before/after model, tool, etc.) let you log, redact, or enforce policies without changing core agent logic.
- Start with the [Agents — callbacks](https://google.github.io/adk-docs/) section and the `core_callback_config` sample in `adk-python/contributing/samples/`.

## Session vs memory vs state

- **`Session`**: conversation thread + metadata managed by a **session service** (e.g. in-memory for notebooks, persistent in production).
- **`ToolContext.state`**: key-value carry-over **within** a session across turns (see `06-session_memory` demo).
- **Memory service** (when enabled): longer-horizon retrieval across sessions — distinct from per-session state; see ADK docs on memory plugins/services.

## Rewind / branching

- Some runtimes support **rewinding** or editing prior turns for debugging UIs; behavior depends on ADK version and server. Treat as an advanced debugging feature, not a core workshop objective.

## Streaming

- **`Runner.run_async`** yields **events**; the final response is one kind of event. UIs can stream partial tokens when the stack exposes them — check current ADK streaming APIs for your target client.

## HITL (human-in-the-loop)

- **`FunctionTool(..., require_confirmation=True)`** pauses for user approval in supported clients (`14-hitl_sensitive_action` demo). Pair with [tool confirmation docs](https://google.github.io/adk-docs/tools/confirmation/).
