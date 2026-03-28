# 04-static_kb_rag

**Level:** Intermediate (retrieval / “RAG-shaped” pattern without managed Vertex corpus).

**Goal:** One **retrieval tool** returns context; the model **grounds** its answer in that text.

## Architecture

```text
┌──────────────────────────────────────────────┐
│              static_kb_agent                  │  ← root agent
│              model: gemini-flash-lite         │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │         search_company_kb(query)        │  │  ← retrieval tool
│  └────────────────────┬───────────────────┘  │
└───────────────────────┼──────────────────────┘
                        │ keyword lookup
                        ▼
              ┌─────────────────┐
              │  in-memory KB   │  (billing, API limits,
              │  (dict)         │   data retention …)
              └─────────────────┘
```

## Try it

```text
What are our API rate limits?
```

```text
How long is data retained?
```

```text
What authentication methods are supported?
```

**Production next step:** Swap the tool body for [VertexAiRagRetrieval](https://github.com/google/adk-python/blob/main/contributing/samples/rag_agent/agent.py) or your vector store.
