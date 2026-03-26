"""Advanced demo: structured JSON-style responses via Pydantic output_schema."""

from google.adk import Agent
from pydantic import BaseModel, Field


class CityProfile(BaseModel):
  """Structured description of a city for downstream apps."""

  name: str = Field(description="City name")
  country: str = Field(description="Country")
  population_band: str = Field(
      description='Approximate size bucket, e.g. "under 500k" or "1–3M"'
  )
  highlights: list[str] = Field(
      description="Up to three notable traits or facts",
      max_length=3,
  )


root_agent = Agent(
    name="structured_city_agent",
    model="gemini-2.5-flash",
    description="Returns city facts as a CityProfile object.",
    instruction=(
        "When the user names or asks about a city, fill in CityProfile fields "
        "accurately. If population is unknown, set population_band to "
        '"unknown". Highlights must be factual and short.'
    ),
    output_schema=CityProfile,
)
