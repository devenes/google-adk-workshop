# 01-hello_web

**Goal:** Smallest runnable agent to validate venv, `GOOGLE_API_KEY`, and `adk web`.

**Run:** From `workshop/demos` with venv active: `adk web .` → select `hello_web`.

**Upstream reference:** [adk-python `contributing/samples/quickstart`](https://github.com/google/adk-python/tree/main/contributing/samples/quickstart) (adds function tools; this demo omits tools on purpose).

## Architecture

```text
┌──────────────────────────────┐
│    hello_workshop_agent      │  ← root agent
│    model: gemini-flash-lite  │
│                              │
│         (no tools)           │
└──────────────────────────────┘
```

## Try it

```text
Hello! What can you help me with?
```

```text
Tell me something interesting about artificial intelligence in three sentences.
```

```text
What's the difference between a large language model and a traditional chatbot?
```
