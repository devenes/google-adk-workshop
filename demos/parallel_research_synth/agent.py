"""Expert demo: ParallelAgent (stub researchers) → synthesis agent.

Aligns with "Parallel Power with ParallelAgent" in
``notebooks/ADK_Learning_tool_multi_agents.ipynb``. Uses stub tools instead of
Search so concurrency is easy to demonstrate without extra API setup.
"""

# Agent is the standard single-model agent from ADK.
from google.adk import Agent

# ParallelAgent runs all its sub_agents at the SAME TIME (concurrently).
# SequentialAgent runs sub_agents one after the other in order.
from google.adk.agents import ParallelAgent, SequentialAgent


# --- Stub Research Tools ---
# These functions return hardcoded text instead of calling a real API.
# In a production system you would replace them with live search calls.

def research_museums(city: str) -> str:
  """Return demo museum picks for a city.

  Args:
      city: City to research.

  Returns:
      Short text snippet for the synthesis step.
  """
  # Hardcoded demo data so students can see parallelism without needing API keys.
  return (
      f"Museums in {city}: City Heritage Museum (permanent exhibits), "
      f"Science Pavilion (interactive)."
  )


def research_events(city: str) -> str:
  """Return demo weekend-style events for a city."""
  # Different stub data from research_museums so each parallel branch looks distinct.
  return (
      f"Events in {city}: Riverfront jazz (Sat evening), makers market (Sun AM)."
  )


def research_food(city: str) -> str:
  """Return demo dining notes for a city."""
  return (
      f"Dining in {city}: Central Market Hall food stalls, Garden District bistro."
  )


# --- Parallel Sub-Agents ---
# Each agent below calls one stub tool and saves its result via output_key.
# Because they are inside a ParallelAgent, all three run concurrently.

_museum_agent = Agent(
    name="museum_agent",
    model="gemini-2.5-flash",
    tools=[research_museums],   # Can only call the museum stub.
    instruction=(
        "Call research_museums with the city the user cares about (infer from "
        "their message if needed). Summarize the tool result in one sentence."
    ),
    # output_key saves this agent's response to state["museum_result"] for the synthesis step.
    output_key="museum_result",
)

_events_agent = Agent(
    name="events_agent",
    model="gemini-2.5-flash",
    tools=[research_events],    # Can only call the events stub.
    instruction=(
        "Call research_events for the user's city. One-sentence summary."
    ),
    # output_key saves the result to state["events_result"].
    output_key="events_result",
)

_food_agent = Agent(
    name="food_agent",
    model="gemini-2.5-flash",
    tools=[research_food],      # Can only call the food stub.
    instruction=(
        "Call research_food for the user's city. One-sentence summary."
    ),
    # output_key saves the result to state["food_result"].
    output_key="food_result",
)

# --- Parallel Block ---
# ParallelAgent runs _museum_agent, _events_agent, and _food_agent simultaneously.
# All three output_keys are written to session state before the synthesis agent starts.
_parallel_block = ParallelAgent(
    name="parallel_city_research",
    # All three agents start at the same time — much faster than running them sequentially.
    sub_agents=[_museum_agent, _events_agent, _food_agent],
)

# --- Synthesis Agent ---
# Runs AFTER the parallel block. Reads all three results via {placeholders} and merges them.
_synthesis = Agent(
    name="synthesis_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You combine parallel research into one Markdown answer for the user.\n"
        # ADK replaces {museum_result}, {events_result}, {food_result} with the
        # values saved by the three parallel agents' output_key fields.
        "Museums:\n{museum_result}\n\nEvents:\n{events_result}\n\nFood:\n"
        "{food_result}\n\nUse ## sections and bullets. Add a one-line intro."
    ),
    # No output_key needed — this is the last step; its response goes directly to the user.
)

# --- Root Agent: Full Pipeline ---
# SequentialAgent first runs the parallel block (all 3 researchers at once),
# then runs the synthesis agent once all results are ready.
root_agent = SequentialAgent(
    name="parallel_then_synthesize",
    description="Runs three researchers in parallel, then merges results.",
    # Step 1: _parallel_block (runs 3 agents concurrently).
    # Step 2: _synthesis (combines the 3 results into one answer).
    sub_agents=[_parallel_block, _synthesis],
)
