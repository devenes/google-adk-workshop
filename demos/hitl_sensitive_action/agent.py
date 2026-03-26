"""Advanced demo: tool execution gated by user confirmation (HITL-style)."""

# Agent is the core ADK class.
from google.adk import Agent

# FunctionTool wraps a Python function as an ADK tool and exposes extra options,
# such as require_confirmation which pauses execution until the user approves.
from google.adk.tools.function_tool import FunctionTool


# --- Simulated Destructive Action ---
# DEMO ONLY: This function prints a message instead of deleting anything.
# In a real system you would need authentication, audit logs, and hard confirmation steps.
def simulate_delete_customer_data(
    customer_id: str,
    reason: str,
) -> str:
  """DEMO ONLY: Pretend to irreversibly delete all data for a customer.

  In production you would guard this with authz, audit logs, and confirmations.

  Args:
      customer_id: Customer identifier.
      reason: Business reason for deletion.

  Returns:
      Confirmation message after the simulated operation.
  """
  # !r formats the strings with quotes, e.g. customer_id='C001' — makes the log clear.
  return (
      f"(simulated) Deleted all records for customer_id={customer_id!r} "
      f"(reason={reason!r})."
  )


# --- Wrapping the function with FunctionTool ---
# We do NOT pass the function directly to tools=[] this time.
# Instead, FunctionTool lets us set require_confirmation=True, which tells ADK to
# pause and ask the user "Do you want to run this?" before actually executing the function.
_delete_tool = FunctionTool(
    simulate_delete_customer_data,  # The Python function to wrap.
    require_confirmation=True,       # Human-in-the-loop: user must approve before execution.
)

# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="hitl_sensitive_agent",

    # model: Gemini model that decides when the deletion tool should be called.
    model="gemini-2.5-flash",

    # description: Short summary for orchestrators.
    description="Demonstrates confirmation before a destructive tool runs.",

    # instruction: Restricts the agent to only call the tool when there is explicit intent.
    instruction=(
        "You help with GDPR-style demos. Only call simulate_delete_customer_data "
        "when the user explicitly requests deletion for a specific customer_id. "
        "Remind them the action is simulated once approved."
    ),

    # tools: Pass the FunctionTool wrapper (not the raw function) so require_confirmation works.
    tools=[_delete_tool],
)
