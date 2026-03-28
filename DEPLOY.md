# Deployment pointers

Workshop demos target **local `adk web`**. For production:

- **Cloud Run / Vertex AI Agent Engine:** follow [Deploy – ADK docs](https://google.github.io/adk-docs/deploy/).
- **Secrets:** never commit API keys; use Secret Manager or runtime env vars in the target platform.
- **Models:** confirm the same model IDs (`gemini-2.5-flash-lite`, etc.) are available in your region and billing project.
- **Tooling:** HTTP tools (`09-live_weather_nws`, Wikipedia helpers) need outbound network from the deployed environment.

After first deploy, re-run the same **checkpoint prompts** from [`demos/CHECKPOINTS.md`](demos/CHECKPOINTS.md) against the hosted endpoint.
