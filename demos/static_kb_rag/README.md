# static_kb_rag

**Level:** Intermediate (retrieval / “RAG-shaped” pattern without managed Vertex corpus).

**Goal:** One **retrieval tool** returns context; the model **grounds** its answer in that text.

**Try:** “What are our API rate limits?” / “How long is data retained?”

**Production next step:** Swap the tool body for [VertexAiRagRetrieval](https://github.com/google/adk-python/blob/main/contributing/samples/rag_agent/agent.py) or your vector store.
