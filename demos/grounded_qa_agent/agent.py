"""Advanced demo: native URL grounding using Gemini's built-in url_context tool.

KEY CONCEPT — What is grounding?
Without grounding, Gemini answers from its training data, which can be:
  - Stale (knowledge cutoff)
  - Hallucinated (confident but incorrect facts)

The url_context tool lets the model fetch the *live* content of a URL you
provide, so its answer is grounded in the actual page text at request time.

HOW IT WORKS:
  1. User provides a URL in their message.
  2. Gemini detects the URL and calls the url_context tool internally.
  3. The Gemini API fetches the page content server-side (no local HTTP calls).
  4. The page body is injected into the model's context window.
  5. Gemini answers using the retrieved text and cites relevant parts.

IMPORTANT CONSTRAINTS:
  - Only works with Gemini 2.x models.
  - The URL must be publicly accessible (no login-walls, captcha protection, or heavy client-side JS rendering).
  - Very large pages may be truncated to fit the context window.
  - The fetching is done directly by Google's backend — not by your local machine.
"""

from google.adk import Agent

# url_context is a built-in ADK tool singleton — no class instantiation needed.
# Adding it to tools= tells ADK to register the url_context tool declaration
# with the Gemini API on every request.
# Unlike custom scraping tools (which might use requests/BeautifulSoup locally),
# url_context delegates retrieval to Google's highly-optimized crawler service.
from google.adk.tools import url_context

# --- Agent definition ---
root_agent = Agent(
    name="grounded_qa_agent",

    # Gemini 2.x required — url_context is not available on 1.x models.
    model="gemini-2.5-flash-lite",

    description=(
        "Answers questions grounded in live content fetched from user-provided URLs. "
        "Prevents hallucination by reading the actual page before responding."
    ),

    instruction=(
        "You have access to the url_context tool, which fetches and reads web pages.\\n"
        "\\n"
        "When a user provides a URL or asks about a web page:\\n"
        "  1. Use url_context to retrieve the page content.\\n"
        "  2. Answer based ONLY on what the page actually says.\\n"
        "  3. Cite the relevant sentences or sections from the page.\\n"
        "  4. If the page cannot be fetched, say so and explain.\\n"
        "\\n"
        "Never invent information — if it is not on the page, say 'I could not find that on the page.'"
    ),

    # tools: Registering url_context enables the native URL fetching capability.
    # url_context is a singleton — do NOT call url_context() with parentheses.
    # The model decides when to invoke it based on the presence of URLs in the prompt.
    tools=[url_context],
)
