# Learner rubric (self-check)

Use after each module in [`CURRICULUM.md`](CURRICULUM.md).

| Skill | I can… | Demo / evidence |
|-------|--------|------------------|
| Tool definition | Write a typed Python function and see its schema in traces | `custom_tools` |
| Chaining | Have the model call tool A then B intentionally | `calculator_basics` |
| Session state | Read/write `ToolContext.state` across turns | `session_memory` |
| Sequential flow | Explain `SequentialAgent` vs a single agent | `sequential_pipeline`, `sequential_state_shared` |
| Delegation | Contrast coordinator `sub_agents` vs `AgentTool` | `multi_agent_coordinator`, `agent_as_tool_orchestrator` |
| Structured output | Constrain final replies with `output_schema` | `structured_output`, `structured_persona_research` |
| Governance | Enable human confirmation before a side effect | `hitl_sensitive_action` |
| Workflow agents | Describe loop exit and parallel merge | `loop_plan_refine`, `parallel_research_synth` |
| Config-first agent | Load tools from YAML | `agent_config_yaml` |

**Pass bar:** run `pytest tests/ -v` from `workshop/` and complete one checkpoint row per demo you teach.
