"""Smoke: sample eval file matches current ADK EvalSet Pydantic schema."""

from __future__ import annotations

from pathlib import Path

from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.local_eval_sets_manager import load_eval_set_from_file

_EVAL_FILE = (
    Path(__file__).resolve().parent.parent
    / "eval"
    / "calculator_basics_smoke.evalset.json"
)


def test_sample_eval_set_validates_as_eval_set():
  raw = _EVAL_FILE.read_text(encoding="utf-8")
  es = EvalSet.model_validate_json(raw)
  assert es.eval_set_id == "workshop_calculator_basics_smoke"
  assert len(es.eval_cases) == 1
  case = es.eval_cases[0]
  assert case.eval_id == "add_two_decimals"
  assert case.session_input is not None
  assert case.session_input.app_name == "calculator_basics"
  assert case.conversation and len(case.conversation) == 1


def test_load_eval_set_from_file_round_trip():
  es = load_eval_set_from_file(str(_EVAL_FILE), eval_set_id="ignored_for_new_schema")
  assert es.eval_set_id == "workshop_calculator_basics_smoke"
