# 03-custom_tools

**Goal:** **Function tools**: Python docstrings and type hints become model-visible tool declarations.

## Architecture

```text
┌──────────────────────────────────────────────────┐
│          weather_time_workshop_agent              │  ← root agent
│          model: gemini-flash-lite                 │
│                                                  │
│  ┌─────────────────────┐  ┌───────────────────┐  │
│  │   get_weather(city) │  │ get_current_time() │  │  ← function tools
│  │   (stub data)       │  │ (real ZoneInfo)    │  │
│  └─────────────────────┘  └───────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Try it

```text
What is the weather and local time in New York?
```

```text
Paris weather
```

```text
What's the current weather and local time in Chicago?
```

**Upstream reference:** [quickstart `agent.py`](https://github.com/google/adk-python/blob/main/contributing/samples/quickstart/agent.py); tool orchestration patterns in [hello_world](https://github.com/google/adk-python/blob/main/contributing/samples/hello_world/agent.py).
