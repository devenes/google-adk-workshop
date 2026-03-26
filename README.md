# ADK workshop

Hands-on materials for presenting the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) with a **local Python virtual environment**. For the original Colab-oriented lab, see [`ADK_Learning_tools.ipynb`](ADK_Learning_tools.ipynb). For the same learning arc on your laptop, see [`notebooks/ADK_Learning_tools_venv.ipynb`](notebooks/ADK_Learning_tools_venv.ipynb) (open from repo root with path `workshop/notebooks/...`).  
**Multi-agent orchestration** (router, `SequentialAgent`, `LoopAgent`, `ParallelAgent`): [`notebooks/ADK_Learning_tool_multi_agents.ipynb`](notebooks/ADK_Learning_tool_multi_agents.ipynb).

**Official companion course:** [ADK Crash Course — From Beginner to Expert](https://codelabs.developers.google.com/onramp/instructions#0) (Google Codelabs: GCP setup, Colab notebooks on tools/memory and multi-agents, Router / Sequential / Loop / Parallel patterns, and ADK Web appendices).

## Prerequisites

- Python **3.10+**
- A **Google AI Studio API key** ([get a key](https://ai.google.dev/gemini-api/docs/api-key)) **or** Vertex AI credentials (see [ADK authentication](https://google.github.io/adk-docs/))
- Optional: Google Cloud project if you use Vertex-only tools

## Virtual environment (use for every demo)

From the repository root:

```bash
cd workshop
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
cd workshop
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -U pip
pip install -r requirements-workshop.txt
```

### Environment variables

| Mode | Typical variables | Notes |
|------|-------------------|--------|
| **Gemini API (Developer API)** | `export GOOGLE_API_KEY="your-key"` | Easiest for workshops; used by demos by default. |
| **Vertex AI** | `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and Application Default Credentials | Use when demos or your key policy require Vertex. See [ADK docs](https://google.github.io/adk-docs/). |

Optional: put variables in `workshop/.env`; ADK Web loads per-agent `.env` when present.

### Jupyter kernel (optional)

```bash
python -m ipykernel install --user --name=adk-workshop --display-name="ADK Workshop"
```

Open the venv notebook and choose this kernel.

## Curriculum (beginner → advanced)

Structured learning paths, timing, and “what’s next” for expert topics are in [`CURRICULUM.md`](CURRICULUM.md).  
**Unified day-long path** (both notebooks + all demo tiers): [`COURSE_BEGINNER_TO_EXPERT.md`](COURSE_BEGINNER_TO_EXPERT.md).

## Runnable demos (`demos/`)

Each folder is one **ADK Web** app (contains `agent.py` with `root_agent`). From `workshop`, with the venv activated:

```bash
cd demos
adk web .
```

Then pick an app in the UI (e.g. `hello_web`, `day_trip_search`).

| Folder | Level | What it shows | Related upstream sample |
|--------|--------|----------------|------------------------|
| [`demos/hello_web`](demos/hello_web) | Beginner | Minimal agent; first `adk web` run | [`quickstart`](https://github.com/google/adk-python/tree/main/contributing/samples/quickstart) |
| [`demos/calculator_basics`](demos/calculator_basics) | Beginner | Simple numeric tools | [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) (patterns) |
| [`demos/custom_tools`](demos/custom_tools) | Beginner | Function tools (weather/time, errors) | [`quickstart`](https://github.com/google/adk-python/tree/main/contributing/samples/quickstart) |
| [`demos/static_kb_rag`](demos/static_kb_rag) | Intermediate | In-memory “RAG-shaped” retrieval | [`rag_agent`](https://github.com/google/adk-python/tree/main/contributing/samples/rag_agent) (production RAG) |
| [`demos/sequential_pipeline`](demos/sequential_pipeline) | Intermediate | `SequentialAgent` (outline → expand) | [`simple_sequential_agent`](https://github.com/google/adk-python/tree/main/contributing/samples/simple_sequential_agent) |
| [`demos/day_trip_search`](demos/day_trip_search) | Intermediate | Grounded itinerary with `google_search` | [`ADK_Learning_tools.ipynb`](ADK_Learning_tools.ipynb) Part 1 |
| [`demos/session_memory`](demos/session_memory) | Intermediate | `ToolContext.state` across turns | [`session_state_agent`](https://github.com/google/adk-python/tree/main/contributing/samples/session_state_agent) |
| [`demos/multi_agent_coordinator`](demos/multi_agent_coordinator) | Advanced | Coordinator + specialist sub-agents | [`hello_world_ma`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_ma) |
| [`demos/structured_output`](demos/structured_output) | Advanced | Pydantic `output_schema` | [`output_schema_with_tools`](https://github.com/google/adk-python/tree/main/contributing/samples/output_schema_with_tools) |
| [`demos/hitl_sensitive_action`](demos/hitl_sensitive_action) | Advanced | Tool confirmation (`require_confirmation`) | [`tool_human_in_the_loop_config`](https://github.com/google/adk-python/tree/main/contributing/samples/tool_human_in_the_loop_config) |
| [`demos/loop_plan_refine`](demos/loop_plan_refine) | Expert | `LoopAgent` + `exit_loop` (plan / critic / refiner) | [`ADK_Learning_tool_multi_agents.ipynb`](notebooks/ADK_Learning_tool_multi_agents.ipynb) |
| [`demos/parallel_research_synth`](demos/parallel_research_synth) | Expert | `ParallelAgent` → synthesis (`output_key` merge) | same notebook |

**Note:** `google_search` may require an eligible Gemini model and account; if it fails in the room, use `hello_web` or `custom_tools` as fallback (see [`PRESENTER_GUIDE.md`](PRESENTER_GUIDE.md)).

## Verify demos locally

With venv activated, from `workshop`:

```bash
pip install -r requirements-workshop.txt
pytest tests/ -v
```

## Learning diagrams

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for Mermaid diagrams (agent/runner/session/tool flow).

## Presenter script

See [`PRESENTER_GUIDE.md`](PRESENTER_GUIDE.md) for timing, fallbacks, and links to [adk-docs](https://google.github.io/adk-docs/) and [adk-samples](https://github.com/google/adk-samples).

## Reference

This workshop material was developed using Google’s official ADK resources as reference, including the [Agent Development Kit documentation](https://google.github.io/adk-docs/), the open-source [adk-python](https://github.com/google/adk-python) project (and its `contributing/samples`), the [ADK Crash Course codelab](https://codelabs.developers.google.com/onramp/instructions#0), and the accompanying learning notebooks in this folder. It is not an official Google product.
