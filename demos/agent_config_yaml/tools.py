"""Tools referenced from root_agent.yaml (Agent Config)."""

import random


def roll_die(sides: int) -> int:
  """Roll an N-sided die (demo).

  Args:
      sides: Number of sides (integer >= 2).

  Returns:
      The roll result.
  """
  s = max(2, int(sides))
  return random.randint(1, s)


def check_prime(nums: list[int]) -> str:
  """Return which integers in the list are prime."""
  primes = []
  for n in nums:
    n = int(n)
    if n < 2:
      continue
    if all(n % i for i in range(2, int(n**0.5) + 1)):
      primes.append(n)
  return "None" if not primes else ", ".join(str(p) for p in primes)
