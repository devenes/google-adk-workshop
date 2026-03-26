# loop_plan_refine

**Level:** Expert (workflow) — **`LoopAgent`** + `exit_loop`.

**Goal:** Same pattern as **“Iterative Ideas with LoopAgent”** in [`ADK_Learning_tool_multi_agents.ipynb`](../../notebooks/ADK_Learning_tool_multi_agents.ipynb): critic ↔ refiner cycle until approval or `max_iterations`.

**Try:** “Plan a 2-hour study session for an ADK certification.” If the first draft is vague, watch the loop refine it; when the critic returns `PLAN_OK`, the refiner calls **`exit_loop`**.

**Note:** This variant avoids `google_search` so it runs offline-safe in more classrooms. For the full travel-time critique, run cells in the Colab-oriented notebook.
