# 13-structured_output

**Level:** Advanced (typed model output for UIs, APIs, and tests).

**Goal:** **`output_schema`** (Pydantic) constrains the final response shape.

## Architecture

```text
┌───────────────────────────────────────────────────────┐
│             structured_city_agent  (root agent)        │
│             model: gemini-flash-lite                   │
│             output_schema: CityProfile (Pydantic)      │
│                                                       │
│                     (no tools)                        │
└───────────────────────────────────────────────────────┘
                          │
                          ▼ forced JSON output
              ┌─────────────────────────┐
              │  CityProfile {          │
              │    name, country,       │
              │    population_band,     │
              │    highlights[≤3]       │
              │  }                      │
              └─────────────────────────┘
```

## Try it

```text
Describe Lyon, France for a travel app.
```

```text
Generate a structured city profile for Osaka, Japan.
```

```text
Create a travel app entry for Cape Town, South Africa.
```

**Combine with tools:** See [output_schema_with_tools](https://github.com/google/adk-python/blob/main/contributing/samples/output_schema_with_tools/agent.py) for the coordinator pattern.
