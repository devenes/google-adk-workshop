"""Parent with output_schema + tools; child specialist also has output_schema (tools combo)."""

import requests
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field


class PersonInfo(BaseModel):
  """Structured biography fields."""

  name: str = Field(description="Full name")
  age: int = Field(description="Age in years if inferable, else 0")
  occupation: str = Field(description="Role or 'unknown'")
  location: str = Field(description="City/country or 'unknown'")
  biography: str = Field(description="Two short sentences max")


def search_wikipedia(query: str) -> str:
  """Look up a Wikipedia summary for query."""
  try:
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + query.replace(" ", "_")
    )
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
      return f"No page (status {r.status_code})."
    d = r.json()
    return f"{d.get('title')}: {d.get('extract', '')}"
  except Exception as e:  # noqa: BLE001
    return str(e)


def get_current_year() -> str:
  from datetime import datetime

  return str(datetime.now().year)


_specialist = Agent(
    name="person_specialist",
    model="gemini-2.5-flash",
    description="Researches a named person via Wikipedia into PersonInfo shape.",
    instruction=(
        "Use search_wikipedia. Fill PersonInfo fields; if age unknown use 0."
    ),
    tools=[search_wikipedia],
    output_schema=PersonInfo,
)

root_agent = Agent(
    name="person_orchestrator",
    model="gemini-2.5-flash",
    description="For politicians or famous people use specialist; else Wikipedia + year tool.",
    instruction=(
        "When asked about a well-known person, call person_specialist with their name.\n"
        "Otherwise use search_wikipedia and get_current_year as needed.\n"
        "Final reply must conform to PersonInfo (same schema)."
    ),
    tools=[
        AgentTool(_specialist, skip_summarization=True),
        search_wikipedia,
        get_current_year,
    ],
    output_schema=PersonInfo,
)
