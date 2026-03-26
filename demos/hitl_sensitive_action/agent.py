"""Advanced demo: tool execution gated by user confirmation (HITL-style)."""

from google.adk import Agent
from google.adk.tools.function_tool import FunctionTool


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
  return (
      f"(simulated) Deleted all records for customer_id={customer_id!r} "
      f"(reason={reason!r})."
  )


_delete_tool = FunctionTool(
    simulate_delete_customer_data,
    require_confirmation=True,
)

root_agent = Agent(
    name="hitl_sensitive_agent",
    model="gemini-2.5-flash",
    description="Demonstrates confirmation before a destructive tool runs.",
    instruction=(
        "You help with GDPR-style demos. Only call simulate_delete_customer_data "
        "when the user explicitly requests deletion for a specific customer_id. "
        "Remind them the action is simulated once approved."
    ),
    tools=[_delete_tool],
)
