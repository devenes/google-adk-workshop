"""Parent with output_schema + tools; child specialist also has output_schema (tools combo)."""

# datetime is Python's standard module for working with dates and times.
import datetime

# requests is used for making HTTP calls to the Wikipedia REST API.
import requests

# Agent is the core ADK class.
from google.adk import Agent

# AgentTool wraps another Agent so an orchestrator can call it as if it were a Python function.
from google.adk.tools.agent_tool import AgentTool

# Pydantic is used to define the exact JSON structure that agents must return.
from pydantic import BaseModel, Field


# --- Output Schema ---
# PersonInfo defines the structured shape the agent's response must conform to.
# When output_schema=PersonInfo is set on an Agent, Gemini is constrained to return
# valid JSON matching these fields — no free-form text allowed.
class PersonInfo(BaseModel):
  """Structured biography fields."""

  # Full name of the person.
  name: str = Field(description="Full name")

  # Age in years. Use 0 if the age cannot be determined from available sources.
  age: int = Field(description="Age in years if inferable, else 0")

  # The person's job title or professional role; use "unknown" if not found.
  occupation: str = Field(description="Role or 'unknown'")

  # City and/or country where the person is based; use "unknown" if not found.
  location: str = Field(description="City/country or 'unknown'")

  # A brief summary — no more than two sentences.
  biography: str = Field(description="Two short sentences max")


# --- Tool: search_wikipedia ---
def search_wikipedia(query: str) -> str:
  """Look up a Wikipedia summary for query."""
  try:
    # Build the Wikipedia API URL, replacing spaces with underscores in the article title.
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + query.replace(" ", "_")
    )

    # Fetch the page summary with a 10-second timeout.
    r = requests.get(url, timeout=10)

    # If the page was not found, return a descriptive message.
    if r.status_code != 200:
      return f"No page (status {r.status_code})."

    # Parse JSON and return "Title: extract text".
    d = r.json()
    return f"{d.get('title')}: {d.get('extract', '')}"

  except Exception as e:  # noqa: BLE001 — broad catch for demo robustness
    # Return error as string so the agent can explain the problem to the user.
    return str(e)


# --- Tool: get_current_year ---
def get_current_year() -> str:
  """Return the current calendar year as a string."""
  # Used to calculate a person's approximate age from their birth year.
  return str(datetime.datetime.now().year)


# --- Specialist Sub-Agent ---
# _specialist is a dedicated agent for researching a single person.
# It uses search_wikipedia and must fill in PersonInfo fields.
# It is NOT exposed directly to users — it is wrapped as a tool below.
_specialist = Agent(
    name="person_specialist",
    model="gemini-2.5-flash",
    description="Researches a named person via Wikipedia into PersonInfo shape.",
    instruction=(
        # The specialist searches Wikipedia and fills out the PersonInfo schema.
        "Use search_wikipedia. Fill PersonInfo fields; if age unknown use 0."
    ),
    tools=[search_wikipedia],     # Can call Wikipedia search.
    output_schema=PersonInfo,     # Must return a PersonInfo-shaped JSON object.
)

# --- Root Agent: Orchestrator ---
# root_agent talks to users and either delegates to _specialist or does its own research.
# Note: root_agent also has output_schema=PersonInfo, so it too must return PersonInfo JSON.
root_agent = Agent(
    name="person_orchestrator",
    model="gemini-2.5-flash",
    description="For politicians or famous people use specialist; else Wikipedia + year tool.",
    instruction=(
        # Tells the orchestrator how to decide between delegation and direct tool use.
        "When asked about a well-known person, call person_specialist with their name.\n"
        "Otherwise use search_wikipedia and get_current_year as needed.\n"
        "Final reply must conform to PersonInfo (same schema)."
    ),
    tools=[
        # AgentTool wraps _specialist — the orchestrator calls it like a Python function.
        # skip_summarization=True passes the specialist's full output back without trimming.
        AgentTool(_specialist, skip_summarization=True),

        # Direct tools the orchestrator can use without delegating.
        search_wikipedia,
        get_current_year,
    ],
    # output_schema forces the orchestrator's final response to be a PersonInfo JSON object.
    output_schema=PersonInfo,
)
