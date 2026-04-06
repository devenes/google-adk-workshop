"""Live weather via api.weather.gov (no API key; US locations)."""

# requests is a popular Python library for making HTTP web requests.
import requests

# Agent is the core ADK class connecting a model to tools and instructions.
from google.adk import Agent

# Custom User-Agent header required by api.weather.gov — they block requests without one.
# This identifies our app politely to the NWS server.
_HEADERS = {"User-Agent": "(adk-workshop, local-demo)"}

# Small lat/lon lookup table so learners don't need a geocoding API.
# Keys are lowercase city names; values are (latitude, longitude) tuples.
_COORDS = {
    "san francisco": (37.7749, -122.4194),
    "palo alto": (37.4419, -122.1430),
    "lake tahoe": (39.0968, -120.0324),
    "new york": (40.7128, -74.0060),
}


# --- Tool: get_live_forecast ---
def get_live_forecast(city: str) -> dict:
  """Return a short public forecast for a supported US city.

  Uses the U.S. National Weather Service API (api.weather.gov).

  Args:
      city: City name (e.g. 'San Francisco', 'Palo Alto').

  Returns:
      dict with status, and either ``forecast`` or ``error_message``.
  """
  # Normalize the city name: strip whitespace and convert to lowercase for lookup.
  key = city.lower().strip()

  # Check if the city is in our hardcoded table; return an error if it is not.
  if key not in _COORDS:
    return {
        "status": "error",
        "error_message": (
            f"Unsupported city '{city}'. Try: {', '.join(sorted(_COORDS))}."
        ),
    }

  # Unpack the latitude and longitude from the table.
  lat, lon = _COORDS[key]

  try:
    # Step 1: Call the NWS /points endpoint to get the forecast URL for these coordinates.
    # The NWS API requires two hops: first get metadata, then get the actual forecast.
    p = requests.get(
        f"https://api.weather.gov/points/{lat},{lon}",
        headers=_HEADERS,
        timeout=10,  # Fail after 10 seconds rather than hanging forever.
    )
    # raise_for_status() raises an exception if the HTTP response code is 4xx or 5xx.
    p.raise_for_status()

    # Extract the forecast URL from the JSON response's "properties" section.
    forecast_url = p.json()["properties"]["forecast"]

    # Step 2: Fetch the actual forecast from the URL we just retrieved.
    f = requests.get(forecast_url, headers=_HEADERS, timeout=10)
    f.raise_for_status()

    # The forecast is broken into "periods" (e.g. "Tonight", "Thursday", "Thursday Night").
    periods = f.json().get("properties", {}).get("periods", [])

    # Guard against an empty periods list (shouldn't happen normally, but be safe).
    if not periods:
      return {"status": "error", "error_message": "No forecast periods returned."}

    # Take only the first (most current) forecast period.
    first = periods[0]

    # Build a human-readable one-line summary: "Tonight: 55°F — Mostly Clear"
    text = (
        f"{first.get('name', 'Next')}: {first.get('temperature')}°"
        f"{first.get('temperatureUnit', 'F')} — {first.get('shortForecast', '')}"
    )

    # Return success with the formatted forecast string.
    return {"status": "success", "forecast": text}

  except Exception as e:  # noqa: BLE001 — broad catch is intentional for a demo tool
    # Any network error, timeout, or JSON parsing issue is caught here.
    # We return a friendly error dict instead of crashing the agent.
    return {"status": "error", "error_message": str(e)}


# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="nws_weather_agent",

    # model: Gemini model that decides to call get_live_forecast based on the user's message.
    model="gemini-2.5-flash",

    # description: Used by orchestrators to decide when to route requests here.
    description="Answers outdoor plans using the National Weather Service API.",

    # instruction: Tells the model to always use the tool and never invent numbers.
    instruction=(
        "For weather questions, call get_live_forecast with the city name. "
        "If the tool errors, explain and suggest a supported city. "
        "Never invent forecast numbers."
    ),

    # tools: The live forecast function registered as an agent tool.
    tools=[get_live_forecast],
)
