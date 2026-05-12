"""Tools referenced from root_agent.yaml (Agent Config)."""

# random is Python's standard library for generating random numbers.
import random
import math


def _coerce_int(value: object) -> int | None:
  """Try converting a value into an integer for safe tool arithmetic."""
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


def roll_die(sides: int) -> int | str:
  """Roll an N-sided die (demo).

  Args:
      sides: Number of sides (integer >= 2).

  Returns:
      The roll result.
  """
  sides_value = _coerce_int(sides)
  if sides_value is None:
    return "Invalid number of sides. Please provide a whole number."

  # Ensure the die has at least 2 sides.
  if sides_value < 2:
    return "Invalid number of sides. Please provide an integer greater than 1."

  # Keep bounds modest for deterministic playground demos.
  if sides_value > 10000:
    return "Invalid number of sides. Please use a number between 2 and 10000."

  # Return a random integer between 1 and s (both endpoints included).
  return random.randint(1, sides_value)


def check_prime(nums: list[int]) -> str:
  """Return which integers in the list are prime."""
  if not isinstance(nums, list):
    return "Invalid input: check_prime expects a list of integers."

  if not nums:
    return "No prime numbers found."

  # Use a set to deduplicate prime values while preserving deterministic output.
  primes = set()

  for n in nums:
    if isinstance(n, bool):
      return "Invalid prime candidate True/False. Please provide whole numbers only."
    try:
      n_value = float(n)
    except (TypeError, ValueError):
      return f"Invalid prime candidate {n!r}. Please provide numeric values only."
    if not math.isfinite(n_value):
      return f"Invalid prime candidate {n!r}. Please provide numeric values only."
    if not n_value.is_integer():
      return f"Invalid prime candidate {n!r}. Please use whole numbers for prime checks."

    n = int(n_value)

    # Numbers less than 2 (0, 1, negatives) are not prime by definition.
    if n < 2:
      continue

    # all(...) returns True only if n is not divisible by ANY i in the range [2, √n].
    # If all() is True, no divisor was found → n is prime.
    if all(n % i for i in range(2, int(n**0.5) + 1)):
      primes.add(n)

  # Return the shared no-prime contract or a sorted comma-separated list of primes.
  if not primes:
    return "No prime numbers found."
  return f"{', '.join(str(p) for p in sorted(primes))} are prime numbers."
