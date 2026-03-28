"""Day-trip itinerary agent using Google Search grounding (workshop)."""

# Agent is the core ADK class that wraps a Gemini model with tools and instructions.
from google.adk import Agent

# google_search is a built-in ADK tool that lets the agent search the web via Google.
# It is pre-built — you do not write any Python code for it; just pass it in tools=[].
from google.adk.tools import google_search

# root_agent is the special name ADK looks for when starting with `adk web` or `adk run`.
root_agent = Agent(
    # name: Unique label for this agent in logs and traces.
    name="day_trip_agent",

    # model: Gemini model used to understand the user's request and call tools.
    model="gemini-2.5-flash-lite",

    # description: One-line summary so orchestrators know what this agent specialises in.
    description=(
        "Generates full-day trip itineraries with mood, interests, and budget hints."
    ),

    # instruction: System prompt — tells the model how to behave for every conversation turn.
    # Triple-quoted strings allow multi-line instructions with numbered guidelines.
    instruction="""
You are the \"Spontaneous Day Trip\" generator. Create engaging same-day itineraries.

Guidelines:
1. Respect budget hints: cheap, mid-range, or splurge.
2. Structure the day as morning, afternoon, and evening blocks.
3. Use Google Search for venues, hours, and current events when helpful.
4. Return the answer in Markdown with clear headings and bullet lists.
""",

    # tools: Pass the built-in google_search tool so the agent can look up real-world info.
    # The model decides when to search and what query to use.
    tools=[google_search],
)
