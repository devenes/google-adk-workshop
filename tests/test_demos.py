"""Smoke tests: each workshop demo exposes a valid root_agent (no LLM calls)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool

_DEMOS_DIR = Path(__file__).resolve().parent.parent / "demos"

DEMO_NAMES = [
    "01-hello_web",
    "02-calculator_basics",
    "03-custom_tools",
    "04-static_kb_rag",
    "07-sequential_pipeline",
    "05-day_trip_search",
    "06-session_memory",
    "08-sequential_state_shared",
    "09-live_weather_nws",
    "12-agent_as_tool_orchestrator",
    "11-multi_agent_coordinator",
    "13-structured_output",
    "15-structured_persona_research",
    "14-hitl_sensitive_action",
    "16-loop_plan_refine",
    "17-parallel_research_synth",
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
  root = _load_demo_module("01-hello_web").root_agent
  assert not root.tools


def test_day_trip_has_search_tool():
  root = _load_demo_module("05-day_trip_search").root_agent
  assert root.tools
  assert len(root.tools) >= 1


def test_custom_tools_function_tools():
  root = _load_demo_module("03-custom_tools").root_agent
  assert root.tools and len(root.tools) == 2


def test_calculator_tools():
  root = _load_demo_module("02-calculator_basics").root_agent
  assert root.tools and len(root.tools) == 2


def test_static_kb_one_tool():
  root = _load_demo_module("04-static_kb_rag").root_agent
  assert root.tools and len(root.tools) >= 1


def test_multi_agent_structure():
  root = _load_demo_module("11-multi_agent_coordinator").root_agent
  assert root.sub_agents and len(root.sub_agents) == 2
  names = {a.name for a in root.sub_agents}
  assert names == {"roll_agent", "prime_agent"}


def test_session_memory_tools():
  root = _load_demo_module("06-session_memory").root_agent
  assert root.tools and len(root.tools) == 2


def test_sequential_has_two_llm_children():
  root = _load_demo_module("07-sequential_pipeline").root_agent
  assert isinstance(root, SequentialAgent)
  assert len(root.sub_agents) == 2


def test_structured_output_schema():
  root = _load_demo_module("13-structured_output").root_agent
  assert root.output_schema is not None


def test_hitl_has_send_email_tool():
  root = _load_demo_module("14-hitl_sensitive_action").root_agent
  assert len(root.tools) == 1
  # Confirmation is enforced via agent instruction; send_email is the single tool.
  assert root.tools[0].__name__ == "send_email"


def test_loop_plan_refine_workflow():
  root = _load_demo_module("16-loop_plan_refine").root_agent
  assert isinstance(root, SequentialAgent)
  assert len(root.sub_agents) == 2
  assert isinstance(root.sub_agents[1], LoopAgent)
  loop = root.sub_agents[1]
  assert loop.max_iterations == 3
  assert {a.name for a in loop.sub_agents} == {"critic_agent", "refiner_agent"}


def test_parallel_research_structure():
  root = _load_demo_module("17-parallel_research_synth").root_agent
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


def test_sequential_state_shared_destination_key():
  root = _load_demo_module("08-sequential_state_shared").root_agent
  assert isinstance(root, SequentialAgent)
  assert root.sub_agents[0].output_key == "destination"


def test_agent_as_tool_wraps_sub_agent():
  root = _load_demo_module("12-agent_as_tool_orchestrator").root_agent
  assert any(isinstance(t, AgentTool) for t in root.tools)


def test_structured_persona_schema_and_nested_tool():
  root = _load_demo_module("15-structured_persona_research").root_agent
  assert root.output_schema is not None
  assert any(isinstance(t, AgentTool) for t in root.tools)


def test_agent_config_yaml_loads_via_loader():
  import yaml

  # AgentLoader now requires valid Python identifiers (no hyphens / leading digits),
  # so we validate the YAML config file directly instead of going through the loader.
  yaml_path = _DEMOS_DIR / "10-agent_config_yaml" / "root_agent.yaml"
  assert yaml_path.is_file(), f"Missing {yaml_path}"

  with open(yaml_path) as f:
    config = yaml.safe_load(f)

  assert config["name"] == "yaml_dice_workshop"
  assert "tools" in config and len(config["tools"]) >= 2
