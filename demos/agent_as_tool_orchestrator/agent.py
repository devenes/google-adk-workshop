"""Orchestrator calls specialists wrapped with AgentTool (agent-as-a-tool pattern)."""

import requests
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool


def search_wikipedia(query: str) -> str:
  """Fetch a short Wikipedia summary for a title or topic.

  Args:
      query: Article title or search phrase.

  Returns:
      Plain text summary or an error string.
  """
  try:
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + query.replace(" ", "_")
    )
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
      return f"No article (HTTP {resp.status_code})."
    data = resp.json()
    return f"{data.get('title', '')}: {data.get('extract', 'No extract.')}"
  except Exception as e:  # noqa: BLE001 — workshop demo
    return f"Request failed: {e}"


def get_current_year() -> str:
  """Return the current calendar year."""
  from datetime import datetime

  return str(datetime.now().year)


_specialist = Agent(
    name="wiki_specialist",
    model="gemini-2.5-flash",
    description="Looks up people and topics via Wikipedia API.",
    instruction=(
        "Use search_wikipedia to collect facts. Summarize key points for the orchestrator."
    ),
    tools=[search_wikipedia],
)

root_agent = Agent(
    name="research_orchestrator",
    model="gemini-2.5-flash",
    description="Delegates deep lookups to wiki_specialist; can use year tool directly.",
    instruction=(
        "When the user asks about a person, place, or topic needing references, call "
        "the wiki_specialist tool with a clear request string.\n"
        "When they need the current year or an age from a birth year, use get_current_year.\n"
        "Combine tool results into one concise answer."
    ),
    tools=[
        AgentTool(_specialist, skip_summarization=True),
        get_current_year,
    ],
)
