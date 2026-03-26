# Sample evaluation sets

This folder holds **offline** eval definitions for the workshop. They use the **Pydantic-backed `EvalSet` JSON** format your installed `google-adk` expects (see `google.adk.evaluation.eval_set.EvalSet` and `eval_case.py` in [adk-python](https://github.com/google/adk-python)).

## Files

| File | Targets |
|------|---------|
| [`calculator_basics_smoke.evalset.json`](calculator_basics_smoke.evalset.json) | [`demos/calculator_basics`](../demos/calculator_basics) — one case, `add_numbers(19.5, 2)` |

## Run (`adk eval`)

1. Install eval extras (pulls heavier deps than `google-adk` alone):

   ```bash
   pip install "google-adk[eval]"
   ```

2. Export `GOOGLE_API_KEY` (or Vertex env per ADK docs).

3. From `workshop/`:

   ```bash
   adk eval demos/calculator_basics eval/calculator_basics_smoke.evalset.json
   ```

   Run a subset of cases:

   ```bash
   adk eval demos/calculator_basics eval/calculator_basics_smoke.evalset.json:add_two_decimals
   ```

**Agent layout:** `adk eval` imports the app folder as a package: it expects [`demos/calculator_basics/__init__.py`](../demos/calculator_basics/__init__.py) with `from . import agent` (same pattern as upstream samples). `adk web` continues to work with `agent.py` only.

## Alternative: legacy JSON array

`load_eval_set_from_file` in ADK falls back to a **legacy** format if `EvalSet.model_validate_json` fails: a top-level **JSON array** of objects `{ "name", "data": [ { "query", "reference", "expected_tool_use", ... } ], "initial_session" }`. Prefer the **`EvalSet` object** for new files; it matches the schema ADK uses in tests and the Web UI.

Longer context: [EVAL.md](../EVAL.md).
