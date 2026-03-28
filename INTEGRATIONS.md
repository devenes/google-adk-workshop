# MCP, OpenAPI, and external tools

## Model Context Protocol (MCP)

- MCP exposes tools hosted in another process; ADK can attach MCP toolsets per project configuration.
- Upstream example: [`tool_mcp_stdio_notion_config`](https://github.com/google/adk-python/tree/main/contributing/samples/tool_mcp_stdio_notion_config) in **adk-python**.
- Workshop path: after learners are comfortable with `FunctionTool`, show MCP as “same contract, different transport.”

## OpenAPI / REST tools

- Many teams wrap internal HTTP APIs as **function tools** (see `09-live_weather_nws` for a small public example).
- For large OpenAPI specs, generate or map operations to tools following your org’s ADK patterns; see ADK docs on tool design and authentication.

## Wikipedia / NWS

- `12-agent_as_tool_orchestrator` and `15-structured_persona_research` use the **Wikipedia REST** summary API.
- `09-live_weather_nws` uses **`api.weather.gov`** (US, rate limits apply).

Always respect third-party terms of use and caching policies in production.
