"""Beginner demo: numeric tools only (no external APIs)."""

from google.adk import Agent


def add_numbers(a: float, b: float) -> float:
  """Add two numbers.

  Args:
      a: First operand.
      b: Second operand.

  Returns:
      Sum of a and b.
  """
  return a + b


def multiply_numbers(a: float, b: float) -> float:
  """Multiply two numbers.

  Args:
      a: First operand.
      b: Second operand.

  Returns:
      Product of a and b.
  """
  return a * b


root_agent = Agent(
    name="calculator_basics_agent",
    model="gemini-2.5-flash",
    description="Adds and multiplies numbers using tools (workshop beginner demo).",
    instruction=(
        "You are a calculator assistant. For any arithmetic the user asks, "
        "call add_numbers and/or multiply_numbers. Do not invent results."
    ),
    tools=[add_numbers, multiply_numbers],
)
