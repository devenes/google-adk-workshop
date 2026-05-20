"""Advanced demo: Python code execution inside Gemini's native sandbox.

KEY CONCEPT — Why code execution?
LLMs are probabilistic and can make arithmetic mistakes, especially for:
  - Multi-step calculations (e.g. compound interest, prime factorisation)
  - Sorting, counting, or string transformation tasks
  - Any task where precision is required

The BuiltInCodeExecutor delegates computation to a real Python interpreter
embedded in the Gemini API — so the answer is always exact.

HOW IT WORKS:
  1. User sends a question.
  2. Gemini writes Python code to solve it.
  3. The built-in sandbox executes the code.
  4. The output (stdout) is fed back to Gemini.
  5. Gemini summarises the result for the user.

No local Python subprocess is started — execution happens server-side.

SECURITY & ISOLATION:
  - The code runs in an isolated, secure sandbox environment managed by Google.
  - It has NO access to your local filesystem, environment variables, or local network.
  - It has NO external internet connectivity (no API requests, curl, etc.).
  - It is completely safe to run, even if the model generates malicious-looking code.
"""

from google.adk import Agent

# BuiltInCodeExecutor signals ADK to attach the native code_execution tool to the
# Gemini API request. It requires a Gemini 2.x model (gemini-2.5-flash-lite or later).
from google.adk.code_executors import BuiltInCodeExecutor

# --- Agent definition ---
root_agent = Agent(
    name="code_execution_agent",

    # gemini-2.5-flash-lite supports the built-in code execution tool.
    # Gemini 1.x models do NOT support it — ADK will raise a ValueError if you try.
    model="gemini-2.5-flash-lite",

    description=(
        "Solves mathematical and computational problems by writing and running "
        "Python code in a secure server-side sandbox."
    ),

    instruction=(
        "You have access to a Python code execution environment.\\n"
        "\\n"
        "For any calculation, sorting, or text manipulation task:\\n"
        "  1. Write concise Python code to solve the problem.\\n"
        "  2. Execute it to get the exact result.\\n"
        "  3. Explain the result in plain language.\\n"
        "\\n"
        "Always run the code — never guess a numeric answer without executing it first."
    ),

    # code_executor: Attaches Gemini's built-in Python sandbox.
    # BuiltInCodeExecutor() requires no local setup — code runs server-side.
    # Contrast this with local/custom command execution which runs on the user's host machine.
    code_executor=BuiltInCodeExecutor(),
)
