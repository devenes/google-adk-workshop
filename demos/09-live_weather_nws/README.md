# 09-live_weather_nws

**Level:** Beginner–intermediate — real **HTTP** tool (like the NWS section in [`ADK_Learning_tools.ipynb`](../../ADK_Learning_tools.ipynb)).

## Architecture

```text
┌────────────────────────────────────────────────┐
│              nws_weather_agent                  │  ← root agent
│              model: gemini-2.0-flash            │
│                                                │
│  ┌──────────────────────────────────────────┐  │
│  │         get_live_forecast(city)           │  │  ← HTTP tool
│  └───────────────────┬──────────────────────┘  │
└───────────────────── │ ────────────────────────┘
                       │  2-hop HTTP
          ┌────────────▼────────────┐
          │   api.weather.gov        │
          │  /points/{lat},{lon}     │  step 1: get forecast URL
          │  /gridpoints/…/forecast  │  step 2: get forecast data
          └──────────────────────────┘
```

## Try it

```text
What's the forecast for Palo Alto?
```

```text
Will it rain in Seattle this weekend?
```

```text
What's the weather like in Austin, Texas right now?
```

**Checkpoint:** Response should match tool output; unsupported cities should list allowed names.

**Note:** `api.weather.gov` is US-only and may rate-limit; requires network access.

See [CHECKPOINTS.md](../CHECKPOINTS.md).
