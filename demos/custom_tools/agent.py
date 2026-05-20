"""Beginner demo: custom function tools with type hints, docstrings, and real timezone support.

This demo shows the two most important properties of ADK function tools:
  1. The schema (parameter names + types + docstring) is auto-generated for Gemini.
  2. Tools return structured dicts so the agent can forward success/error cleanly.
"""

# datetime is the standard Python module for working with dates and times.
import datetime

# ZoneInfo lets us convert a time to a specific timezone (e.g. "America/New_York").
from zoneinfo import ZoneInfo

# Agent is the main ADK class that connects a Gemini model to tools and instructions.
from google.adk import Agent


def _normalize_city(city: object) -> str:
  """Normalize user-entered city text for deterministic validation and matching."""
  if not isinstance(city, str):
    return ""
  city = city.strip()
  if not city:
    return ""
  city = city.split(",", 1)[0].strip()
  if not city:
    return ""
  return city


# --- Supported weather data ---
# Hardcoded weather stubs by lowercase city name.
# A real implementation would call an API like OpenWeatherMap or NWS.
# Stubs let learners see the tool-call flow without needing any API key.
_WEATHER_STUBS: dict[str, str] = {
    "new york":    "Sunny, 25 °C (77 °F). Light breeze.",
    "london":      "Overcast, 14 °C (57 °F). Chance of drizzle.",
    "tokyo":       "Partly cloudy, 22 °C (72 °F). Humid.",
    "chicago":     "Windy, 18 °C (64 °F). Clear skies.",
    "los angeles": "Sunny, 28 °C (82 °F). Low humidity.",
    "paris":       "Cloudy, 17 °C (63 °F). Light rain expected.",
}

# --- Supported timezone data ---
# Map of lowercase city names to IANA timezone identifiers.
# ZoneInfo requires these exact strings — see:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
_TIMEZONES: dict[str, str] = {
    "new york":    "America/New_York",
    "london":      "Europe/London",
    "tokyo":       "Asia/Tokyo",
    "chicago":     "America/Chicago",
    "los angeles": "America/Los_Angeles",
    "paris":       "Europe/Paris",
}


# --- Tool: get_weather ---
# This is a "stub" tool — it returns a hardcoded answer instead of calling a real weather API.
# Stubs are great for learning because they always produce predictable results.
def get_weather(city: str) -> dict:
  """Retrieve a canned weather report for a city (demo stub).

  Args:
      city: City name.

  Returns:
      dict with ``status`` and either ``report`` or ``error_message``.
  """
  city_value = _normalize_city(city)
  if not city_value:
    if not isinstance(city, str):
      return {
        "status": "error",
        "error_message": (
          f"Invalid city value {city!r}. Please provide a city name as text."
        ),
      }
    return {
      "status": "error",
      "error_message": (
        "City value is empty. Please provide a city name."
      ),
    }

  report = _WEATHER_STUBS.get(city_value.lower())
  if report:
    return {"status": "success", "report": f"The weather in {city_value}: {report}"}

  # For any other city, return an error dict — the agent will explain this to the user.
  supported = ", ".join(sorted(_WEATHER_STUBS))
  return {
      "status": "error",
      "error_message": f"Weather information for '{city_value}' is not available. Supported cities: {supported}.",
  }


# --- Tool: get_current_time ---
# Returns the real current time for a supported city using Python's timezone library.
def get_current_time(city: str) -> dict:
  """Return the current time for a supported city (demo).

  Args:
      city: City name.

  Returns:
      dict with ``status`` and either ``report`` or ``error_message``.
  """
  city_value = _normalize_city(city)
  if not city_value:
    if not isinstance(city, str):
      return {
        "status": "error",
        "error_message": (
          f"Invalid city value {city!r}. Please provide a city name as text."
        ),
      }
    return {
      "status": "error",
      "error_message": (
        "City value is empty. Please provide a city name."
      ),
    }

  tz_identifier = _TIMEZONES.get(city_value.lower())
  if not tz_identifier:
    supported = ", ".join(sorted(_TIMEZONES))
    return {
        "status": "error",
        "error_message": f"No timezone mapping for '{city_value}'. Supported cities: {supported}.",
    }

  # Create a timezone object from the IANA identifier string.
  tz = ZoneInfo(tz_identifier)

  # Get the current date and time in that timezone.
  now = datetime.datetime.now(tz)

  # Format the time as a human-readable string, e.g. "2024-06-15 14:30:00 EDT-0400".
  report = (
      f'The current time in {city_value} is '
      f"{now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
  )

  # Return a success dict with the formatted time string.
  return {"status": "success", "report": report}


# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="weather_time_workshop_agent",

    # model: The Gemini model that decides which tool to call based on the user's message.
    model="gemini-2.5-flash-lite",

    # description: Short summary so orchestrators know when to delegate to this agent.
    description="Answers questions about time and weather using function tools.",

    # instruction: System prompt — permanent guidance given to the model every turn.
    instruction=(
        "Use the tools to answer. For weather or time, call the right tool. "
        "If a tool returns an error, explain it clearly. "
        "You may call both tools when the user asks for both."
    ),

    # tools: Python functions the model can call. ADK generates tool schemas from type hints.
    tools=[get_weather, get_current_time],
)
