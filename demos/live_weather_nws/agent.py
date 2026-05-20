"""Live weather via api.weather.gov (no API key; US locations)."""

# requests is a popular Python library for making HTTP web requests.
import requests

# Agent is the core ADK class connecting a model to tools and instructions.
from google.adk import Agent

# Custom User-Agent header required by api.weather.gov — they block requests without one.
# A User-Agent is a short identifier string your app sends with every HTTP request so the
# server knows which client is calling (like a name tag for your program).
_HEADERS = {"User-Agent": "(adk-workshop, local-demo)"}

# Small lat/lon lookup table so learners don't need a geocoding API.
# Keys are lowercase city names; values are (latitude, longitude) tuples.
_COORDS = {
    "san francisco": (37.7749, -122.4194),
    "palo alto": (37.4419, -122.1430),
    "lake tahoe": (39.0968, -120.0324),
    "new york": (40.7128, -74.0060),
    "seattle": (47.6062, -122.3321),
    "austin": (30.2672, -97.7431),
    "los angeles": (34.0522, -118.2437),
}


def _normalize_city(city: object) -> str:
  """Normalize user-entered city text to a lookup key."""
  if not isinstance(city, str) or not city.strip():
    return ""
  # Keep just the first comma-separated part (e.g. "Austin, TX" -> "austin").
  return city.lower().strip().split(",")[0].strip()


# --- Tool: get_live_forecast ---
def get_live_forecast(city: str) -> dict:
  """Return a short public forecast for a supported US city.

  Uses the U.S. National Weather Service API (api.weather.gov).

  Args:
      city: City name (e.g. 'San Francisco', 'Palo Alto').

  Returns:
      dict with status, and either ``forecast`` or ``error_message``.
  """
  # Normalize the city name for lookup.
  key = _normalize_city(city)
  if not key:
    if not isinstance(city, str):
      return {
        "status": "error",
        "error_message": f"Invalid city value {city!r}. Please provide a city name as text.",
      }
    return {
      "status": "error",
      "error_message": "City value is empty. Please provide a supported city.",
    }

  # Check if the city is in our hardcoded table; return an error if it is not.
  if key not in _COORDS:
    city_label = key
    return {
        "status": "error",
        "error_message": (
            f"Unsupported city '{city_label}'. Try: {', '.join(sorted(_COORDS))}."
        ),
    }

  # Unpack the latitude and longitude from the table.
  lat, lon = _COORDS[key]

  # Step 1: Call the NWS /points endpoint to get the forecast URL for these
  # coordinates. The API requires two hops: first metadata, then forecast details.
  try:
    points_resp = requests.get(
        f"https://api.weather.gov/points/{lat},{lon}",
        headers=_HEADERS,
        timeout=10,  # Fail after 10 seconds rather than hanging forever.
    )
    points_resp.raise_for_status()
  except requests.RequestException as exc:
    return {
      "status": "error",
      "error_message": f"Unable to fetch forecast metadata: {exc}",
    }

  try:
    # Extract the forecast URL from the JSON response's "properties" section.
    forecast_payload = points_resp.json()
    properties = forecast_payload.get("properties")
  except (ValueError, TypeError, AttributeError) as exc:
    return {
      "status": "error",
      "error_message": f"Invalid forecast metadata response: {exc}",
    }

  if not isinstance(properties, dict):
    return {
      "status": "error",
      "error_message": "Invalid forecast metadata response: 'properties' field is not a dict.",
    }

  forecast_url = properties.get("forecast")
  if not isinstance(forecast_url, str):
    return {
      "status": "error",
      "error_message": "Forecast metadata is missing a forecast URL.",
    }

  # Step 2: Fetch the actual forecast from the URL we just retrieved.
  try:
    forecast_resp = requests.get(forecast_url, headers=_HEADERS, timeout=10)
    forecast_resp.raise_for_status()
  except requests.RequestException as exc:
    return {
      "status": "error",
      "error_message": f"Unable to fetch forecast details: {exc}",
    }

  try:
    periods = forecast_resp.json().get("properties", {}).get("periods", [])
  except (ValueError, TypeError) as exc:
    return {
      "status": "error",
      "error_message": f"Invalid forecast response format: {exc}",
    }

  # Guard against a missing or unsupported forecast payload shape.
  if not isinstance(periods, list):
    return {
      "status": "error",
      "error_message": "Invalid forecast response format: periods must be a list.",
    }

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


# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="nws_weather_agent",

    # model: gemini-2.5-flash (not -lite) because structured multi-hop API responses and
    # detailed forecast payloads require stronger reasoning than the lighter model provides.
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
