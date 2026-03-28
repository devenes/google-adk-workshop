# 15-structured_persona_research

**Level:** Expert — **`output_schema` on root + specialist as search tool** (pattern from [output_schema_with_tools](https://github.com/google/adk-python/blob/main/contributing/samples/output_schema_with_tools/agent.py)).

> **Note:** Gemini forbids combining built-in tools (`google_search`) and function calling (`output_schema`) in the same request. The fix is to split concerns: the specialist searches freely (no `output_schema`), and the orchestrator formats the result (no `google_search`).

## Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│         person_orchestrator  (root agent)                     │
│         model: gemini-2.5-flash                               │
│         output_schema: PersonInfo (Pydantic)                  │
│         no google_search — keeps function calling safe        │
│                                                              │
│  ┌─────────────────────────────┐                             │
│  │  AgentTool(person_specialist)│                             │  ← tool
│  │  (agent wrapped as a tool)   │                             │
│  └──────────────┬──────────────┘                             │
└─────────────────│────────────────────────────────────────────┘
                  │ invoked as tool call
                  ▼
      ┌────────────────────────────────────┐
      │        person_specialist            │  ← sub-agent
      │        model: gemini-2.5-flash-lite │
      │        no output_schema             │
      │        (incompatible with built-in) │
      │                                    │
      │  ┌──────────────────────────────┐  │
      │  │       google_search()         │  │  ← specialist tool
      │  └──────────────────────────────┘  │
      └────────────────────────────────────┘
                  │ returns free-form text
                  ▼
      orchestrator formats into:
        PersonInfo { name, age, occupation, location, biography }
```

## Try it

```text
Structured PersonInfo for Marie Curie.
```

```text
Generate a PersonInfo profile for Alan Turing.
```

```text
Create a structured PersonInfo entry for Grace Hopper.
```

**Checkpoint:** UI / JSON shows `PersonInfo` fields; tool trace includes `person_specialist` → `google_search`.

See [CHECKPOINTS.md](../CHECKPOINTS.md).
