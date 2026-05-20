"""Beginner demo: four arithmetic tools showing the core ADK function-tool pattern.

KEY CONCEPT — How ADK converts a Python function into a Gemini tool:
  1. Function name       → tool name (the model uses this to select the right tool).
  2. Parameter type hints → JSON schema sent to Gemini for input validation.
  3. Docstring (Args)    → natural-language descriptions Gemini reads to fill arguments.
  4. Return value        → passed back to the model as the tool's result.

No decorators or registration calls needed — just list functions in tools=[].
"""

import math

# Agent is the main building block in ADK — it wraps a Gemini model with tools and instructions.
from google.adk import Agent


# --- Tool functions ---
# Any regular Python function can become an agent "tool".
# ADK reads the function name, type hints, and docstring to build a tool schema for the model.
# The model decides WHEN to call the tool; Python actually runs it.

def _coerce_float(value: object) -> float | None:
  """Try converting an input to float for tool numeric arguments."""
  if isinstance(value, bool):
    return None
  try:
    number = float(value)
  except (TypeError, ValueError):
    return None
  if not math.isfinite(number):
    return None
  return number


def add_numbers(a: float, b: float) -> float | str:
  """Add two numbers.

  Args:
      a: First operand.
      b: Second operand.

  Returns:
      Sum of a and b, or an error message if inputs are invalid.
  """
  left = _coerce_float(a)
  right = _coerce_float(b)
  if left is None or right is None:
    return "Invalid input: add_numbers expects two numeric values."

  # Simply return the sum — the agent will show this result to the user.
  return left + right


def multiply_numbers(a: float, b: float) -> float | str:
  """Multiply two numbers.

  Args:
      a: First operand.
      b: Second operand.

  Returns:
      Product of a and b, or an error message if inputs are invalid.
  """
  left = _coerce_float(a)
  right = _coerce_float(b)
  if left is None or right is None:
    return "Invalid input: multiply_numbers expects two numeric values."

  # Simply return the product — the agent will show this result to the user.
  return left * right


def subtract_numbers(a: float, b: float) -> float | str:
  """Subtract the second number from the first.

  Args:
      a: Number to subtract from (minuend).
      b: Number to subtract (subtrahend).

  Returns:
      Difference a − b, or an error message if inputs are invalid.
  """
  left = _coerce_float(a)
  right = _coerce_float(b)
  if left is None or right is None:
    return "Invalid input: subtract_numbers expects two numeric values."
  return left - right


def divide_numbers(a: float, b: float) -> float | str:
  """Divide the first number by the second.

  Args:
      a: Dividend (number to divide).
      b: Divisor (number to divide by). Must not be zero.

  Returns:
      Quotient a ÷ b, or an error message if inputs are invalid or b is zero.
  """
  left = _coerce_float(a)
  right = _coerce_float(b)
  if left is None or right is None:
    return "Invalid input: divide_numbers expects two numeric values."
  # Guard against division by zero — Python raises ZeroDivisionError without this check.
  if right == 0:
    return "Cannot divide by zero."
  return left / right


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
        "You are a calculator assistant. Use add_numbers, subtract_numbers, "
        "multiply_numbers, and divide_numbers for any arithmetic the user asks. "
        "Always call a tool for every calculation — do not compute in your head. "
        "If the user requests multiple operations, chain the tool calls as needed."
    ),

    # tools: All four arithmetic functions. ADK converts each to a Gemini tool automatically.
    tools=[add_numbers, subtract_numbers, multiply_numbers, divide_numbers],
)
