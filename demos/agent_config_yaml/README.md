# agent_config_yaml

**Level:** Intermediate — **Agent Config** (`root_agent.yaml`) instead of defining `root_agent` in Python.

**Run:** `cd demos && adk web .` → select `agent_config_yaml`.

**Learn more:** [Agent config docs](https://google.github.io/adk-docs/agents/config/).

**Checkpoint:** Same behavior as dice demos: “Roll a 10-sided die” / “Is 17 prime?”.

**Note:** ADK resolves `agent_config_yaml.tools.*` because the app folder name matches the package (see `__init__.py` + `tools.py`).

See [CHECKPOINTS.md](../CHECKPOINTS.md).
