# Learner rubric (self-check)

Use after each module in [`CURRICULUM.md`](CURRICULUM.md).

| Skill | I can… | Demo / evidence |
|-------|--------|------------------|
| Tool definition | Write a typed Python function and see its schema in traces | `03-custom_tools` |
| Chaining | Have the model call tool A then B intentionally | `02-calculator_basics` |
| Session state | Read/write `ToolContext.state` across turns | `06-session_memory` |
| Sequential flow | Explain `SequentialAgent` vs a single agent | `07-sequential_pipeline`, `08-sequential_state_shared` |
| Delegation | Contrast coordinator `sub_agents` vs `AgentTool` | `11-multi_agent_coordinator`, `12-agent_as_tool_orchestrator` |
| Structured output | Constrain final replies with `output_schema` | `13-structured_output`, `15-structured_persona_research` |
| Governance | Enable human confirmation before a side effect | `14-hitl_sensitive_action` |
| Workflow agents | Describe loop exit and parallel merge | `16-loop_plan_refine`, `17-parallel_research_synth` |
| Config-first agent | Load tools from YAML | `10-agent_config_yaml` |

**Pass bar:** run `pytest tests/ -v` from `workshop/` and complete one checkpoint row per demo you teach.
