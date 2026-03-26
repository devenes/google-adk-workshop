"""Expert demo: planner → LoopAgent(critic ↔ refiner) with exit_loop (no Search).

Mirrors the “Iterative Ideas with LoopAgent” section in
``notebooks/ADK_Learning_tool_multi_agents.ipynb`` with a smaller, classroom-safe
loop (no live web lookup required).
"""

from google.adk import Agent
from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.tools import exit_loop

_COMPLETION_PHRASE = "PLAN_OK"

_planner = Agent(
    name="planner_agent",
    model="gemini-2.5-flash",
    instruction=(
        "Draft a short plan for the user's goal as exactly two bullet lines, "
        "each starting with '- '. Keep each line under 15 words."
    ),
    output_key="current_plan",
)

_critic = Agent(
    name="critic_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You review plans for clarity.\n"
        "Current plan:\n{current_plan}\n\n"
        f"If the plan has at least two lines starting with '- ' and they "
        f"describe distinct steps, reply with this exact text and nothing "
        f"else: {_COMPLETION_PHRASE}\n"
        "Otherwise reply with one short sentence describing what to fix."
    ),
    output_key="criticism",
)

_refiner = Agent(
    name="refiner_agent",
    model="gemini-2.5-flash",
    tools=[exit_loop],
    instruction=(
        "Critique:\n{criticism}\nPrior plan:\n{current_plan}\n\n"
        f"If the critique is exactly {_COMPLETION_PHRASE}, you MUST call the "
        "exit_loop tool once and produce no other text.\n"
        "Otherwise output a revised two-bullet plan (same format as before) "
        "as plain text only—do not call exit_loop."
    ),
    output_key="current_plan",
)

_refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[_critic, _refiner],
    max_iterations=3,
)

root_agent = SequentialAgent(
    name="iterative_plan_workshop",
    description="Plans, critiques, and refines until PLAN_OK or max iterations.",
    sub_agents=[_planner, _refinement_loop],
)
