# 08-sequential_state_shared

**Level:** Intermediate — same **`output_key` + `{placeholder}`** pattern as the foodie/transport section in [`ADK_Learning_tool_multi_agents.ipynb`](../../notebooks/ADK_Learning_tool_multi_agents.ipynb), without Search.

## Architecture

```text
┌─────────── sequential_state_shared (SequentialAgent) ─────────────┐
│                                                                     │
│  ┌──────────────────────┐           ┌───────────────────────────┐  │
│  │   pick_destination    │           │      navigate_there        │  │
│  │   (sub-agent)         │           │      (sub-agent)           │  │
│  │                       │  state    │                           │  │
│  │  output_key=          │ ────────► │  instruction uses         │  │
│  │  "destination"        │           │  {destination} placeholder │  │
│  └──────────────────────┘           └───────────────────────────┘  │
│                                                                     │
│              shared state: { destination: "…" }                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Try it

```text
I’m near Caltrain and want dinner at Ramen Nagi in Palo Alto, how do I get there?
```

```text
Starting from Union Square in San Francisco, what’s the best way to get to the Golden Gate Bridge?
```

```text
I’m at SFO airport and need to reach the Salesforce Tower for a 3pm meeting—how should I travel?
```

**Checkpoint:** Second agent’s reply should explicitly use the venue picked in step 1.

See also [CHECKPOINTS.md](../CHECKPOINTS.md).
