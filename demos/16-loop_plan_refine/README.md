# 16-loop_plan_refine

**Level:** Expert (workflow) — **`LoopAgent`** + `exit_loop`.

**Goal:** Same pattern as **“Iterative Ideas with LoopAgent”** in [`ADK_Learning_tool_multi_agents.ipynb`](../../notebooks/ADK_Learning_tool_multi_agents.ipynb): critic ↔ refiner cycle until approval or `max_iterations`.

## Architecture

```text
┌──────────── iterative_plan_workshop (SequentialAgent) ─────────────┐
│                                                                      │
│  ┌──────────────────┐                                               │
│  │     planner       │  output_key="current_plan"  (runs once)      │
│  └────────┬─────────┘                                               │
│           │                                                         │
│           ▼                                                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │          refinement_loop  (LoopAgent, max_iterations=3)         │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────┐                               │ │
│  │  │  critic  (sub-agent)         │  output_key="criticism"       │ │
│  │  │  reads {current_plan}        │  outputs PLAN_OK if approved  │ │
│  │  └──────────────┬──────────────┘                               │ │
│  │                 │                                               │ │
│  │                 ▼                                               │ │
│  │  ┌─────────────────────────────┐                               │ │
│  │  │  refiner  (sub-agent)        │  output_key="current_plan"    │ │
│  │  │  reads {criticism}           │  calls exit_loop if PLAN_OK   │ │
│  │  │  tool: exit_loop (built-in)  │  else rewrites plan           │ │
│  │  └─────────────────────────────┘                               │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Try it

```text
Plan a 2-hour study session for an ADK certification.
```

```text
Create a focused 90-minute plan for learning Python decorators.
```

```text
Draft a one-week preparation plan for a data structures technical interview.
```

**Note:** This variant avoids `google_search` so it runs offline-safe in more classrooms. For the full travel-time critique, run cells in the Colab-oriented notebook.
