# 07-sequential_pipeline

**Level:** Intermediate (control flow without tool routing).

**Goal:** **SequentialAgent** always runs `outline_drafter` then `detail_expander` — deterministic stage order.

## Architecture

```text
┌─────────── sequential_write_pipeline (SequentialAgent) ──────────┐
│                                                                    │
│  ┌────────────────────┐  text   ┌────────────────────────────┐   │
│  │   outline_drafter   │ ──────► │      detail_expander        │   │
│  │   (sub-agent)       │        │      (sub-agent)             │   │
│  │   3-bullet outline  │        │   expands to full paragraph  │   │
│  └────────────────────┘        └────────────────────────────┘   │
│                                                                    │
│  runs step 1 → step 2  (deterministic order, no tools)            │
└────────────────────────────────────────────────────────────────────┘
```

## Try it

```text
Topic: benefits of automated testing for APIs.
```

```text
Topic: how neural networks learn from data.
```

```text
Topic: best practices for designing REST APIs.
```

**Upstream reference:** [simple_sequential_agent](https://github.com/google/adk-python/blob/main/contributing/samples/simple_sequential_agent/agent.py).
