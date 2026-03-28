# Evaluation (`adk eval`)

## Workshop sample

- **Eval set:** [`eval/calculator_basics_smoke.evalset.json`](eval/calculator_basics_smoke.evalset.json)
- **Target app:** [`demos/02-calculator_basics`](demos/02-calculator_basics)

That file is a single **`EvalSet`** document (not a bare array). ADK parses it with `google.adk.evaluation.eval_set.EvalSet`. Authoritative field definitions live in the Python modules:

- [`eval_set.py`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) — `eval_set_id`, `name`, `description`, `eval_cases`
- [`eval_case.py`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py) — `eval_id`, `conversation`, `session_input`, rubrics, etc.

Each **invocation** in `conversation` has `user_content`, optional `final_response`, and optional `intermediate_data` (`tool_uses`, `tool_responses`, `intermediate_responses`) using the same JSON shape as `google.genai.types.Content` / `FunctionCall`.

## Install

The `adk eval` CLI requires extra dependencies:

```bash
pip install "google-adk[eval]"
```

Core workshop installs only need `google-adk` (see [`requirements-workshop.txt`](requirements-workshop.txt)); add the `[eval]` extra when you run evaluations.

## Commands

From the **`workshop`** directory, with `GOOGLE_API_KEY` set:

```bash
adk eval demos/02-calculator_basics eval/calculator_basics_smoke.evalset.json
```

Specific eval case ids (comma-separated after `:`):

```bash
adk eval demos/02-calculator_basics eval/calculator_basics_smoke.evalset.json:add_two_decimals
```

Optional flags: `--config_file_path` for metric weights, `--print_detailed_results`, `--eval_storage_uri` for GCS-backed sets (see `adk eval --help`).

## `adk eval` vs `adk web` package layout

`adk web` loads `root_agent` from `agent.py` under each app folder. **`adk eval` currently loads `demos/<app>/__init__.py` as the entry module** and expects `from . import agent` so that `root_agent` is available as `agent.root_agent`. The calculator demo therefore includes [`demos/02-calculator_basics/__init__.py`](demos/02-calculator_basics/__init__.py). Add the same pattern to other demos if you point `adk eval` at them.

## Legacy array format

If `EvalSet.model_validate_json` fails, `load_eval_set_from_file` falls back to `convert_eval_set_to_pydantic_schema` in `local_eval_sets_manager`, which accepts a JSON **array** of cases with `name`, `data[]` (`query`, `reference`, `expected_tool_use`, …), and `initial_session`. New workshop content should use the **`EvalSet` JSON object** so `eval_set_id` and types are explicit.

## CI / pytest

[`tests/test_eval_set_schema.py`](tests/test_eval_set_schema.py) checks that the sample file validates (no API calls). Full `adk eval` runs are optional and need a key plus `google-adk[eval]`.

More detail: [`eval/README.md`](eval/README.md).
