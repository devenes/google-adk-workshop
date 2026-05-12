# agent_config_yaml

**Level:** Intermediate — **Agent Config** (`root_agent.yaml`) instead of defining `root_agent` in Python.

**Run:** `cd demos && adk web .` → select `agent_config_yaml`.

**Learn more:** [Agent config docs](https://google.github.io/adk-docs/agents/config/).

## Architecture

```text
  root_agent.yaml  ← agent defined in YAML (not Python)
       │
       ▼
┌──────────────────────────────────────────┐
│           root_agent  (yaml-configured)   │  ← root agent
│           model: (set in YAML)            │
│                                          │
│  ┌─────────────┐   ┌──────────────────┐  │
│  │  roll_die() │   │  check_prime()   │  │  ← tools referenced
│  └─────────────┘   └──────────────────┘  │     via tools.* in YAML
└──────────────────────────────────────────┘
```

## Try it

```text
Roll a 10-sided die.
```

```text
Is 17 prime?
```

```text
Roll a 20-sided die and tell me if the result is prime.
```

**Note:** This demo uses a YAML agent definition in `root_agent.yaml`, and the local `agent.py` wrapper loads that config (including `tools.*` lookups) so `adk eval` can still resolve a stable `agent.root_agent` contract through the package shim in `__init__.py`.

See [CHECKPOINTS.md](../CHECKPOINTS.md).
