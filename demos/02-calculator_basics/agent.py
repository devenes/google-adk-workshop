"""Beginner demo: numeric tools only (no external APIs)."""

# Agent is the main building block in ADK — it wraps a Gemini model with tools and instructions.
from google.adk import Agent


# --- Tool functions ---
# Any regular Python function can become an agent "tool".
# ADK reads the function name, type hints, and docstring to build a tool schema for the model.
# The model decides WHEN to call the tool; Python actually runs it.

def add_numbers(a: float, b: float) -> float:
  """Add two numbers.

  Args:
      a: First operand.
      b: Second operand.

  Returns:
      Sum of a and b.
  """
  # Simply return the sum — the agent will show this result to the user.
  return a + b


def multiply_numbers(a: float, b: float) -> float:
  """Multiply two numbers.

  Args:
      a: First operand.
      b: Second operand.

  Returns:
      Product of a and b.
  """
  # Simply return the product — the agent will show this result to the user.
  return a * b


# --- Agent definition ---
# ADK looks for a variable named root_agent when you run `adk web` or `adk run`.
root_agent = Agent(
    # name: Unique label for this agent (shown in logs and multi-agent traces).
    name="calculator_basics_agent",

    # model: The Gemini model that reads the user's message and decides which tool to call.
    model="gemini-2.5-flash-lite",

    # description: Short summary used by orchestrator agents to decide when to delegate here.
    description="Adds and multiplies numbers using tools (workshop beginner demo).",

    # instruction: System-level instructions that shape the agent's behavior every turn.
    instruction=(
        "You are a calculator assistant. For any arithmetic the user asks, "
        "call add_numbers and/or multiply_numbers. Do not invent results."
    ),

    # tools: The list of Python functions the agent is allowed to call.
    # ADK automatically converts each function into a Gemini function-calling tool.
    tools=[add_numbers, multiply_numbers],
)
