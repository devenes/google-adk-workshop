"""Multi-agent workshop demo: coordinator delegates to specialists."""

import random

from google.adk import Agent
from google.genai import types


def roll_die(sides: int) -> int:
  """Roll a die with the given number of sides and return the outcome."""
  return random.randint(1, sides)


def check_prime(nums: list[int]) -> str:
  """Check which numbers in the list are prime."""
  primes = set()
  for number in nums:
    number = int(number)
    if number <= 1:
      continue
    is_prime = True
    for i in range(2, int(number**0.5) + 1):
      if number % i == 0:
        is_prime = False
        break
    if is_prime:
      primes.add(number)
  if not primes:
    return "No prime numbers found."
  return f"{', '.join(str(n) for n in sorted(primes))} are prime numbers."


_dice_safety = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.OFF,
        ),
    ]
)

roll_agent = Agent(
    name="roll_agent",
    model="gemini-2.5-flash",
    description="Rolls dice with a requested number of sides.",
    instruction=(
        "When asked to roll a die, call roll_die with the number of sides as an "
        "integer. Report the numeric result clearly."
    ),
    tools=[roll_die],
    generate_content_config=_dice_safety,
)

prime_agent = Agent(
    name="prime_agent",
    model="gemini-2.5-flash",
    description="Checks primality for integers via the check_prime tool.",
    instruction=(
        "When asked about primes, call check_prime with a list of integers. "
        "Never guess primes without the tool."
    ),
    tools=[check_prime],
    generate_content_config=_dice_safety,
)

root_agent = Agent(
    name="dice_prime_coordinator",
    model="gemini-2.5-flash",
    description="Coordinates dice rolls and prime checks via sub-agents.",
    instruction="""
You delegate work to specialists:
- For rolling dice, rely on roll_agent.
- For prime checks, rely on prime_agent.
- If the user asks to roll then check primality, use roll_agent first, then
  prime_agent with the rolled value in a list.
Summarize outcomes clearly for the user.
""",
    sub_agents=[roll_agent, prime_agent],
    generate_content_config=_dice_safety,
)
