# parallel_research_synth

**Level:** Expert (workflow) — **`ParallelAgent`** + **`SequentialAgent`**.

**Goal:** Same architecture as **“Parallel Power with ParallelAgent”** in [`ADK_Learning_tool_multi_agents.ipynb`](../../notebooks/ADK_Learning_tool_multi_agents.ipynb): independent branches write `output_key` fields; a final agent reads `{museum_result}`, `{events_result}`, `{food_result}` from shared state.

**Try:** “I'm visiting Austin for a weekend—what museums, events, and food should I consider?”

**Contrast:** [`sequential_pipeline`](../sequential_pipeline) runs LLM stages one-by-one; here the three researchers run **concurrently** (then synthesize).
