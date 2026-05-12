# Demo checkpoints (hands-on)

From **`cd demos && adk web .`**, pick an app and verify:

| App                            | Say / do                     | Pass if                                             |
| ------------------------------ | ---------------------------- | --------------------------------------------------- |
| hello_web                      | Any greeting                 | Plain model reply                                   |
| calculator_basics              | "What is 125 \* 437?"        | Correct product                                     |
| custom_tools                  | Weather/time + errors          | Tool calls + plausible results                      |
| static_kb_rag                  | Question about snippets file | Cites KB tool                                       |
| sequential_pipeline            | Outline a topic              | Two-step flow (outline → expand)                    |
| day_trip_search                | Day trip in a city           | Search / itinerary (needs eligible `google_search`) |
| session_memory                 | Name then ask to recall      | `ToolContext.state` persists                        |
| sequential_state_shared         | Dinner venue + directions    | Second step uses `{destination}` from first         |
| live_weather_nws               | "Forecast for Seattle"       | NWS-style snippet (US cities in tool map)           |
| agent_as_tool_orchestrator     | Facts about a famous person  | `search_specialist` (google_search-backed)           |
| multi_agent_coordinator        | Dice roll + prime check      | Coordinator delegates                               |
| structured_output              | Trip JSON request            | Response matches schema                             |
| structured_persona_research     | "PersonInfo for …"           | Structured fields + optional specialist             |
| hitl_sensitive_action          | Sensitive demo flow          | Confirmation when configured                        |
| loop_plan_refine               | Improve a short plan         | Loop / critic pattern                               |
| parallel_research_synth         | City weekend plan            | Parallel agents + synthesis                         |

## Workshop command contract

From repository root:

```bash
python3 -m pytest tests/ -v
python3 -m pytest tests/test_demos.py -q
adk eval demos/<demo_folder> eval/<evalset_file>.evalset.json
```

**YAML-config app:** `agent_config_yaml` is loaded via `root_agent.yaml` and `tools.py` with package entry compatibility.

## Malformed-input checkpoints

- `custom_tools`
  - Try non-text input for weather/time city (for example `123`) and verify the tool returns a clear validation error.
  - Try blank city input and verify message asks for a city name.
  - Try `None` for weather/time inputs.
- `hitl_sensitive_action`
  - Try calling `send_email` with invalid `to` and non-text `subject` / `body`.
  - Verify empty `subject` and empty `body` return explicit validation messages.
- `multi_agent_coordinator`
  - Ask to roll a die with non-text / boolean / fractional inputs and expect validation.
  - Ask to check primes with non-list input and expect validation.
  - Ask to check primes with a non-integer candidate and expect candidate-specific validation.
- `parallel_research_synth`
  - Ask for `research_museums`, `research_events`, and `research_food` with invalid city values and expect `"Invalid city input..."`.
- `static_kb_rag`
  - Ask the KB tool for non-text input (for example `123`) and verify it returns a clear query guidance message.
  - Ask with empty/whitespace-only input and verify keyword guidance.
- `session_memory`
  - Send `remember_display_name` with empty input or non-text input and verify it returns an explicit validation message.
- `live_weather_nws`
  - Ask for a blank city and verify the response is a friendly invalid-input message.
  - Ask for malformed city text (for example blank/only comma) and verify no network call:
    `"City value is empty..."`.
  - Ask for unsupported city variants (for example `AtLanTiS, WA`) and verify normalized
    message format, e.g. `"Unsupported city 'atlantis'. Try: ..."` without network.

## Validation notes

- Live-weather malformed-input checks should be asserted with request mocking so invalid payloads never call the NWS API.

## Post-change smoke check suggestions

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
python3 -m pip install -r requirements-workshop.txt
python3 -m pytest tests/ -v
python3 -m pytest tests/test_demos.py -q
python scripts/check_api_key_leaks.py
```

Expected sequence output shape after dependency setup:
- `python3 -m venv .venv` and install succeed without error.
- `python3 -m pytest tests/test_demos.py -q` (and `python3 -m pytest tests/ -v`) should execute and report `failed 0`.

See per-demo READMEs for level tags.
