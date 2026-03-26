"""Expert demo: ParallelAgent (stub researchers) → synthesis agent.

Aligns with “Parallel Power with ParallelAgent” in
``notebooks/ADK_Learning_tool_multi_agents.ipynb``. Uses stub tools instead of
Search so concurrency is easy to demonstrate without extra API setup.
"""

from google.adk import Agent
from google.adk.agents import ParallelAgent, SequentialAgent


def research_museums(city: str) -> str:
  """Return demo museum picks for a city.

  Args:
      city: City to research.

  Returns:
      Short text snippet for the synthesis step.
  """
  return (
      f"Museums in {city}: City Heritage Museum (permanent exhibits), "
      f"Science Pavilion (interactive)."
  )


def research_events(city: str) -> str:
  """Return demo weekend-style events for a city."""
  return (
      f"Events in {city}: Riverfront jazz (Sat evening), makers market (Sun AM)."
  )


def research_food(city: str) -> str:
  """Return demo dining notes for a city."""
  return (
      f"Dining in {city}: Central Market Hall food stalls, Garden District bistro."
  )


_museum_agent = Agent(
    name="museum_agent",
    model="gemini-2.5-flash",
    tools=[research_museums],
    instruction=(
        "Call research_museums with the city the user cares about (infer from "
        "their message if needed). Summarize the tool result in one sentence."
    ),
    output_key="museum_result",
)

_events_agent = Agent(
    name="events_agent",
    model="gemini-2.5-flash",
    tools=[research_events],
    instruction=(
        "Call research_events for the user's city. One-sentence summary."
    ),
    output_key="events_result",
)

_food_agent = Agent(
    name="food_agent",
    model="gemini-2.5-flash",
    tools=[research_food],
    instruction=(
        "Call research_food for the user's city. One-sentence summary."
    ),
    output_key="food_result",
)

_parallel_block = ParallelAgent(
    name="parallel_city_research",
    sub_agents=[_museum_agent, _events_agent, _food_agent],
)

_synthesis = Agent(
    name="synthesis_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You combine parallel research into one Markdown answer for the user.\n"
        "Museums:\n{museum_result}\n\nEvents:\n{events_result}\n\nFood:\n"
        "{food_result}\n\nUse ## sections and bullets. Add a one-line intro."
    ),
)

root_agent = SequentialAgent(
    name="parallel_then_synthesize",
    description="Runs three researchers in parallel, then merges results.",
    sub_agents=[_parallel_block, _synthesis],
)
