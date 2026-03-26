"""Live weather via api.weather.gov (no API key; US locations)."""

import requests
from google.adk import Agent

_HEADERS = {"User-Agent": "(adk-workshop, local-demo)"}

# Small lat/lon table so learners do not need geocoding.
_COORDS = {
    "san francisco": (37.7749, -122.4194),
    "palo alto": (37.4419, -122.1430),
    "lake tahoe": (39.0968, -120.0324),
    "new york": (40.7128, -74.0060),
}


def get_live_forecast(city: str) -> dict:
  """Return a short public forecast for a supported US city.

  Uses the U.S. National Weather Service API (api.weather.gov).

  Args:
      city: City name (e.g. 'San Francisco', 'Palo Alto').

  Returns:
      dict with status, and either ``forecast`` or ``error_message``.
  """
  key = city.lower().strip()
  if key not in _COORDS:
    return {
        "status": "error",
        "error_message": (
            f"Unsupported city '{city}'. Try: {', '.join(sorted(_COORDS))}."
        ),
    }
  lat, lon = _COORDS[key]
  try:
    p = requests.get(
        f"https://api.weather.gov/points/{lat},{lon}",
        headers=_HEADERS,
        timeout=10,
    )
    p.raise_for_status()
    forecast_url = p.json()["properties"]["forecast"]
    f = requests.get(forecast_url, headers=_HEADERS, timeout=10)
    f.raise_for_status()
    periods = f.json().get("properties", {}).get("periods", [])
    if not periods:
      return {"status": "error", "error_message": "No forecast periods returned."}
    first = periods[0]
    text = (
        f"{first.get('name', 'Next')}: {first.get('temperature')}°"
        f"{first.get('temperatureUnit', 'F')} — {first.get('shortForecast', '')}"
    )
    return {"status": "success", "forecast": text}
  except Exception as e:  # noqa: BLE001
    return {"status": "error", "error_message": str(e)}


root_agent = Agent(
    name="nws_weather_agent",
    model="gemini-2.5-flash",
    description="Answers outdoor plans using the National Weather Service API.",
    instruction=(
        "For weather questions, call get_live_forecast with the city name. "
        "If the tool errors, explain and suggest a supported city. "
        "Never invent forecast numbers."
    ),
    tools=[get_live_forecast],
)
