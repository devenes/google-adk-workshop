# structured_input_agent

**Level:** Advanced — **Schema-In, Schema-Out Transformation** (`input_schema` and `output_schema`).

This demo illustrates how to define an agent that takes a structured Pydantic model payload as input and outputs another structured Pydantic model payload.

## Architecture

```text
       [UserActivityLog payload] (JSON input)
                 │
                 ▼
┌──────────────────────────────────────────┐
│         structured_input_agent           │
│         model: gemini-2.5-flash-lite     │
│                                          │
│  - Input validation: UserActivityLog     │
│  - Output validation: UserAnalysisReport │
└──────────────────────────────────────────┘
                 │
                 ▼
      [UserAnalysisReport payload] (JSON output)
```

## Setup and Concepts

1. **`input_schema`**: Restricts the inputs acceptable by this agent (or when wrapped in an `AgentTool`).
2. **`output_schema`**: Forces Gemini to respond with a structured JSON object matching the defined Pydantic model.
3. **Agent-to-Agent Delegation**: When an orchestrator wraps this agent inside an `AgentTool`, the orchestrator parses the `input_schema` parameters, ensuring strong typing between sub-agents.

## Run and Try

Run the web interface:
```bash
cd demos && adk web .
```
And select `structured_input_agent`.

See [CHECKPOINTS.md](../CHECKPOINTS.md) for verification details.
