# Sample evaluation sets

This folder holds **offline** eval definitions for the workshop. They use the **Pydantic-backed `EvalSet` JSON** format your installed `google-adk` expects (see `google.adk.evaluation.eval_set.EvalSet` and `eval_case.py` in [adk-python](https://github.com/google/adk-python)).

## Files

| File | Targets |
|------|---------|
| [`calculator_basics_smoke.evalset.json`](calculator_basics_smoke.evalset.json) | [`demos/calculator_basics`](../demos/calculator_basics) — one case, `add_numbers(19.5, 2)` |

## Run (`adk eval`)

1. Install eval extras (pulls heavier deps than `google-adk` alone):

   ```bash
   python3 -m pip install "google-adk[eval]"
   ```

2. Export `GOOGLE_API_KEY` (or Vertex env per ADK docs).

3. From repo root:

   ```bash
   adk eval demos/calculator_basics eval/calculator_basics_smoke.evalset.json
   ```

   Run a subset of cases:

   ```bash
   adk eval demos/calculator_basics eval/calculator_basics_smoke.evalset.json:add_two_decimals
   ```

   Workshop contract for any eval run:

   ```bash
   python3 -m pip install -r requirements-workshop.txt
   python3 -m pytest tests/ -v
   adk eval demos/<demo_folder> eval/<evalset_file>.evalset.json
   ```

**Agent layout:** `adk eval` imports the app folder as a package: it expects each target demo folder to expose `agent.root_agent` from `__init__.py` via `from . import agent` (for example [`demos/calculator_basics/__init__.py`](../demos/calculator_basics/__init__.py)).
YAML-backed demos include a dedicated `agent.py` wrapper (for example [`demos/agent_config_yaml/agent.py`](../demos/agent_config_yaml/agent.py)) that loads `root_agent.yaml` and is re-exported by `__init__.py`.

**Workshop note:** `adk web` still loads demos from `agent.py` (or the configured YAML entry), and the same `__init__.py` package shim keeps `adk eval` loading deterministic across all workshop demos.

## Alternative: legacy JSON array

`load_eval_set_from_file` in ADK falls back to a **legacy** format if `EvalSet.model_validate_json` fails: a top-level **JSON array** of objects `{ "name", "data": [ { "query", "reference", "expected_tool_use", ... } ], "initial_session" }`. Prefer the **`EvalSet` object** for new files; it matches the schema ADK uses in tests and the Web UI.

Longer context: [EVAL.md](../EVAL.md).
