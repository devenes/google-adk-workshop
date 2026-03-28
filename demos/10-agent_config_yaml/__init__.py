"""YAML-configured agent package for ADK Web."""
import os
import sys

# Add this directory to sys.path so the YAML's `tools.*` references resolve
# when adk web is run from the parent demos/ folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
