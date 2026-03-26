"""Sequential pipeline: first agent writes output_key, second reads {placeholder}."""

from google.adk import Agent
from google.adk.agents import SequentialAgent

# Step 1: choose a single destination string for downstream steps.
_pick_spot = Agent(
    name="pick_destination",
    model="gemini-2.5-flash",
    instruction=(
        "From the user's message, pick one specific venue or neighborhood name they "
        "want to go to. Reply with only that name (a few words), no quotes or extra text."
    ),
    output_key="destination",
)

# Step 2: ADK injects state['destination'] into {destination} in the instruction.
_navigate = Agent(
    name="navigate_there",
    model="gemini-2.5-flash",
    instruction=(
        "The chosen destination is: {destination}\n"
        "Give short, practical directions or transit hints from a plausible starting "
        "point the user mentioned, or from 'downtown' if they did not specify a start."
    ),
)

root_agent = SequentialAgent(
    name="sequential_state_shared",
    description="Demonstrates output_key and instruction placeholders between steps.",
    sub_agents=[_pick_spot, _navigate],
)
