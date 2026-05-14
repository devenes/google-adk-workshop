# Module: agent_config_yaml
"""YAML-configured agent package for ADK Web."""

import importlib.util
import os
import sys

_FALLBACK_AGENT_MODULE_NAME = "demos_10_agent_config_yaml_agent"

def _should_fallback_for_import_error(exc: Exception) -> bool:
  """Return True only for import failures caused by package context.

  `adk eval` and direct module loaders may execute this file without package
  context, causing `from . import agent` to fail as `ValueError`. A direct
  `ModuleNotFoundError` for `agent` also indicates the same context issue.
  """
  if isinstance(exc, ModuleNotFoundError):
    return exc.name == "agent"
  return isinstance(exc, ValueError)


try:
  from . import agent
except (ModuleNotFoundError, ValueError) as exc:
  if not _should_fallback_for_import_error(exc):
    raise
  # Fallback for non-package execution contexts where `from . import agent`
  # would fail before package-relative import can be established
  # (for example, `google.adk` `adk eval` entry loading and module-loader tests).
  _agent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.py")
  _spec = importlib.util.spec_from_file_location(_FALLBACK_AGENT_MODULE_NAME, _agent_path)
  if _spec is None or _spec.loader is None:
    raise
  _agent_module = importlib.util.module_from_spec(_spec)
  sys.modules[_FALLBACK_AGENT_MODULE_NAME] = _agent_module
  try:
    _spec.loader.exec_module(_agent_module)
  except Exception:
    sys.modules.pop(_FALLBACK_AGENT_MODULE_NAME, None)
    raise
  agent = _agent_module
