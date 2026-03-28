# Demo checkpoints (hands-on)

After **`cd workshop/demos && adk web .`**, pick an app and verify:

| App | Say / do | Pass if |
|-----|-----------|---------|
| 01-hello_web | Any greeting | Plain model reply |
| 02-calculator_basics | "What is 125 * 437?" | Correct product |
| 03-custom_tools | Roll die; prime test | Tool calls + plausible results |
| 04-static_kb_rag | Question about snippets file | Cites KB tool |
| 07-sequential_pipeline | Outline a topic | Two-step flow (outline → expand) |
| 05-day_trip_search | Day trip in a city | Search / itinerary (needs eligible `google_search`) |
| 06-session_memory | Name then ask to recall | `ToolContext.state` persists |
| 08-sequential_state_shared | Dinner venue + directions | Second step uses `{destination}` from first |
| 09-live_weather_nws | "Forecast for Seattle" | NWS-style snippet (US cities in tool map) |
| 12-agent_as_tool_orchestrator | Facts about a famous person | `wiki_specialist` or Wikipedia tool run |
| 11-multi_agent_coordinator | Stock quote + prime check | Coordinator delegates |
| 13-structured_output | Trip JSON request | Response matches schema |
| 15-structured_persona_research | "PersonInfo for …" | Structured fields + optional specialist |
| 14-hitl_sensitive_action | Sensitive demo flow | Confirmation when configured |
| 16-loop_plan_refine | Improve a short plan | Loop / critic pattern |
| 17-parallel_research_synth | City weekend plan | Parallel agents + synthesis |

**YAML-only app:** `10-agent_config_yaml` — no `root_agent` in `agent.py`; ADK loads `root_agent.yaml` + `tools.py`.

See per-demo READMEs for level tags.
