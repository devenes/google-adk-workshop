"""Minimal ADK agent for first `adk web` run (workshop)."""

from google.adk import Agent

root_agent = Agent(
    name="hello_workshop_agent",
    model="gemini-2.5-flash",
    description="A minimal assistant for introducing ADK Web.",
    instruction=(
        "You are a friendly workshop assistant. Keep answers concise and practical. "
        "When asked about ADK, explain it as a code-first Python framework for building "
        "agents with tools, sessions, and optional multi-agent orchestration."
    ),
)
