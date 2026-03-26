"""Sequential pipeline: first agent writes output_key, second reads {placeholder}."""

# Agent is the standard single-model agent from ADK.
from google.adk import Agent

# SequentialAgent chains multiple agents so they run one after the other in order.
from google.adk.agents import SequentialAgent


# --- Step 1: Destination Picker ---
# output_key tells ADK to save this agent's final text response into session state
# under the key "destination". Other agents can then read it via {destination}.
_pick_spot = Agent(
    name="pick_destination",
    model="gemini-2.5-flash",
    instruction=(
        # The model should extract exactly one destination name and output it as plain text.
        "From the user's message, pick one specific venue or neighborhood name they "
        "want to go to. Reply with only that name (a few words), no quotes or extra text."
    ),
    # output_key: ADK writes this agent's response to state["destination"] automatically.
    output_key="destination",
)

# --- Step 2: Navigation Helper ---
# {destination} is a placeholder. Before this agent runs, ADK replaces {destination}
# in the instruction string with the value saved by _pick_spot's output_key.
_navigate = Agent(
    name="navigate_there",
    model="gemini-2.5-flash",
    instruction=(
        # ADK injects the saved destination here before the model sees this instruction.
        "The chosen destination is: {destination}\n"
        "Give short, practical directions or transit hints from a plausible starting "
        "point the user mentioned, or from 'downtown' if they did not specify a start."
    ),
    # No output_key needed here — this is the final step, so we just show the result.
)

# --- Root Agent: SequentialAgent ---
# SequentialAgent runs _pick_spot first, then _navigate.
# State is automatically shared between steps via output_key + {placeholder} injection.
root_agent = SequentialAgent(
    name="sequential_state_shared",

    # description: Explains the pipeline's purpose to orchestrators.
    description="Demonstrates output_key and instruction placeholders between steps.",

    # sub_agents: Run in this exact order — pick destination, then navigate there.
    sub_agents=[_pick_spot, _navigate],
)
