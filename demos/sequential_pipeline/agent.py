"""Intermediate demo: SequentialAgent runs sub-agents in fixed order."""

# Agent is the standard single-model agent from ADK.
from google.adk import Agent

# SequentialAgent chains multiple agents so they run one after the other.
# Each sub-agent's output is added to the conversation before the next one starts.
from google.adk.agents import SequentialAgent


# --- Step 1: Outline Drafter ---
# This sub-agent runs FIRST. It receives the user's topic and creates a bullet-point outline.
_outline_agent = Agent(
    name="outline_drafter",       # Unique name for this sub-agent.
    model="gemini-2.5-flash",     # Gemini model powering this step.
    instruction=(
        # Tell the model to produce exactly 3 bullet points — no extra text.
        "Given the user's topic, output exactly 3 short bullet points as an "
        "outline only. No introduction or conclusion."
    ),
)

# --- Step 2: Detail Expander ---
# This sub-agent runs SECOND. It reads the outline already in the conversation
# (produced by _outline_agent) and expands it into a paragraph.
_expand_agent = Agent(
    name="detail_expander",       # Unique name for this sub-agent.
    model="gemini-2.5-flash",     # Gemini model powering this step.
    instruction=(
        # "prior outline from the conversation" — ADK passes the full conversation
        # history to each sub-agent, so this agent can see what _outline_agent wrote.
        "Read the prior outline from the conversation and expand it into one "
        "coherent short paragraph (under 120 words). Do not add new sections."
    ),
)

# --- Root Agent: SequentialAgent ---
# SequentialAgent is NOT a Gemini model — it is a workflow controller.
# It simply runs sub_agents in order: first _outline_agent, then _expand_agent.
root_agent = SequentialAgent(
    name="sequential_write_pipeline",

    # description: Tells orchestrators what this pipeline produces.
    description="First drafts bullets, then expands to a paragraph.",

    # sub_agents: The ordered list of agents to run. Order matters!
    sub_agents=[_outline_agent, _expand_agent],
)
