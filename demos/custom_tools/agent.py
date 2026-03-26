"""Custom function tools (workshop) — deterministic stubs + schema from type hints."""

# datetime is the standard Python module for working with dates and times.
import datetime

# ZoneInfo lets us convert a time to a specific timezone (e.g. "America/New_York").
from zoneinfo import ZoneInfo

# Agent is the main ADK class that connects a Gemini model to tools and instructions.
from google.adk import Agent


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
  # Convert city to lowercase so "New York", "new york", "NEW YORK" all match.
  if city.lower() == "new york":
    # Return a success dict with the canned weather report string.
    return {
        "status": "success",
        "report": (
            "The weather in New York is sunny with a temperature of 25 °C "
            "(77 °F)."
        ),
    }
  # For any other city, return an error dict — the agent will explain this to the user.
  return {
      "status": "error",
      "error_message": f"Weather information for '{city}' is not available.",
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
  # Only "new york" is supported in this demo — other cities return an error.
  if city.lower() == "new york":
    tz_identifier = "America/New_York"  # IANA timezone string for New York.
  else:
    # Return an error dict for unsupported cities.
    return {
        "status": "error",
        "error_message": f"No timezone mapping for '{city}'.",
    }

  # Create a timezone object from the IANA identifier string.
  tz = ZoneInfo(tz_identifier)

  # Get the current date and time in that timezone.
  now = datetime.datetime.now(tz)

  # Format the time as a human-readable string, e.g. "2024-06-15 14:30:00 EDT-0400".
  report = (
      f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
  )

  # Return a success dict with the formatted time string.
  return {"status": "success", "report": report}


# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="weather_time_workshop_agent",

    # model: The Gemini model that decides which tool to call based on the user's message.
    model="gemini-2.5-flash",

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
