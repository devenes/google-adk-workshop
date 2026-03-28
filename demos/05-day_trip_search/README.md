# 05-day_trip_search

**Goal:** Show a **built-in tool** (`google_search`) for grounded, up-to-date answers.

**Run:** `adk web .` from `workshop/demos` → `day_trip_search`.

**Workshop tie-in:** Mirrors **Part 1** of [`ADK_Learning_tools.ipynb`](../../ADK_Learning_tools.ipynb) (Colab-oriented original in `workshop/`).

**Note:** Search availability depends on your Gemini API / project settings; have [`hello_web`](../01-hello_web) ready as a fallback.

## Architecture

```text
┌──────────────────────────────────────┐
│           day_trip_agent              │  ← root agent
│           model: gemini-flash-lite    │
│                                      │
│  ┌────────────────────────────────┐  │
│  │   google_search  (built-in)    │  │  ← built-in ADK tool
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

## Try it

```text
Plan a cheap day trip to Barcelona for a solo traveller who loves street food and art.
```

```text
I have a mid-range budget and one free Saturday in Tokyo. Suggest a full day — morning, afternoon, and evening.
```

```text
Splurge day trip from London to the Cotswolds for a couple who enjoy history and fine dining.
```
