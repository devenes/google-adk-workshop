# ADK course path: beginner → expert

Use a **virtual environment** for every path ([`README.md`](README.md)). Official codelab context: [ADK Crash Course (Google Codelabs)](https://codelabs.developers.google.com/onramp/instructions#0).

This document ties together **two notebook tracks** and **`demos/`** so you can teach a full arc in one day or split across sessions.

---

## Course map

```mermaid
flowchart LR
  subgraph foundations [Foundations]
    NB1[Notebook_Tools_Memory]
    D1[demos_hello_calc_custom]
  end
  subgraph context [Context_and_grounding]
    D2[demos_kb_search_session]
  end
  subgraph workflows [Multi_agent_workflows]
    NB2[Notebook_MultiAgents]
    D3[demos_sequential_loop_parallel]
  end
  subgraph prod [Production_topics]
    X[Expert_table_CURRICULUM]
  end
  foundations --> context --> workflows --> prod
```

---

## Module 1 — Foundations (beginner)

**Concepts:** `Agent`, instructions, tools, docstrings → schemas, first **`adk web`** session.

| Step | Resource | Practice |
|------|----------|----------|
| 1.1 | [`notebooks/ADK_Learning_tools_venv.ipynb`](notebooks/ADK_Learning_tools_venv.ipynb) | Part 0–1: imports, day trip agent, `Runner` |
| 1.2 | [`demos/hello_web`](demos/hello_web) | Chat-only agent in Web UI |
| 1.3 | [`demos/calculator_basics`](demos/calculator_basics) | Tool chaining |
| 1.4 | [`demos/custom_tools`](demos/custom_tools) | Structured tool results / errors |

**Colab original (optional):** [`ADK_Learning_tools.ipynb`](ADK_Learning_tools.ipynb) — align with codelab *Session 1–2*.

---

## Module 2 — Context & grounding (intermediate)

**Concepts:** retrieval-shaped tools, **`google_search`**, **`ToolContext.state`**, `SequentialAgent` (simple pipeline).

| Step | Resource | Practice |
|------|----------|----------|
| 2.1 | [`demos/static_kb_rag`](demos/static_kb_rag) | Ground answers in snippet tool |
| 2.2 | [`demos/day_trip_search`](demos/day_trip_search) | Built-in search tool |
| 2.3 | [`notebooks/ADK_Learning_tools_venv.ipynb`](notebooks/ADK_Learning_tools_venv.ipynb) | Part 3: memory / same session |
| 2.4 | [`demos/session_memory`](demos/session_memory) | State across turns in Web UI |
| 2.5 | [`demos/sequential_pipeline`](demos/sequential_pipeline) | Two-step **ordered** LLM pipeline |

**Colab / codelab alignment:** *Session 4 (memory)* in the [Codelab guide](https://codelabs.developers.google.com/onramp/instructions#0).

---

## Module 3 — Multi-agent orchestration (advanced → expert)

**Primary notebook:** [`notebooks/ADK_Learning_tool_multi_agents.ipynb`](notebooks/ADK_Learning_tool_multi_agents.ipynb)

This matches codelab **Colab 2** themes: Router, Sequential workflows, `SequentialAgent` + `output_key`, **`LoopAgent`**, **`ParallelAgent`**.

| Part | Notebook (≈ section) | What learners do | Matching `adk web` demo |
|------|----------------------|------------------|-------------------------|
| 0 | Part 0: Setup | Install, auth, imports (`SequentialAgent`, `LoopAgent`, `ParallelAgent`) | (same venv as [`README`](README.md)) |
| 1 | Part 1: Router + manual combo | Router returns a route string; Python dispatches (`if` / `elif`) | Concept-only in notebook; **`multi_agent_coordinator`** shows **LLM delegation** to sub-agents instead |
| 2 | Part 2: `SequentialAgent` + state | `output_key`, `{placeholders}` in instructions | [`sequential_pipeline`](demos/sequential_pipeline) (outline→expand); notebook adds **foodie + transport** + search |
| 3 | LoopAgent | Critic ↔ refiner, **`exit_loop`**, `max_iterations` | [`loop_plan_refine`](demos/loop_plan_refine) (compact, no Search) |
| 4 | ParallelAgent | Three finders + **synthesis** | [`parallel_research_synth`](demos/parallel_research_synth) (stub tools, fast) |

**Talk track for Part 1 (router):** The notebook’s pattern is **explicit routing** (good for debugging). ADK Web often uses a **single parent `Agent`** with `sub_agents` and model-driven handoff—compare with [`multi_agent_coordinator`](demos/multi_agent_coordinator).

---

## Module 4 — Governance & structure (advanced)

| Step | Resource | Practice |
|------|----------|----------|
| 4.1 | [`demos/structured_output`](demos/structured_output) | Pydantic `output_schema` |
| 4.2 | [`demos/hitl_sensitive_action`](demos/hitl_sensitive_action) | `FunctionTool(require_confirmation=True)` |
| 4.3 | [ADK tool confirmation docs](https://google.github.io/adk-docs/tools/confirmation/) | Discuss production guardrails |

---

## Module 5 — Expert extensions (self-study)

See the **Expert** table in [`CURRICULUM.md`](CURRICULUM.md): Vertex RAG, skills, MCP, `adk eval`, deploy.

---

## Suggested schedules

| Duration | Modules |
|----------|---------|
| **2 h** | 1 + slice of 2 (`hello_web` → `custom_tools` → `session_memory`) |
| **4 h** | 1 + 2 + start 3 (`sequential_pipeline` + notebook Part 1–2 discussion) |
| **Full day** | 1 → 2 → 3 (full multi-agent notebook + all workflow demos) → 4 |

---

## Demo commands (repeat for every session)

```bash
cd workshop
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements-workshop.txt
export GOOGLE_API_KEY="..."

cd demos
adk web .
```

---

## Verify install (optional)

```bash
cd workshop && source .venv/bin/activate && pytest tests/ -v
```
