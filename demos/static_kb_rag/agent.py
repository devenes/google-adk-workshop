"""Intermediate demo: retrieval over a tiny in-memory KB (RAG-shaped, no Vertex)."""

from google.adk import Agent

_KB_SNIPPETS: dict[str, str] = {
    "billing_cycle": (
        "Billing cycles close on the last day of each month. Invoices are "
        "sent within 48 hours."
    ),
    "api_rate_limits": (
        "Default API quota is 1,000 requests per minute per project. "
        "Contact support for a limit increase."
    ),
    "data_retention": (
        "Workspace analytics are retained for 90 days unless an extended "
        "retention addon is enabled."
    ),
}


def search_company_kb(query: str) -> str:
  """Search internal policy snippets by topic or keywords (demo).

  Args:
      query: User question or keywords (e.g. billing, rate limit, retention).

  Returns:
      Matching snippets as plain text, or a short message if nothing fits.
  """
  q = query.lower()
  hits: list[str] = []
  for key, text in _KB_SNIPPETS.items():
    readable = key.replace("_", " ")
    if (
        readable in q
        or key.replace("_", "") in q.replace(" ", "")
        or any(token in text.lower() for token in q.split() if len(token) > 3)
    ):
      hits.append(f"### {readable}\n{text}")
  if not hits:
    return (
        "No snippets matched. Topics in this demo KB: billing_cycle, "
        "api_rate_limits, data_retention."
    )
  return "\n\n".join(hits)


root_agent = Agent(
    name="static_kb_agent",
    model="gemini-2.5-flash",
    description="Answers from a small static knowledge base via search_company_kb.",
    instruction=(
        "Use search_company_kb whenever the user asks about company policy in this "
        "demo (billing, API limits, retention). Cite the snippets in your answer; "
        "do not invent policy."
    ),
    tools=[search_company_kb],
)
