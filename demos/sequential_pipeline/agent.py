"""Intermediate demo: SequentialAgent runs sub-agents in fixed order."""

from google.adk import Agent
from google.adk.agents import SequentialAgent

_outline_agent = Agent(
    name="outline_drafter",
    model="gemini-2.5-flash",
    instruction=(
        "Given the user's topic, output exactly 3 short bullet points as an "
        "outline only. No introduction or conclusion."
    ),
)

_expand_agent = Agent(
    name="detail_expander",
    model="gemini-2.5-flash",
    instruction=(
        "Read the prior outline from the conversation and expand it into one "
        "coherent short paragraph (under 120 words). Do not add new sections."
    ),
)

root_agent = SequentialAgent(
    name="sequential_write_pipeline",
    description="First drafts bullets, then expands to a paragraph.",
    sub_agents=[_outline_agent, _expand_agent],
)
