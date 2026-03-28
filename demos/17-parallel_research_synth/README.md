# 17-parallel_research_synth

> **Token streaming** should be enabled for this demo.

**Level:** Expert (workflow) — **`ParallelAgent`** + **`SequentialAgent`**.

**Goal:** Same architecture as **“Parallel Power with ParallelAgent”** in [`ADK_Learning_tool_multi_agents.ipynb`](../../notebooks/ADK_Learning_tool_multi_agents.ipynb): independent branches write `output_key` fields; a final agent reads `{museum_result}`, `{events_result}`, `{food_result}` from shared state.

## Architecture

```text
┌──────────── parallel_then_synthesize (SequentialAgent) ──────────────┐
│                                                                        │
│  ┌─────────────────────────── ParallelAgent ──────────────────────┐  │
│  │  (all three run concurrently)                                   │  │
│  │                                                                 │  │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐  │  │
│  │  │ museum_researcher│ │events_researcher │ │food_researcher │  │  │
│  │  │ output_key=       │ │ output_key=       │ │ output_key=     │  │  │
│  │  │ "museum_result"  │ │ "events_result"  │ │ "food_result"  │  │  │
│  │  │                  │ │                  │ │                │  │  │
│  │  │ research_        │ │ research_events()│ │ research_food()│  │  │
│  │  │ museums() (stub) │ │ (stub)           │ │ (stub)         │  │  │
│  │  └──────────────────┘ └──────────────────┘ └────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                               │                                        │
│          state: { museum_result, events_result, food_result }          │
│                               │                                        │
│                               ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  synthesizer  (sub-agent, no tools)                               │ │
│  │  reads {museum_result}, {events_result}, {food_result}            │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

## Try it

```text
I'm visiting Austin for a weekend—what museums, events, and food should I consider?
```

```text
Planning a weekend in Lisbon—what are the top museums, current events, and local food scenes?
```

```text
I have two days in Chicago—recommend museums, events happening this season, and must-try food spots.
```

**Contrast:** [`07-sequential_pipeline`](../07-sequential_pipeline) runs LLM stages one-by-one; here the three researchers run **concurrently** (then synthesize).
