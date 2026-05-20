"""Advanced demo: structured JSON-style responses via Pydantic output_schema."""

# Agent is the core ADK class for building agents.
from google.adk import Agent

# Pydantic is a data-validation library. We use it to define the exact shape of the agent's output.
# BaseModel: base class for all Pydantic data models.
# Field: lets us attach descriptions and constraints to each field.
from pydantic import BaseModel, Field


# --- Output Schema ---
# A Pydantic model defines the *structure* of the JSON the agent must return.
# When output_schema is set on an Agent, Gemini is forced to return valid JSON
# that matches this schema — no free-form text, no made-up fields.
class CityProfile(BaseModel):
  """Structured description of a city for downstream apps."""

  # str field: the agent must fill in the city's name as a string.
  name: str = Field(description="City name")

  # str field: the country the city belongs to.
  country: str = Field(description="Country")

  # str field: approximate population bucket — keeps the answer simple and consistent.
  population_band: str = Field(
      description='Approximate size bucket, e.g. "under 500k" or "1–3M"'
  )

  # list[str] field: up to three interesting facts about the city.
  # max_length=3 tells Pydantic to reject lists longer than 3 items.
  # Gemini receives this constraint as part of the JSON schema, so the model itself
  # is restricted to producing at most 3 items in the list.
  highlights: list[str] = Field(
      description="Up to three notable traits or facts",
      max_length=3,
  )


# --- Agent definition ---
root_agent = Agent(
    # name: Unique label for this agent.
    name="structured_city_agent",

    # model: Gemini model powering this agent.
    model="gemini-2.5-flash-lite",

    # description: Short summary for orchestrators.
    description="Returns city facts as a CityProfile object.",

    # instruction: Guides the model on how to fill in the CityProfile fields.
    instruction=(
        "When the user names or asks about a city, fill in CityProfile fields "
        "accurately. If population is unknown, set population_band to "
        '"unknown". Highlights must be factual and short.'
    ),

    # output_schema: Forces the model to return a JSON object matching CityProfile.
    # There are no tools= here — the model fills the schema directly from its knowledge.
    #
    # CRITICAL ADK RULE: You cannot combine output_schema with function tools= on the same Agent.
    # If an agent needs to call function tools AND return a structured JSON schema, you must
    # use an orchestrator agent with output_schema that calls a specialist agent with tools.
    # See structured_persona_research for an example of this workaround.
    output_schema=CityProfile,
)
