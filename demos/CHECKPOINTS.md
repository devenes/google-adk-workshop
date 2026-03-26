# Demo checkpoints (hands-on)

After **`cd workshop/demos && adk web .`**, pick an app and verify:

| App | Say / do | Pass if |
|-----|-----------|---------|
| hello_web | Any greeting | Plain model reply |
| calculator_basics | "What is 125 * 437?" | Correct product |
| custom_tools | Roll die; prime test | Tool calls + plausible results |
| static_kb_rag | Question about snippets file | Cites KB tool |
| sequential_pipeline | Outline a topic | Two-step flow (outline → expand) |
| day_trip_search | Day trip in a city | Search / itinerary (needs eligible `google_search`) |
| session_memory | Name then ask to recall | `ToolContext.state` persists |
| sequential_state_shared | Dinner venue + directions | Second step uses `{destination}` from first |
| live_weather_nws | "Forecast for Seattle" | NWS-style snippet (US cities in tool map) |
| agent_as_tool_orchestrator | Facts about a famous person | `wiki_specialist` or Wikipedia tool run |
| multi_agent_coordinator | Stock quote + prime check | Coordinator delegates |
| structured_output | Trip JSON request | Response matches schema |
| structured_persona_research | "PersonInfo for …" | Structured fields + optional specialist |
| hitl_sensitive_action | Sensitive demo flow | Confirmation when configured |
| loop_plan_refine | Improve a short plan | Loop / critic pattern |
| parallel_research_synth | City weekend plan | Parallel agents + synthesis |

**YAML-only app:** `agent_config_yaml` — no `root_agent` in `agent.py`; ADK loads `root_agent.yaml` + `tools.py`.

See per-demo READMEs for level tags.
