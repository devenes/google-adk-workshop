"""Multi-agent workshop demo: coordinator delegates to specialists."""

# --- Standard library imports ---
import math    # For math.isfinite() — guards against nan/inf inputs.
import random  # For random.randint() — used in roll_die.

# --- Third-party / ADK imports ---
# Agent is the core ADK class for building individual agents.
from google.adk import Agent

# types from google.genai lets us configure safety filters and content generation settings.
from google.genai import types


# --- Private helpers ---
# _coerce_int converts loosely-typed inputs to a clean Python int.
# It is a private helper (not a tool) — learners should not list it in tools=[].

def _coerce_int(value: object) -> int | None:
  """Try converting a value into an integer for safe tool arithmetic.

  Rejects booleans (True/False would otherwise coerce to 1/0),
  non-numeric types, NaN, Infinity, and fractional values.

  Returns:
      A plain int, or None if the conversion is not safe.
  """
  if isinstance(value, bool):
    return None
  try:
    number = float(value)
  except (TypeError, ValueError):
    return None
  if not math.isfinite(number):
    return None
  if not number.is_integer():
    return None
  return int(number)


# --- Tool: roll_die ---
def roll_die(sides: int) -> int | str:
  """Roll a die with the given number of sides and return the outcome."""
  sides_value = _coerce_int(sides)
  if sides_value is None:
    return "Invalid number of sides. Please provide a whole number."

  # Ensure the die has at least two sides.
  if sides_value < 2:
    return "Invalid number of sides. Please provide an integer greater than 1."

  # Keep bounds modest to avoid pathological inputs.
  if sides_value > 10000:
    return "Invalid number of sides. Please use a number between 2 and 10000."

  # random.randint(a, b) returns an integer N such that a <= N <= b (both ends inclusive).
  return random.randint(1, sides_value)


# --- Tool: check_prime ---
def check_prime(nums: list[int]) -> str:
  """Check which numbers in the list are prime.

  Args:
      nums: List of integers to test for primality. Must be a list;
            booleans and non-integer floats are rejected individually.

  Returns:
      A comma-separated string of primes found, e.g. '2, 3, 5 are prime numbers.',
      or 'No prime numbers found.' if none qualify.
  """
  if not isinstance(nums, list):
    return "Invalid input: check_prime expects a list of integers."

  if not nums:
    return "No prime numbers found."

  # A set is used to avoid duplicates if the same number appears twice.
  primes = set()

  for number in nums:
    if isinstance(number, bool):
      return "Invalid prime candidate True/False. Please provide whole numbers only."
    try:
      number_value = float(number)
    except (TypeError, ValueError):
      return f"Invalid prime candidate {number!r}. Please provide numeric values only."
    if not math.isfinite(number_value):
      return f"Invalid prime candidate {number!r}. Please provide numeric values only."
    if not number_value.is_integer():
      return f"Invalid prime candidate {number!r}. Please use whole numbers for prime checks."

    number = int(number_value)

    # Numbers <= 1 are not prime by definition (0, 1, and negatives are excluded).
    if number <= 1:
      continue

    # Assume prime until we find a divisor.
    is_prime = True

    # Trial division: check all integers from 2 up to √number.
    # If any divides evenly, the number is composite (not prime).
    for i in range(2, int(number**0.5) + 1):
      if number % i == 0:
        is_prime = False
        break  # No need to keep checking — we already found a factor.

    # If no divisors were found, the number is prime.
    if is_prime:
      primes.add(number)

  # Return a human-readable result string for the agent to relay to the user.
  if not primes:
    return "No prime numbers found."
  return f"{', '.join(str(n) for n in sorted(primes))} are prime numbers."


# --- Safety Configuration ---
# GenerateContentConfig lets us tune how Gemini generates responses.
# Here we turn off the DANGEROUS_CONTENT safety filter so "roll a d20 and kill the dragon"
# type messages don't get blocked — common in tabletop-game demos.
_dice_safety = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            # HARM_CATEGORY_DANGEROUS_CONTENT covers topics like violence or weapons.
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            # OFF means: never block on this category. Appropriate for a classroom dice demo.
            threshold=types.HarmBlockThreshold.OFF,
        ),
    ]
)

# --- Specialist Agent: roll_agent ---
# This agent only knows how to roll dice. It is a sub-agent used by root_agent below.
roll_agent = Agent(
    name="roll_agent",
    model="gemini-2.5-flash-lite",
    description="Rolls dice with a requested number of sides.",
    instruction=(
        "When asked to roll a die, call roll_die with the number of sides as an "
        "integer. If the result is an integer, report it clearly. "
        "If the result is an error message, relay that message to the user."
    ),
    tools=[roll_die],                        # Only the dice-rolling tool.
    generate_content_config=_dice_safety,    # Apply relaxed safety settings.
)

# --- Specialist Agent: prime_agent ---
# This agent only knows how to check prime numbers.
prime_agent = Agent(
    name="prime_agent",
    model="gemini-2.5-flash-lite",
    description="Checks primality for integers via the check_prime tool.",
    instruction=(
        "When asked about primes, call check_prime with a list of integers. "
        "Never guess primes without the tool."
    ),
    tools=[check_prime],                     # Only the primality-checking tool.
    generate_content_config=_dice_safety,    # Same safety config for consistency.
)

# --- Root Agent: Coordinator ---
# root_agent is the main agent users talk to.
# It does NOT have any tools itself — instead it delegates work to the specialists above
# by listing them in sub_agents. ADK's coordinator model reads each specialist's description
# to decide which one to route the request to.
root_agent = Agent(
    name="dice_prime_coordinator",
    model="gemini-2.5-flash-lite",
    description="Coordinates dice rolls and prime checks via sub-agents.",
    instruction="""
You delegate work to specialists:
- For rolling dice, rely on roll_agent.
- For prime checks, rely on prime_agent.
- If the user asks to roll then check primality, use roll_agent first, then
  prime_agent with the rolled value in a list.
Summarize outcomes clearly for the user.
""",
    # sub_agents: The coordinator can delegate to any agent listed here.
    # The model picks the right specialist based on their description fields.
    sub_agents=[roll_agent, prime_agent],
    generate_content_config=_dice_safety,    # Apply to coordinator too.
)
