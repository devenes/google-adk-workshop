"""Intermediate demo: retrieval over a tiny in-memory KB (RAG-shaped, no Vertex)."""

# Agent is the core ADK class connecting a Gemini model with tools and instructions.
from google.adk import Agent

# --- Knowledge Base ---
# RAG stands for Retrieval-Augmented Generation.
# Instead of relying on the model's training data, we store facts here and search them at runtime.
# This is a tiny in-memory dictionary; a real system would use a vector database or search index.
# The keys are topic names; the values are the policy text the agent is allowed to cite.
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


# --- Tool: search_company_kb ---
def search_company_kb(query: str) -> str:
  """Search internal policy snippets by topic or keywords (demo).

  Args:
      query: User question or keywords (e.g. billing, rate limit, retention).

  Returns:
      Matching snippets as plain text, or a short message if nothing fits.
  """
  # Lowercase the query so matching is case-insensitive.
  q = query.lower()

  # hits will collect all snippets that are relevant to the query.
  hits: list[str] = []

  # Loop over every entry in the knowledge base dictionary.
  for key, text in _KB_SNIPPETS.items():
    # Convert underscores to spaces for a friendlier readable label, e.g. "billing cycle".
    readable = key.replace("_", " ")

    # Check three different ways the query might match this KB entry:
    if (
        readable in q  # 1. The full topic name appears in the query ("billing cycle").
        or key.replace("_", "") in q.replace(" ", "")  # 2. Compact match ignoring spaces.
        or any(token in text.lower() for token in q.split() if len(token) > 3)
        # 3. Any query word longer than 3 letters appears inside the snippet text.
    ):
      # Format the matching snippet with a Markdown heading and add to results list.
      hits.append(f"### {readable}\n{text}")

  # If no snippets matched, tell the agent which topics ARE available.
  if not hits:
    return (
        "No snippets matched. Topics in this demo KB: billing_cycle, "
        "api_rate_limits, data_retention."
    )

  # Join all matching snippets with a blank line between them and return as one string.
  return "\n\n".join(hits)


# --- Agent definition ---
root_agent = Agent(
    # name: Unique label for this agent.
    name="static_kb_agent",

    # model: The Gemini model that reads the query and decides to call search_company_kb.
    model="gemini-2.5-flash",

    # description: Used by orchestrators to decide when to delegate to this agent.
    description="Answers from a small static knowledge base via search_company_kb.",

    # instruction: Tells the model to always use the tool and never invent policy.
    instruction=(
        "Use search_company_kb whenever the user asks about company policy in this "
        "demo (billing, API limits, retention). Cite the snippets in your answer; "
        "do not invent policy."
    ),

    # tools: The search function above — the model calls it with the user's query.
    tools=[search_company_kb],
)
