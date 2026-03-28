# 11-multi_agent_coordinator

**Goal:** **Multi-agent** composition: a coordinator `root_agent` with `sub_agents`, each with its own tools and instructions.

## Architecture

```text
          ┌──────────────────────────────────┐
          │      dice_prime_coordinator       │  ← root agent (no tools)
          │      model: gemini-flash-lite     │
          │      routes by sub-agent desc.    │
          └───────────────┬──────────────────┘
                          │ delegates to
              ┌───────────┴───────────┐
              ▼                       ▼
  ┌────────────────────┐   ┌────────────────────┐
  │     roll_agent      │   │     prime_agent     │  ← sub-agents
  │                    │   │                    │
  │  ┌──────────────┐  │   │  ┌──────────────┐  │
  │  │  roll_die()  │  │   │  │check_prime() │  │  ← tools
  │  └──────────────┘  │   │  └──────────────┘  │
  └────────────────────┘   └────────────────────┘
```

## Try it

```text
Roll a 10-sided die.
```

```text
Is that number prime? (follow-up after the roll)
```

```text
Roll a 15-sided die and tell me if the result is prime.
```

**Upstream reference:** [hello_world_ma](https://github.com/google/adk-python/blob/main/contributing/samples/hello_world_ma/agent.py) (includes `ExampleTool`; this demo stays minimal).
