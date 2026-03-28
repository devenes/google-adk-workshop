# Presenter guide: ADK conference workshop

Use this script with [`README.md`](README.md), [`CURRICULUM.md`](CURRICULUM.md), [`COURSE_BEGINNER_TO_EXPERT.md`](COURSE_BEGINNER_TO_EXPERT.md), and [`demos/`](demos/). Always tell attendees to **create and activate a venv** before `pip install` (repeat the snippet from the README in the first hands-on block).

## Quick links

- Hands-on checkpoints: [`demos/CHECKPOINTS.md`](demos/CHECKPOINTS.md); learner rubric: [`RUBRIC.md`](RUBRIC.md); eval / deploy stubs: [`EVAL.md`](EVAL.md), [`DEPLOY.md`](DEPLOY.md); callbacks & memory primer: [`LEARNING_DEEP_DIVE.md`](LEARNING_DEEP_DIVE.md); MCP/OpenAPI: [`INTEGRATIONS.md`](INTEGRATIONS.md)
- Documentation: [google.github.io/adk-docs](https://google.github.io/adk-docs/)
- Samples (broader than this repo’s `contributing/samples`): [github.com/google/adk-samples](https://github.com/google/adk-samples)
- Python ADK source: [github.com/google/adk-python](https://github.com/google/adk-python)

## Formats (pick one)

| Format | Suggested live demos | Skip / slide only |
|--------|----------------------|-------------------|
| **45 min** | venv + `01-hello_web` + `02-calculator_basics` or `03-custom_tools` + 5 min Q&A | `05-day_trip_search` (show on slide), `14-hitl_sensitive_action` clip |
| **90 min** | Follow **Beginner → Intermediate** in [`CURRICULUM.md`](CURRICULUM.md): e.g. `04-static_kb_rag`, `05-day_trip_search`, `06-session_memory`, `07-sequential_pipeline` | Expert-only topics (Vertex RAG, MCP) |
| **Half-day** | Full curriculum through **Advanced** + **Expert workflows** (`16-loop_plan_refine`, `17-parallel_research_synth`) + [`ADK_Learning_tool_multi_agents.ipynb`](notebooks/ADK_Learning_tool_multi_agents.ipynb) highlights | Self-study: MCP, `adk eval`, production deploy |

## 45-minute timeline (tight)

| Minutes | Segment | Do / say |
|---------|---------|----------|
| 0–5 | Hook | Agents as code: instructions + model + tools; ADK gives Runner, sessions, Web UI, deploy paths. |
| 5–10 | Venv | Live: `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements-workshop.txt`, `export GOOGLE_API_KEY=...`. |
| 10–22 | First run | `cd demos && adk web .` → open `01-hello_web`. Prompt: “Explain what ADK is in one paragraph.” Show trace/tool-less reply. |
| 22–35 | Tools | Switch to `02-calculator_basics` (“(19.5+2)*3”) or `03-custom_tools` (weather/time). Mention type hints → tool schema. |
| 35–42 | Wrap | Point to [`CURRICULUM.md`](CURRICULUM.md): search, state, sequential flow, HITL. Show one diagram from [`ARCHITECTURE.md`](ARCHITECTURE.md). |
| 42–45 | Q&A | Google Search needs eligible API; Vertex alternative per docs. |

## 90-minute timeline

| Minutes | Segment | Do / say |
|---------|---------|----------|
| 0–10 | Problem + ADK value | Code-first, testable, composable; same agent can run locally and on Cloud Run / Vertex AI Agent Engine. |
| 10–18 | Venv + verification | Same as README; run `pytest tests/ -v` once (optional but impressive for engineers). |
| 18–28 | `01-hello_web` + `02-calculator_basics` | Dev UI basics; first tool calls. |
| 28–40 | `03-custom_tools` + `04-static_kb_rag` | Parallel tools vs a **retrieval**-style tool. |
| 40–50 | `05-day_trip_search` | `google_search` grounding; note latency / account requirements. |
| 50–60 | `07-sequential_pipeline` + `06-session_memory` | Fixed order vs **session state** across turns. |
| 60–72 | `11-multi_agent_coordinator` + `13-structured_output` | Delegation; then **Pydantic** output for apps. |
| 72–82 | `14-hitl_sensitive_action` | Approve/reject dangerous tool; link to docs. |
| 82–88 | Notebook or expert pointers | `ADK_Learning_tools_venv.ipynb` or [`CURRICULUM.md`](CURRICULUM.md) Expert row. |
| 88–90 | Q&A | Hand out README + link to adk-samples. |

## Half-day (module menu)

1. **Setup** (20 min): README venv + `pytest tests/ -v`.
2. **Beginner block** (45 min): [`CURRICULUM.md`](CURRICULUM.md) Level 0 + Beginner demos.
3. **Intermediate block** (60 min): `04-static_kb_rag` through `07-sequential_pipeline`.
4. **Advanced block** (60 min): `11-multi_agent_coordinator`, `13-structured_output`, `14-hitl_sensitive_action`.
5. **Notebook** (45 min): `ADK_Learning_tools_venv.ipynb` Parts 0–3.
6. **Expert stretch** (optional): Expert table in [`CURRICULUM.md`](CURRICULUM.md), [HITL docs](https://google.github.io/adk-docs/tools/confirmation/), `adk eval`, [adk-samples](https://github.com/google/adk-samples).

## Failure fallbacks (read before the talk)

| Issue | Fallback |
|-------|----------|
| `google_search` errors or disabled | Use `01-hello_web` + `03-custom_tools` only; explain search as “upgrade path” with billing/model eligibility. |
| No API key | Do not run live LLM; walk through `agent.py` files and ARCHITECTURE.md; run `pytest` (imports still validate structure if ADK installed). |
| `adk web` port blocked | Try another port per ADK CLI help; or run notebook with `Runner` only (Part 1 cells). |
| Slow Wi-Fi | Pre-record a short screen capture of `adk web` for `03-custom_tools`. |

## Demo commands cheat sheet

```bash
cd workshop && source .venv/bin/activate
export GOOGLE_API_KEY="..."

cd demos
adk web .
```

## Suggested prompts (copy/paste)

- **hello_web:** “In three bullets, what problems does ADK solve for developers?”
- **calculator_basics:** “Compute (19.5 + 2) multiplied by 3 using your tools.”
- **day_trip_search:** “Budget frugal, mood relaxed, city Barcelona—morning afternoon evening markdown itinerary.”
- **custom_tools:** “What’s the weather and local time in New York?”
- **static_kb_rag:** “Summarize our API rate limits and data retention policy.”
- **sequential_pipeline:** “Topic: why observability matters for LLM apps.”
- **multi_agent_coordinator:** “Roll a 20-sided die and tell me if the number is prime.”
- **session_memory:** Turn 1: “Remember my display name is Sam.” Turn 2: “What display name did I give you?”
- **structured_output:** “Give a CityProfile for Lisbon, Portugal.”
- **hitl_sensitive_action:** “Delete all data for customer_id=demo-001 (reason=GDPR request).” Then approve or reject in the UI.
- **loop_plan_refine:** “Plan two concrete steps to prepare a 15-minute talk on LoopAgent.”
- **parallel_research_synth:** “Weekend in Chicago—museums, events, and food ideas.”

## Assessment (optional)

Attendees can confirm setup with:

```bash
cd workshop && source .venv/bin/activate
pytest tests/ -v
```
