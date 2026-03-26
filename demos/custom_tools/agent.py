"""Custom function tools (workshop) — deterministic stubs + schema from type hints."""

import datetime
from zoneinfo import ZoneInfo

from google.adk import Agent


def get_weather(city: str) -> dict:
  """Retrieve a canned weather report for a city (demo stub).

  Args:
      city: City name.

  Returns:
      dict with ``status`` and either ``report`` or ``error_message``.
  """
  if city.lower() == "new york":
    return {
        "status": "success",
        "report": (
            "The weather in New York is sunny with a temperature of 25 °C "
            "(77 °F)."
        ),
    }
  return {
      "status": "error",
      "error_message": f"Weather information for '{city}' is not available.",
  }


def get_current_time(city: str) -> dict:
  """Return the current time for a supported city (demo).

  Args:
      city: City name.

  Returns:
      dict with ``status`` and either ``report`` or ``error_message``.
  """
  if city.lower() == "new york":
    tz_identifier = "America/New_York"
  else:
    return {
        "status": "error",
        "error_message": f"No timezone mapping for '{city}'.",
    }

  tz = ZoneInfo(tz_identifier)
  now = datetime.datetime.now(tz)
  report = (
      f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
  )
  return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_workshop_agent",
    model="gemini-2.5-flash",
    description="Answers questions about time and weather using function tools.",
    instruction=(
        "Use the tools to answer. For weather or time, call the right tool. "
        "If a tool returns an error, explain it clearly. "
        "You may call both tools when the user asks for both."
    ),
    tools=[get_weather, get_current_time],
)
