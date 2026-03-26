"""Orchestrator calls specialists wrapped with AgentTool (agent-as-a-tool pattern)."""

# datetime is the standard Python module for date and time operations.
import datetime

# requests is a popular library for making HTTP web requests.
import requests

# Agent is the core ADK class.
from google.adk import Agent

# AgentTool wraps another Agent so an orchestrator can call it just like a Python function.
# This is the "agent-as-a-tool" pattern: one agent delegates sub-tasks to another agent.
from google.adk.tools.agent_tool import AgentTool


# --- Tool: search_wikipedia ---
# This function fetches a short summary from Wikipedia's public REST API (no key needed).
def search_wikipedia(query: str) -> str:
  """Fetch a short Wikipedia summary for a title or topic.

  Args:
      query: Article title or search phrase.

  Returns:
      Plain text summary or an error string.
  """
  try:
    # Build the Wikipedia REST API URL by replacing spaces with underscores in the query.
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + query.replace(" ", "_")
    )

    # Make a GET request with a 10-second timeout to avoid hanging.
    resp = requests.get(url, timeout=10)

    # If the page was not found (e.g., 404), return a friendly message.
    if resp.status_code != 200:
      return f"No article (HTTP {resp.status_code})."

    # Parse the JSON response and return "Title: extract text".
    data = resp.json()
    return f"{data.get('title', '')}: {data.get('extract', 'No extract.')}"

  except Exception as e:  # noqa: BLE001 — catch all errors in this demo tool
    # Return the error message as a string so the agent can relay it to the user.
    return f"Request failed: {e}"


# --- Tool: get_current_year ---
def get_current_year() -> str:
  """Return the current calendar year."""
  # datetime.datetime.now() gives the current local date and time.
  # .year extracts just the 4-digit year integer; str() converts it to text.
  return str(datetime.datetime.now().year)


# --- Specialist Agent ---
# _specialist is a sub-agent that knows how to use search_wikipedia.
# It is NOT exposed directly to the user — it is wrapped as a tool below.
_specialist = Agent(
    name="wiki_specialist",
    model="gemini-2.5-flash",
    description="Looks up people and topics via Wikipedia API.",
    instruction=(
        # Tell the specialist to always use the tool and summarize results.
        "Use search_wikipedia to collect facts. Summarize key points for the orchestrator."
    ),
    tools=[search_wikipedia],  # The specialist can call search_wikipedia.
)

# --- Root Agent: Orchestrator ---
# root_agent is the main agent that users talk to.
# It delegates deep Wikipedia lookups to _specialist via AgentTool.
root_agent = Agent(
    name="research_orchestrator",
    model="gemini-2.5-flash",
    description="Delegates deep lookups to wiki_specialist; can use year tool directly.",
    instruction=(
        # Tells the orchestrator when to delegate to the specialist vs. use tools directly.
        "When the user asks about a person, place, or topic needing references, call "
        "the wiki_specialist tool with a clear request string.\n"
        "When they need the current year or an age from a birth year, use get_current_year.\n"
        "Combine tool results into one concise answer."
    ),
    tools=[
        # AgentTool wraps _specialist so the orchestrator can call it like a function.
        # skip_summarization=True means the specialist's full response is passed back as-is.
        AgentTool(_specialist, skip_summarization=True),

        # get_current_year is a simple Python function tool used directly by the orchestrator.
        get_current_year,
    ],
)
