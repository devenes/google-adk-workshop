# 12-agent_as_tool_orchestrator

**Level:** Advanced — **`AgentTool`**: an agent invoked as a tool (same idea as Session 3 / Agent-as-a-Tool in the codelab).

## Architecture

```text
┌───────────────────────────────────────────────────────┐
│             research_orchestrator  (root agent)        │
│             model: gemini-flash-lite                   │
│                                                       │
│  ┌──────────────────────────────┐  ┌───────────────┐  │
│  │  AgentTool(search_specialist)│  │get_current_   │  │  ← tools
│  │  (agent wrapped as a tool)   │  │year()         │  │
│  └──────────────┬───────────────┘  └───────────────┘  │
└─────────────────│─────────────────────────────────────┘
                  │ invoked as tool call
                  ▼
      ┌───────────────────────────┐
      │      search_specialist     │  ← sub-agent (runs inside tool)
      │                           │
      │  ┌───────────────────────┐│
      │  │    google_search()    ││  ← built-in ADK tool
      │  └───────────────────────┘│
      └───────────────────────────┘
```

`get_current_year` is reserved for questions about today's date or current-age
calculations. Historical dates always come from `search_specialist`.

## Try it

```text
Give two facts about Ada Lovelace.
```

```text
What year is it and was she alive then?
```

```text
Who invented the World Wide Web, and in what year?
```

**Checkpoint:** Logs should show the nested specialist run inside the tool.

No extra dependencies — `google_search` is built into `google-adk`.

See [CHECKPOINTS.md](../CHECKPOINTS.md).
