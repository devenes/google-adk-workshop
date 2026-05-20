# grounded_qa_agent

**Level:** Advanced — **Native URL Grounding** (`url_context`).

This demo showcases how to equip an agent with Gemini 2.x's native `url_context` grounding tool, allowing it to fetch, parse, and reason over the live contents of arbitrary URLs provided by the user.

## Architecture

```text
       [User Prompt with URL, e.g. https://example.com]
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 grounded_qa_agent                       │
│            model: gemini-2.5-flash-lite                 │
│                                                         │
│     Uses built-in tool: url_context                     │
└─────────────────────────────────────────────────────────┘
        │                                          ▲
        ▼ (requests URL)                           │ (webpage body)
┌─────────────────────────────────────────────────────────┐
│          Gemini Built-in HTTP Scraper                   │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
            [Grounded Response citing webpage]
```

## Concepts

1. **`url_context`**: A native model-side tool for fetching web pages. Unlike custom scrapers, this is handled directly by the Gemini API, requiring zero local setup.
2. **Real-time Grounding**: Allows the agent to answer questions about dynamic or freshly updated content on the web by pointing it directly to the source.

## Run and Try

Run the web interface:
```bash
cd demos && adk web .
```
And select `grounded_qa_agent`. Try asking:
* "Summarize the content of the page https://example.com"
* "What is the primary message of https://www.google.com?"
