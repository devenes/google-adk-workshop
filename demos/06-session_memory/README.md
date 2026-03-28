# 06-session_memory

**Goal:** Show **session state** through `ToolContext.state`, persisted for the same session across turns in ADK Web.

## Architecture

```text
┌──────────────────────────────────────────────────────────┐
│            session_memory_workshop_agent                  │  ← root agent
│            model: gemini-flash-lite                       │
│                                                          │
│  ┌──────────────────────────┐  ┌──────────────────────┐  │
│  │  remember_display_name() │  │ recall_display_name() │  │  ← state tools
│  │  (writes ToolContext)    │  │ (reads ToolContext)   │  │
│  └──────────────────────────┘  └──────────────────────┘  │
│                                                          │
│                     session.state { }   ← persists across turns
└──────────────────────────────────────────────────────────┘
```

## Try it

```text
Message 1: Please remember my display name is Jordan.
Message 2 (new turn): What's my display name?
```

```text
Message 1: Store my preferred programming language as Python.
Message 2 (new turn): Which language should I use for the project?
```

```text
Message 1: My team name is Falcon Squad.
Message 2 (new turn): What's my team name?
```

**Upstream reference:** [session_state_agent](https://github.com/google/adk-python/tree/main/contributing/samples/session_state_agent) (callback-heavy internal example); this demo keeps the learner-focused path minimal.
