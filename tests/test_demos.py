"""Smoke tests: each workshop demo exposes a valid root_agent (no LLM calls)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent
from google.adk.tools.function_tool import FunctionTool

_DEMOS_DIR = Path(__file__).resolve().parent.parent / "demos"

DEMO_NAMES = [
    "hello_web",
    "calculator_basics",
    "custom_tools",
    "static_kb_rag",
    "sequential_pipeline",
    "day_trip_search",
    "session_memory",
    "multi_agent_coordinator",
    "structured_output",
    "hitl_sensitive_action",
    "loop_plan_refine",
    "parallel_research_synth",
]


def _load_demo_module(demo_name: str):
  path = _DEMOS_DIR / demo_name / "agent.py"
  assert path.is_file(), f"Missing {path}"
  spec = importlib.util.spec_from_file_location(
      f"workshop_demo_{demo_name}", path
  )
  assert spec and spec.loader
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


@pytest.mark.parametrize("name", DEMO_NAMES)
def test_demo_defines_root_agent(name: str):
  mod = _load_demo_module(name)
  root = mod.root_agent
  assert root.name
  model = getattr(root, "model", None)
  if model is not None:
    assert model
  else:
    assert isinstance(
        root, SequentialAgent
    ), f"{name}: non-LLM root should be SequentialAgent"
    assert root.sub_agents


def test_hello_web_is_minimal():
  root = _load_demo_module("hello_web").root_agent
  assert not root.tools


def test_day_trip_has_search_tool():
  root = _load_demo_module("day_trip_search").root_agent
  assert root.tools
  assert len(root.tools) >= 1


def test_custom_tools_function_tools():
  root = _load_demo_module("custom_tools").root_agent
  assert root.tools and len(root.tools) == 2


def test_calculator_tools():
  root = _load_demo_module("calculator_basics").root_agent
  assert root.tools and len(root.tools) == 2


def test_static_kb_one_tool():
  root = _load_demo_module("static_kb_rag").root_agent
  assert root.tools and len(root.tools) >= 1


def test_multi_agent_structure():
  root = _load_demo_module("multi_agent_coordinator").root_agent
  assert root.sub_agents and len(root.sub_agents) == 2
  names = {a.name for a in root.sub_agents}
  assert names == {"roll_agent", "prime_agent"}


def test_session_memory_tools():
  root = _load_demo_module("session_memory").root_agent
  assert root.tools and len(root.tools) == 2


def test_sequential_has_two_llm_children():
  root = _load_demo_module("sequential_pipeline").root_agent
  assert isinstance(root, SequentialAgent)
  assert len(root.sub_agents) == 2


def test_structured_output_schema():
  root = _load_demo_module("structured_output").root_agent
  assert root.output_schema is not None


def test_hitl_wraps_function_tool_with_confirmation():
  root = _load_demo_module("hitl_sensitive_action").root_agent
  assert len(root.tools) == 1
  tool = root.tools[0]
  assert isinstance(tool, FunctionTool)
  assert getattr(tool, "_require_confirmation", None) is True


def test_loop_plan_refine_workflow():
  root = _load_demo_module("loop_plan_refine").root_agent
  assert isinstance(root, SequentialAgent)
  assert len(root.sub_agents) == 2
  assert isinstance(root.sub_agents[1], LoopAgent)
  loop = root.sub_agents[1]
  assert loop.max_iterations == 3
  assert {a.name for a in loop.sub_agents} == {"critic_agent", "refiner_agent"}


def test_parallel_research_structure():
  root = _load_demo_module("parallel_research_synth").root_agent
  assert isinstance(root, SequentialAgent)
  assert len(root.sub_agents) == 2
  assert isinstance(root.sub_agents[0], ParallelAgent)
  para = root.sub_agents[0]
  assert len(para.sub_agents) == 3
  assert {a.name for a in para.sub_agents} == {
      "museum_agent",
      "events_agent",
      "food_agent",
  }
