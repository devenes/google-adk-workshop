# 10-agent_config_yaml

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

**Note:** The folder name `10-agent_config_yaml` is not a valid Python identifier, so `__init__.py` adds its own directory to `sys.path` at import time — this lets the YAML's `tools.*` references resolve correctly.

See [CHECKPOINTS.md](../CHECKPOINTS.md).
