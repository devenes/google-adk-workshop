"""Smoke tests: each workshop demo exposes a valid root_agent (no LLM calls)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch
import sys

import pytest
import requests
from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
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
    "sequential_state_shared",
    "live_weather_nws",
    "agent_as_tool_orchestrator",
    "multi_agent_coordinator",
    "structured_output",
    "structured_persona_research",
    "hitl_sensitive_action",
    "loop_plan_refine",
    "parallel_research_synth",
    "structured_input_agent",
    "few_shot_translator",
    "code_execution_agent",
    "grounded_qa_agent",
]


def _load_demo_module_file(module_name: str, path: Path):
  assert path.is_file(), f"Missing {path}"
  spec = importlib.util.spec_from_file_location(
      module_name, path
  )
  assert spec and spec.loader
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


def _load_demo_module(demo_name: str):
  return _load_demo_module_file(f"workshop_demo_{demo_name}", _DEMOS_DIR / demo_name / "agent.py")


@contextmanager
def _load_demo_init_module_direct(
    demo_name: str,
    module_name: str,
    cleanup_module_names: tuple[str, ...] = (),
    **spec_kwargs,
):
  demo_path = _DEMOS_DIR / demo_name / "__init__.py"
  cleanup_module_names = cleanup_module_names + (
      module_name,
      f"{module_name}.agent",
  )
  spec = importlib.util.spec_from_file_location(module_name, demo_path, **spec_kwargs)
  assert spec and spec.loader
  mod = importlib.util.module_from_spec(spec)
  sys.modules[module_name] = mod
  try:
    spec.loader.exec_module(mod)
    yield mod
  finally:
    for leftover in set(cleanup_module_names):
      sys.modules.pop(leftover, None)


def _load_demo_init_module(demo_name: str):
  demo_path = _DEMOS_DIR / demo_name / "__init__.py"
  module_name = f"workshop_demo_{demo_name.replace('-', '_')}_init"
  # Load the package as a package-like module so relative imports in
  # app-level __init__.py files (for example, `from . import agent`) resolve.
  spec = importlib.util.spec_from_file_location(
      module_name,
      demo_path,
      submodule_search_locations=[str(demo_path.parent)],
  )
  assert spec and spec.loader
  mod = importlib.util.module_from_spec(spec)
  sys.modules[module_name] = mod
  try:
    spec.loader.exec_module(mod)
  finally:
    sys.modules.pop(module_name, None)
  return mod


def _load_demo_tools_module(demo_name: str):
  return _load_demo_module_file(
      f"workshop_demo_{demo_name}_tools", _DEMOS_DIR / demo_name / "tools.py"
  )


class _DummyToolContext:
  def __init__(self):
    self.state = {}


class _FakeResponse:
  """Minimal response object used to test request error and decode paths."""

  def __init__(self, payload=None, json_error: Exception | None = None):
    self._payload = payload if payload is not None else {}
    self._json_error = json_error

  def raise_for_status(self):
    return None

  def json(self):
    if self._json_error:
      raise self._json_error
    return self._payload


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
  assert root.tools and len(root.tools) == 4
  mod = _load_demo_module("calculator_basics")
  assert mod.add_numbers(2, 3) == 5
  assert mod.add_numbers(2.5, 2.5) == 5
  assert mod.add_numbers(True, 2) == (
      "Invalid input: add_numbers expects two numeric values."
  )
  assert mod.add_numbers("abc", 2) == (
      "Invalid input: add_numbers expects two numeric values."
  )
  assert mod.add_numbers(float("nan"), 1) == (
      "Invalid input: add_numbers expects two numeric values."
  )
  assert mod.add_numbers(float("inf"), 1) == (
      "Invalid input: add_numbers expects two numeric values."
  )
  assert mod.subtract_numbers(10, 3) == 7
  assert mod.subtract_numbers(0.5, 0.2) == pytest.approx(0.3)
  assert mod.subtract_numbers(True, 1) == (
      "Invalid input: subtract_numbers expects two numeric values."
  )
  assert mod.subtract_numbers("x", 1) == (
      "Invalid input: subtract_numbers expects two numeric values."
  )
  assert mod.multiply_numbers(2, 3) == 6
  assert mod.multiply_numbers("2", 2.5) == 5
  assert mod.multiply_numbers("bad", 2) == (
      "Invalid input: multiply_numbers expects two numeric values."
  )
  assert mod.multiply_numbers(float("nan"), 2) == (
      "Invalid input: multiply_numbers expects two numeric values."
  )
  assert mod.multiply_numbers(float("-inf"), 2) == (
      "Invalid input: multiply_numbers expects two numeric values."
  )
  assert mod.divide_numbers(10, 2) == 5.0
  assert mod.divide_numbers(7, 2) == 3.5
  assert mod.divide_numbers(5, 0) == "Cannot divide by zero."
  assert mod.divide_numbers(True, 2) == (
      "Invalid input: divide_numbers expects two numeric values."
  )
  assert mod.divide_numbers(float("inf"), 2) == (
      "Invalid input: divide_numbers expects two numeric values."
  )



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


def test_structured_input_and_output_schemas():
  root = _load_demo_module("structured_input_agent").root_agent
  assert root.input_schema is not None
  assert root.output_schema is not None
  assert root.input_schema.__name__ == "UserActivityLog"
  assert root.output_schema.__name__ == "UserAnalysisReport"


def test_few_shot_translator_instructions():
  root = _load_demo_module("few_shot_translator").root_agent
  assert "--- Examples ---" in root.instruction
  assert "[TONE:" in root.instruction


def test_code_execution_agent_config():
  root = _load_demo_module("code_execution_agent").root_agent
  assert root.code_executor is not None
  assert root.code_executor.__class__.__name__ == "BuiltInCodeExecutor"


def test_grounded_qa_agent_config():
  root = _load_demo_module("grounded_qa_agent").root_agent
  assert len(root.tools) == 1
  assert root.tools[0].__class__.__name__ == "UrlContextTool"


def test_hitl_has_send_email_tool():
  root = _load_demo_module("hitl_sensitive_action").root_agent
  assert len(root.tools) == 1
  # Confirmation is enforced via agent instruction; send_email is the single tool.
  assert root.tools[0].__name__ == "send_email"


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


def test_sequential_state_shared_destination_key():
  root = _load_demo_module("sequential_state_shared").root_agent
  assert isinstance(root, SequentialAgent)
  assert root.sub_agents[0].output_key == "destination"


def test_agent_as_tool_wraps_sub_agent():
  root = _load_demo_module("agent_as_tool_orchestrator").root_agent
  assert any(isinstance(t, AgentTool) for t in root.tools)


def test_structured_persona_schema_and_nested_tool():
  root = _load_demo_module("structured_persona_research").root_agent
  assert root.output_schema is not None
  assert any(isinstance(t, AgentTool) for t in root.tools)


def test_agent_config_yaml_loads_via_loader():
  init_module = _load_demo_init_module("agent_config_yaml")
  assert hasattr(init_module, "agent")
  root = init_module.agent.root_agent

  assert root.name == "yaml_dice_workshop"
  assert root.tools
  tool_names = {
      getattr(tool, "name", getattr(tool, "__name__", "")) for tool in root.tools
  }
  assert tool_names == {"roll_die", "check_prime"}
  assert root.model


def test_agent_config_yaml_import_context_falls_back_to_agent_module(monkeypatch):
  import builtins

  module_name = "workshop_demo_10_agent_config_yaml_direct_load"
  fallback_module_name = "demos_10_agent_config_yaml_agent"
  original_import = builtins.__import__
  fallback_calls = {"count": 0}
  original_spec_from_file_location = importlib.util.spec_from_file_location

  def blocked_relative_agent_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "" and level == 1 and "agent" in fromlist:
      raise ModuleNotFoundError("No module named 'agent'", name="agent")
    return original_import(name, globals, locals, fromlist, level)

  def counted_spec(*args, **kwargs):
    if len(args) >= 1 and args[0] == fallback_module_name:
      fallback_calls["count"] += 1
    return original_spec_from_file_location(*args, **kwargs)

  monkeypatch.setattr(builtins, "__import__", blocked_relative_agent_import)
  monkeypatch.setattr(importlib.util, "spec_from_file_location", counted_spec)
  with _load_demo_init_module_direct(
      "agent_config_yaml", module_name, cleanup_module_names=(fallback_module_name,)
  ) as mod:
    assert hasattr(mod, "agent")
    root = mod.agent.root_agent
    assert root.name == "yaml_dice_workshop"
    assert "demos_10_agent_config_yaml_agent" in sys.modules
    tool_names = {
        getattr(tool, "name", getattr(tool, "__name__", "")) for tool in root.tools
    }
    assert tool_names == {"roll_die", "check_prime"}
  assert fallback_calls["count"] == 1
  assert fallback_module_name not in sys.modules


def test_agent_config_yaml_import_context_fallback_failure_leaks_no_agent_module(
    monkeypatch,
):
  import builtins
  from google.adk.agents import config_agent_utils

  module_name = "workshop_demo_10_agent_config_yaml_fallback_failure"
  fallback_module_name = "demos_10_agent_config_yaml_agent"
  original_import = builtins.__import__
  original_spec_from_file_location = importlib.util.spec_from_file_location
  fallback_calls = {"count": 0}
  failure_message = "dependency failure during agent load"

  def blocked_relative_agent_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "" and level == 1 and "agent" in fromlist:
      raise ModuleNotFoundError("No module named 'agent'", name="agent")
    return original_import(name, globals, locals, fromlist, level)

  def counted_spec(*args, **kwargs):
    if len(args) >= 1 and args[0] == fallback_module_name:
      fallback_calls["count"] += 1
    return original_spec_from_file_location(*args, **kwargs)

  def broken_from_config(*_args, **_kwargs):
    raise ImportError(failure_message)

  monkeypatch.setattr(builtins, "__import__", blocked_relative_agent_import)
  monkeypatch.setattr(config_agent_utils, "from_config", broken_from_config)
  monkeypatch.setattr(importlib.util, "spec_from_file_location", counted_spec)
  with pytest.raises(ImportError, match="dependency failure during agent load"):
    with _load_demo_init_module_direct(
        "agent_config_yaml",
        module_name,
        cleanup_module_names=(fallback_module_name,),
    ):
      pass
  assert fallback_calls["count"] == 1
  assert fallback_module_name not in sys.modules


def test_agent_config_yaml_import_context_and_error_propagation(monkeypatch):
  from google.adk.agents import config_agent_utils

  demo_path = _DEMOS_DIR / "agent_config_yaml" / "__init__.py"
  module_name = "workshop_demo_10_agent_config_yaml_broken_import"
  fallback_module_name = "demos_10_agent_config_yaml_agent"
  original_spec = importlib.util.spec_from_file_location
  fallback_calls = {"count": 0}

  def tracked_spec(*args, **kwargs):
    if len(args) >= 2 and Path(args[1]).name == "agent.py":
      fallback_calls["count"] += 1
    return original_spec(*args, **kwargs)

  def broken_from_config(*_args, **_kwargs):
    # Simulates a genuine dependency failure inside agent.py.
    raise ImportError("dependency failure")

  # Keep monkey patching scoped to this test and avoid leaking state.
  monkeypatch.setattr(config_agent_utils, "from_config", broken_from_config)
  monkeypatch.setattr(importlib.util, "spec_from_file_location", tracked_spec)

  with pytest.raises(ImportError, match="dependency failure"):
    with _load_demo_init_module_direct(
        "agent_config_yaml",
        module_name,
        cleanup_module_names=(fallback_module_name,),
        submodule_search_locations=[str(demo_path.parent)],
    ):
      pass
  assert fallback_calls["count"] == 0
  assert fallback_module_name not in sys.modules


def test_hitl_send_email_validation():
  mod = _load_demo_module("hitl_sensitive_action")
  assert mod.send_email(123, "topic", "hello") == (
      "Invalid recipient. Please provide a text email address."
  )
  assert mod.send_email("user@localhost", "topic", "hello") == (
      "Invalid recipient email. Please provide a valid email address."
  )
  assert mod.send_email("user@localhost@bad", "topic", "hello") == (
      "Invalid recipient email. Please provide a valid email address."
  )
  assert mod.send_email("user@example", "topic", "hello") == (
      "Invalid recipient email. Please provide a valid email address."
  )
  assert mod.send_email("user@.com", "topic", "hello") == (
      "Invalid recipient email. Please provide a valid email address."
  )
  assert mod.send_email("user@example.com", 123, "hello") == (
      "Invalid subject. Please provide the email subject as text."
  )
  assert mod.send_email("user@example.com", "   ", "hello") == (
      "Email subject is required."
  )
  assert mod.send_email("user@example.com", "topic", 123) == (
      "Invalid body. Please provide the email body as text."
  )
  assert mod.send_email("user@example.com", "topic", "   ") == (
      "Email body is required."
  )
  assert "(simulated) Email sent to 'user@example.com' with subject 'topic' — body: 'hello'." in (
      mod.send_email("user@example.com", "topic", "hello")
  )


def test_custom_tools_input_validation():
  mod = _load_demo_module("custom_tools")
  assert mod.get_weather(123) == {
      "status": "error",
      "error_message": "Invalid city value 123. Please provide a city name as text.",
  }
  assert mod.get_weather(None) == {
      "status": "error",
      "error_message": "Invalid city value None. Please provide a city name as text.",
  }
  assert mod.get_weather(float("nan")) == {
      "status": "error",
      "error_message": "Invalid city value nan. Please provide a city name as text.",
  }
  assert mod.get_weather(float("inf")) == {
      "status": "error",
      "error_message": "Invalid city value inf. Please provide a city name as text.",
  }
  assert mod.get_weather("   ") == {
      "status": "error",
      "error_message": "City value is empty. Please provide a city name.",
  }
  assert mod.get_weather(",") == {
      "status": "error",
      "error_message": "City value is empty. Please provide a city name.",
  }
  # All supported cities should return success
  for city in ("New York", "London", "Tokyo", "Chicago", "Los Angeles", "Paris"):
    assert mod.get_weather(city)["status"] == "success", f"Expected success for {city}"
  assert mod.get_weather("New York, TX")["status"] == "success"
  # Unsupported city should list supported options in the error message
  result = mod.get_weather("Atlantis")
  assert result["status"] == "error"
  assert "london" in result["error_message"].lower()

  assert mod.get_current_time(123) == {
      "status": "error",
      "error_message": "Invalid city value 123. Please provide a city name as text.",
  }
  assert mod.get_current_time(None) == {
      "status": "error",
      "error_message": "Invalid city value None. Please provide a city name as text.",
  }
  assert mod.get_current_time(float("-inf")) == {
      "status": "error",
      "error_message": "Invalid city value -inf. Please provide a city name as text.",
  }
  assert mod.get_current_time("") == {
      "status": "error",
      "error_message": "City value is empty. Please provide a city name.",
  }
  # All supported cities should return success
  for city in ("New York", "London", "Tokyo", "Chicago", "Los Angeles", "Paris"):
    assert mod.get_current_time(city)["status"] == "success", f"Expected success for {city}"
  assert mod.get_current_time("New York, TX")["status"] == "success"



def test_static_kb_input_validation():
  mod = _load_demo_module("static_kb_rag")
  assert (
      mod.search_company_kb(123)
      == "search_company_kb expects a text query. Please ask a question as plain text."
  )
  assert (
      mod.search_company_kb(None)
      == "search_company_kb expects a text query. Please ask a question as plain text."
  )
  assert (
      mod.search_company_kb("")
      == "Please enter a query with at least one keyword before searching."
  )
  assert (
      mod.search_company_kb("   ")
      == "Please enter a query with at least one keyword before searching."
  )


def test_session_memory_input_validation():
  mod = _load_demo_module("session_memory")
  ctx = _DummyToolContext()

  assert mod.remember_display_name(123, ctx) == (
      "Invalid display name. Please provide a text name."
  )
  assert mod.remember_display_name(None, ctx) == (
      "Invalid display name. Please provide a text name."
  )
  assert mod.remember_display_name("   ", ctx) == (
      "Invalid display name. Name is required."
  )
  assert mod.recall_display_name(tool_context=ctx) == (
      "No display name is stored yet. Ask the user what to call them."
  )
  assert mod.remember_display_name("Ada", ctx) == (
      "Got it — I'll remember you as Ada for this session."
  )
  assert ctx.state.get("user_display_name") == "Ada"


def test_live_weather_input_validation():
  mod = _load_demo_module("live_weather_nws")
  with patch.object(mod, "requests") as mocked_requests:
    assert mod.get_live_forecast(None) == {
        "status": "error",
        "error_message": "Invalid city value None. Please provide a city name as text.",
    }
    assert mod.get_live_forecast(123) == {
        "status": "error",
        "error_message": "Invalid city value 123. Please provide a city name as text.",
    }
    assert mod.get_live_forecast("   ") == {
        "status": "error",
        "error_message": "City value is empty. Please provide a supported city.",
    }
    assert mod.get_live_forecast(",") == {
        "status": "error",
        "error_message": "City value is empty. Please provide a supported city.",
    }
    assert mod.get_live_forecast("  ,  ") == {
        "status": "error",
        "error_message": "City value is empty. Please provide a supported city.",
    }
    city_list = ", ".join(sorted(mod._COORDS))
    assert mod.get_live_forecast("AtLanTiS, WA") == {
        "status": "error",
        "error_message": f"Unsupported city 'atlantis'. Try: {city_list}.",
    }
    assert mod.get_live_forecast(float("nan")) == {
        "status": "error",
        "error_message": "Invalid city value nan. Please provide a city name as text.",
    }
    assert mod.get_live_forecast(float("inf")) == {
        "status": "error",
        "error_message": "Invalid city value inf. Please provide a city name as text.",
    }
    assert not mocked_requests.get.called

  # Normalize comma-separated input for supported cities.
  assert mod.get_live_forecast("Austin, TX")["status"] == "success"


def test_live_weather_external_error_contracts():
  mod = _load_demo_module("live_weather_nws")

  with patch.object(mod.requests, "get", side_effect=requests.Timeout("timeout")) as mocked:
    result = mod.get_live_forecast("Austin")
    assert result["status"] == "error"
    assert result["error_message"].startswith("Unable to fetch forecast metadata:")

  assert mocked.call_count == 1

  with patch.object(
      mod.requests,
      "get",
      side_effect=[
          _FakeResponse(
              payload={"properties": {"forecast": "https://api.weather.gov/forecast"}}
          ),
          requests.Timeout("timeout"),
      ],
  ) as mocked:
    result = mod.get_live_forecast("Austin")
    assert result["status"] == "error"
    assert result["error_message"].startswith("Unable to fetch forecast details:")

  assert mocked.call_count == 2

  with patch.object(
      mod.requests,
      "get",
      side_effect=[
          _FakeResponse(payload={"wrong": "shape"}),
          _FakeResponse(payload={}),
      ],
  ):
    result = mod.get_live_forecast("Austin")
    assert result["status"] == "error"
    assert result["error_message"].startswith("Invalid forecast metadata response:")

  with patch.object(
      mod.requests,
      "get",
      side_effect=[
          _FakeResponse(payload={"properties": {}}),
      ],
  ):
    result = mod.get_live_forecast("Austin")
    assert result["status"] == "error"
    assert result["error_message"] == (
        "Forecast metadata is missing a forecast URL."
    )

  with patch.object(
      mod.requests,
      "get",
      side_effect=[
          _FakeResponse(payload={"properties": {"forecast": "https://api.weather.gov/forecast"}}),
          _FakeResponse(payload={"properties": {"periods": "not-a-list"}}),
      ],
  ):
    result = mod.get_live_forecast("Austin")
    assert result["status"] == "error"
    assert result["error_message"] == (
        "Invalid forecast response format: periods must be a list."
    )

  with patch.object(
      mod.requests,
      "get",
      side_effect=[
          _FakeResponse(payload={"properties": {"forecast": "https://api.weather.gov/forecast"}}),
          _FakeResponse(json_error=ValueError("bad payload")),
      ],
  ):
    result = mod.get_live_forecast("Austin")
    assert result["status"] == "error"
    assert result["error_message"].startswith("Invalid forecast response format:")


def test_parallel_research_city_validation():
  mod = _load_demo_module("parallel_research_synth")
  assert mod.research_museums(123) == (
      "Invalid city input. Please provide a city name."
  )
  assert mod.research_events("") == "Invalid city input. Please provide a city name."
  assert mod.research_food("  ,  ") == "Invalid city input. Please provide a city name."
  assert mod.research_food("   ") == "Invalid city input. Please provide a city name."
  assert mod.research_museums("Austin, TX") == (
      "Museums in Austin: City Heritage Museum (permanent exhibits), Science Pavilion (interactive)."
  )
  assert "Museums in Austin" in mod.research_museums("Austin")


def test_multi_agent_tool_validation():
  mod = _load_demo_module("multi_agent_coordinator")
  assert mod.roll_die("abc") == "Invalid number of sides. Please provide a whole number."
  assert mod.roll_die(True) == "Invalid number of sides. Please provide a whole number."
  assert mod.roll_die(1.2) == "Invalid number of sides. Please provide a whole number."
  assert mod.roll_die(float("inf")) == (
      "Invalid number of sides. Please provide a whole number."
  )
  assert mod.roll_die(float("nan")) == (
      "Invalid number of sides. Please provide a whole number."
  )
  assert mod.roll_die(1) == (
      "Invalid number of sides. Please provide an integer greater than 1."
  )
  assert mod.roll_die(-1) == (
      "Invalid number of sides. Please provide an integer greater than 1."
  )
  assert mod.roll_die(10001) == (
      "Invalid number of sides. Please use a number between 2 and 10000."
  )
  assert mod.check_prime("not a list") == (
      "Invalid input: check_prime expects a list of integers."
  )
  assert mod.check_prime(True) == (
      "Invalid input: check_prime expects a list of integers."
  )
  assert mod.check_prime([]) == "No prime numbers found."
  assert mod.check_prime([0, 1, -1, 4]) == "No prime numbers found."
  assert mod.check_prime([7, 7, 2, 8, 13, 13, 4]) == (
      "2, 7, 13 are prime numbers."
  )
  assert "Invalid prime candidate" in mod.check_prime([2.2])
  assert "Invalid prime candidate" in mod.check_prime([float("inf")])
  assert "Invalid prime candidate" in mod.check_prime([float("nan")])


def test_yaml_tool_validation():
  mod = _load_demo_tools_module("agent_config_yaml")
  assert mod.roll_die("abc") == "Invalid number of sides. Please provide a whole number."
  assert mod.roll_die(True) == "Invalid number of sides. Please provide a whole number."
  assert mod.roll_die(1.2) == "Invalid number of sides. Please provide a whole number."
  assert mod.roll_die(float("inf")) == (
      "Invalid number of sides. Please provide a whole number."
  )
  assert mod.roll_die(float("nan")) == (
      "Invalid number of sides. Please provide a whole number."
  )
  assert mod.roll_die(0) == (
      "Invalid number of sides. Please provide an integer greater than 1."
  )
  assert mod.roll_die(-1) == (
      "Invalid number of sides. Please provide an integer greater than 1."
  )
  assert mod.roll_die(10001) == (
      "Invalid number of sides. Please use a number between 2 and 10000."
  )
  assert mod.check_prime("not a list") == (
      "Invalid input: check_prime expects a list of integers."
  )
  assert mod.check_prime(True) == (
      "Invalid input: check_prime expects a list of integers."
  )
  assert mod.check_prime([]) == "No prime numbers found."
  assert mod.check_prime([4, 1, -3, 9]) == "No prime numbers found."
  assert mod.check_prime([13, 13, 2, 2, 7, 4]) == (
      "2, 7, 13 are prime numbers."
  )
  assert "Invalid prime candidate" in mod.check_prime([2.2])
  assert "Invalid prime candidate" in mod.check_prime([float("inf")])
  assert "Invalid prime candidate" in mod.check_prime([float("nan")])
