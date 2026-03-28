"""Orchestrator calls specialists wrapped with AgentTool (agent-as-a-tool pattern)."""

# datetime is the standard Python module for date and time operations.
import datetime

# Agent is the core ADK class.
from google.adk import Agent

# AgentTool wraps another Agent so an orchestrator can call it just like a Python function.
# This is the "agent-as-a-tool" pattern: one agent delegates sub-tasks to another agent.
from google.adk.tools.agent_tool import AgentTool

# google_search is a built-in ADK tool — no API key or setup required beyond ADK itself.
from google.adk.tools import google_search


# --- Tool: get_current_year ---
def get_current_year() -> str:
  """Return the current calendar year."""
  # datetime.datetime.now() gives the current local date and time.
  # .year extracts just the 4-digit year integer; str() converts it to text.
  return str(datetime.datetime.now().year)


# --- Specialist Agent ---
# _specialist is a sub-agent that searches the web via google_search.
# It is NOT exposed directly to the user — it is wrapped as a tool below.
_specialist = Agent(
    name="search_specialist",
    model="gemini-2.5-flash-lite",
    description="Searches the web and summarizes findings for a given topic or question.",
    instruction=(
        # Tell the specialist to always search and summarize the results.
        "You are a research assistant. Use google_search to find accurate, up-to-date "
        "information on the given topic. Summarize the key facts clearly for the orchestrator."
    ),
    tools=[google_search],  # The specialist can search the web.
)

# --- Root Agent: Orchestrator ---
# root_agent is the main agent that users talk to.
# It delegates research lookups to _specialist via AgentTool.
root_agent = Agent(
    name="research_orchestrator",
    model="gemini-2.5-flash-lite",
    description="Delegates research lookups to search_specialist; can use year tool directly.",
    instruction=(
        # Tells the orchestrator when to delegate to the specialist vs. use tools directly.
        "When the user asks about a person, place, event, or topic needing research, call "
        "the search_specialist tool with a clear request string.\n"
        "Use get_current_year ONLY when the user explicitly asks what year it is today, "
        "or to calculate a current age (birth year → today's year). "
        "Do NOT use it for historical dates — those come from search_specialist.\n"
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
