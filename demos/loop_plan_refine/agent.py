"""Expert demo: planner → LoopAgent(critic ↔ refiner) with exit_loop (no Search).

Mirrors the "Iterative Ideas with LoopAgent" section in
``notebooks/ADK_Learning_tool_multi_agents.ipynb`` with a smaller, classroom-safe
loop (no live web lookup required).
"""

# Agent is the standard single-model agent.
from google.adk import Agent

# LoopAgent runs its sub_agents repeatedly until exit_loop is called or max_iterations is hit.
# SequentialAgent chains multiple agents to run one after the other.
from google.adk.agents import LoopAgent, SequentialAgent

# exit_loop is a built-in ADK tool. When an agent calls it, the surrounding LoopAgent stops.
from google.adk.tools import exit_loop

# _COMPLETION_PHRASE is the agreed signal between the critic and the refiner.
# When the critic outputs exactly this phrase, the refiner knows the plan is good enough
# and calls exit_loop to stop the iteration cycle.
_COMPLETION_PHRASE = "PLAN_OK"

# --- Step 1: Planner ---
# Runs once at the start (outside the loop). Creates the first draft plan.
_planner = Agent(
    name="planner_agent",
    model="gemini-2.5-flash",
    instruction=(
        # Constrains output to exactly two bullet lines for easy parsing by the critic.
        "Draft a short plan for the user's goal as exactly two bullet lines, "
        "each starting with '- '. Keep each line under 15 words."
    ),
    # output_key saves this agent's text response into session state["current_plan"].
    # The critic reads it via {current_plan} in its instruction below.
    output_key="current_plan",
)

# --- Loop Sub-Agent 1: Critic ---
# Runs inside the loop. Reads the current plan and either approves it or gives feedback.
_critic = Agent(
    name="critic_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You review plans for clarity.\n"
        # {current_plan} is replaced by ADK with the value from session state before this runs.
        "Current plan:\n{current_plan}\n\n"
        f"If the plan has at least two lines starting with '- ' and they "
        f"describe distinct steps, reply with this exact text and nothing "
        # _COMPLETION_PHRASE is the exit signal — the refiner watches for this exact string.
        f"else: {_COMPLETION_PHRASE}\n"
        "Otherwise reply with one short sentence describing what to fix."
    ),
    # output_key saves the critic's verdict into session state["criticism"].
    output_key="criticism",
)

# --- Loop Sub-Agent 2: Refiner ---
# Runs inside the loop after the critic. Either exits the loop or rewrites the plan.
_refiner = Agent(
    name="refiner_agent",
    model="gemini-2.5-flash",
    # exit_loop is a special ADK tool: calling it signals the LoopAgent to stop iterating.
    tools=[exit_loop],
    instruction=(
        # {criticism} and {current_plan} are injected from session state by ADK.
        "Critique:\n{criticism}\nPrior plan:\n{current_plan}\n\n"
        f"If the critique is exactly {_COMPLETION_PHRASE}, you MUST call the "
        "exit_loop tool once and produce no other text.\n"
        "Otherwise output a revised two-bullet plan (same format as before) "
        "do not call exit_loop."
        # output_key overwrites current_plan with the refined version for the next iteration.
    ),
    output_key="current_plan",  # Updated plan is saved back for the next critic pass.
)

# --- Loop: Critic + Refiner iterate together ---
# LoopAgent repeats [_critic, _refiner] until exit_loop is called or max_iterations is reached.
_refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[_critic, _refiner],  # Order matters: critic runs first each iteration.
    max_iterations=3,                # Safety cap — prevents infinite loops in the demo.
)

# --- Root Agent: Full Pipeline ---
# SequentialAgent first runs the planner (once), then enters the refinement loop.
root_agent = SequentialAgent(
    name="iterative_plan_workshop",
    description="Plans, critiques, and refines until PLAN_OK or max iterations.",
    # sub_agents run in order: planner creates the first draft, loop refines it.
    sub_agents=[_planner, _refinement_loop],
)
