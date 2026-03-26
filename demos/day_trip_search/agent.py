"""Day-trip itinerary agent using Google Search grounding (workshop)."""

from google.adk import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="day_trip_agent",
    model="gemini-2.5-flash",
    description=(
        "Generates full-day trip itineraries with mood, interests, and budget hints."
    ),
    instruction="""
You are the \"Spontaneous Day Trip\" generator. Create engaging same-day itineraries.

Guidelines:
1. Respect budget hints: cheap, mid-range, or splurge.
2. Structure the day as morning, afternoon, and evening blocks.
3. Use Google Search for venues, hours, and current events when helpful.
4. Return the answer in Markdown with clear headings and bullet lists.
""",
    tools=[google_search],
)
