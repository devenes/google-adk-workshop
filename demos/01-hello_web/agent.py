"""Minimal ADK agent for first `adk web` run (workshop)."""

# Agent is the core class from the Google ADK library.
# Every ADK project needs at least one Agent to handle user messages.
from google.adk import Agent

# root_agent is the special variable name ADK looks for in this module.
# When you run `adk web` or `adk run`, it automatically finds and starts root_agent.
root_agent = Agent(
    # name: A unique identifier for this agent (used in logs and multi-agent setups).
    name="hello_workshop_agent",

    # model: Which Gemini model powers this agent's language understanding.
    # "gemini-2.5-flash-lite" is fast and cheap — great for learning.
    model="gemini-2.5-flash-lite",

    # description: A short summary of what this agent does.
    # Other agents can read this description to decide when to delegate work here.
    description="A minimal assistant for introducing ADK Web.",

    # instruction: The system prompt that shapes the agent's personality and behavior.
    # Think of it as permanent instructions the model always has in mind.
    instruction=(
        "You are a friendly workshop assistant. Keep answers concise and practical. "
        "When asked about ADK, explain it as a code-first Python framework for building "
        "agents with tools, sessions, and optional multi-agent orchestration."
    ),
    # No tools= here — this agent just chats, it cannot call any Python functions.
)
