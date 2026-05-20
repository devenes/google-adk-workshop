"""Advanced demo: schema-in, schema-out typed transformation using input_schema + output_schema.

KEY CONCEPT — Why both schemas?
  - output_schema alone forces structured JSON output from a free-form prompt.
  - input_schema additionally validates and types the incoming payload when this
    agent is wrapped in an AgentTool and called by an orchestrator.

Together they create a fully typed "function" at the agent layer:
    UserActivityLog  →  [structured_input_agent]  →  UserAnalysisReport

This pattern is ideal for:
  - ETL-style pipelines where one agent transforms structured data for another.
  - Downstream systems that consume predictable JSON (e.g. dashboards, databases).
  - Strict multi-agent contracts where input types must be enforced at runtime.

NOTE: Because output_schema is set, this agent uses Gemini's constrained decoding
mode — it cannot call any tools or produce free-form text alongside the schema.

UX NOTE: When input_schema is set on a root agent, the ADK Web UI does not display
a simple text chat bar. Instead, it prompts the user to enter a raw JSON payload matching
the input_schema structure.
"""

from google.adk import Agent

# Pydantic v2 BaseModel is the standard way to define ADK schemas.
# Field() lets us attach human-readable descriptions to each field.
# Gemini receives these descriptions as parameter descriptions in its JSON Schema,
# which helps it understand exactly what content to populate.
from pydantic import BaseModel, Field


# =============================================================================
# Input Schema — defines what data this agent expects to receive.
# When used as an AgentTool, ADK will present these fields to the calling
# orchestrator agent as function parameters (like a typed function signature).
# =============================================================================
class UserActivityLog(BaseModel):
  """Structured log of a user's recent actions on a platform."""

  user_id: str = Field(description="Unique identifier for the user")

  # list[str] lets Pydantic validate that each action is a string.
  actions: list[str] = Field(
      description="Ordered list of actions performed, e.g. 'click_ad', 'view_item_price'"
  )

  # Constrained to known device classes — the model is instructed to use these.
  device: str = Field(
      description="Device class: 'mobile', 'desktop', or 'tablet'"
  )


# =============================================================================
# Output Schema — defines the structured JSON the agent MUST return.
# Gemini's constrained decoding guarantees every field is populated and typed
# correctly. Callers can safely deserialise with UserAnalysisReport.model_validate().
# =============================================================================
class UserAnalysisReport(BaseModel):
  """Structured user classification and recommendations based on activity logs."""

  # Echo the user_id so downstream systems can correlate input → output.
  user_id: str = Field(description="Matches the incoming user_id exactly")

  primary_interest: str = Field(
      description="Primary category of interest inferred from actions (e.g. 'price comparison')"
  )

  # Constrained vocabulary makes downstream logic predictable.
  risk_level: str = Field(
      description="Inferred risk level: must be exactly 'low', 'medium', or 'high'"
  )

  recommendations: list[str] = Field(
      description="Exactly two distinct, actionable recommendations for the platform",
      max_length=2,   # Passed as maxItems in the JSON Schema so Gemini's output engine enforces it.
  )


# --- Agent definition ---
root_agent = Agent(
    name="structured_input_agent",

    # gemini-2.5-flash-lite is sufficient; flash is also fine for schema-constrained tasks.
    model="gemini-2.5-flash-lite",

    description=(
        "Analyzes structured UserActivityLog payloads and returns structured "
        "UserAnalysisReport objects. No free-form text output."
    ),

    instruction=(
        "You receive a UserActivityLog payload.\\n"
        "Analyse the sequence of actions and the device type to infer:\\n"
        "  • primary_interest: what the user appears most interested in.\\n"
        "  • risk_level: 'low' (casual browsing), 'medium' (considering purchase), "
        "'high' (high-value transaction signals).\\n"
        "  • recommendations: exactly two concrete, platform-specific suggestions.\\n"
        "Return ONLY the UserAnalysisReport JSON. No additional text."
    ),

    # input_schema: Validates incoming data and exposes typed parameters to orchestrators.
    input_schema=UserActivityLog,

    # output_schema: Forces Gemini to return a JSON object matching UserAnalysisReport.
    # WARNING: You cannot combine output_schema with tools= — they use conflicting
    # response modes (constrained JSON vs. function call JSON).
    output_schema=UserAnalysisReport,
)
