"""YAML-configured agent shim for ADK eval package loading."""

from __future__ import annotations

import os
import sys

from google.adk.agents import config_agent_utils

# Keep the local directory on module import path so `tools.*` entries in
# root_agent.yaml resolve to this folder when loaded from adk eval.
_AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _AGENT_DIR not in sys.path:
  sys.path.insert(0, _AGENT_DIR)

root_agent = config_agent_utils.from_config(os.path.join(_AGENT_DIR, "root_agent.yaml"))

