"""Tools referenced from root_agent.yaml (Agent Config)."""

# random is Python's standard library for generating random numbers.
import random


def roll_die(sides: int) -> int:
  """Roll an N-sided die (demo).

  Args:
      sides: Number of sides (integer >= 2).

  Returns:
      The roll result.
  """
  # Ensure the die has at least 2 sides; max(2, ...) prevents invalid single-sided dice.
  s = max(2, int(sides))

  # Return a random integer between 1 and s (both endpoints included).
  return random.randint(1, s)


def check_prime(nums: list[int]) -> str:
  """Return which integers in the list are prime."""
  primes = []  # Collect all prime numbers found in the input list.

  for n in nums:
    # Cast to int in case floats are passed (e.g., 7.0 instead of 7).
    n = int(n)

    # Numbers less than 2 (0, 1, negatives) are not prime by definition.
    if n < 2:
      continue

    # all(...) returns True only if n is not divisible by ANY i in the range [2, √n].
    # If all() is True, no divisor was found → n is prime.
    if all(n % i for i in range(2, int(n**0.5) + 1)):
      primes.append(n)

  # Return "None" if no primes were found, or a comma-separated list of primes.
  return "None" if not primes else ", ".join(str(p) for p in primes)
