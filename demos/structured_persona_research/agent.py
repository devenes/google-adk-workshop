"""Parent with output_schema + tools; child specialist also has output_schema (tools combo)."""

# Agent is the core ADK class.
from google.adk import Agent

# AgentTool wraps another Agent so an orchestrator can call it as if it were a Python function.
from google.adk.tools.agent_tool import AgentTool

# google_search is a built-in ADK tool — no API key or setup required beyond ADK itself.
from google.adk.tools import google_search

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


# --- Specialist Sub-Agent ---
# _specialist searches the web and returns free-form research text.
# No output_schema here — Gemini forbids combining built-in tools (google_search)
# with function calling (which output_schema uses internally).
# It is NOT exposed directly to users — it is wrapped as a tool below.
_specialist = Agent(
    name="person_specialist",
    model="gemini-2.5-flash-lite",
    description="Researches a named person via Google Search and returns a biographical summary.",
    instruction=(
        # The specialist searches the web and returns raw research for the orchestrator to format.
        "Use google_search to find name, age, occupation, location, and biography. "
        "Return all findings as a detailed text summary."
    ),
    tools=[google_search],        # Can search the web; no output_schema (incompatible with built-in tools).
)

# --- Root Agent: Orchestrator ---
# root_agent delegates research to _specialist, then formats the result into PersonInfo.
# It has output_schema but no google_search — keeping function calling and built-in tools separate.
root_agent = Agent(
    name="person_orchestrator",
    model="gemini-2.5-flash",
    description="Delegates research to person_specialist, then formats the result as PersonInfo.",
    instruction=(
        # Orchestrator always delegates searching to the specialist, then formats the output.
        "Call person_specialist with the person's name to gather research.\n"
        "Then format the result into PersonInfo fields; use 0 for unknown age, 'unknown' for other missing fields."
    ),
    tools=[
        # AgentTool wraps _specialist — the orchestrator calls it like a Python function.
        # skip_summarization=True passes the specialist's full output back without trimming.
        AgentTool(_specialist, skip_summarization=True),
    ],
    # output_schema forces the orchestrator's final response to be a PersonInfo JSON object.
    # Safe here because the orchestrator itself has no built-in tools.
    output_schema=PersonInfo,
)
