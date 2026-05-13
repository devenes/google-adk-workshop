"""Simple HITL demo: agent asks the user for confirmation before sending an email."""

# Agent is the core ADK class.
from google.adk import Agent


# --- Simulated sensitive action ---
def send_email(to: str, subject: str, body: str) -> str:
  """Send an email to the specified recipient (simulated).

  Args:
      to: Recipient email address.
      subject: Email subject line.
      body: Email body text.

  Returns:
      Confirmation string after the simulated send.
  """
  # DEMO ONLY: prints instead of sending a real email.
  return f"(simulated) Email sent to {to!r} with subject {subject!r} — body: {body!r}."


# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="hitl_email_agent",

    # model: Gemini model that decides when to call the tools.
    model="gemini-2.5-flash-lite",

    # description: Short summary for orchestrators.
    description="Sends emails only after explicit user confirmation.",

    # instruction: Forces the agent to ask the user before calling send_email.
    # This is the human-in-the-loop gate — the agent must pause and wait for
    # a "yes" reply before proceeding. If the user says no, it must cancel.
    instruction=(
        "You help users send emails.\n"
        "\n"
        "IMPORTANT: Before calling send_email you MUST ask the user:\n"
        "  'Are you sure you want to send this email to [to] with subject [subject]?\n"
        "   Reply YES to confirm or NO to cancel.'\n"
        "\n"
        "Wait for the user's reply:\n"
        "- If they say YES → call send_email with the details.\n"
        "- If they say NO  → cancel and confirm cancellation.\n"
        "Never call send_email without explicit user approval first."
    ),

    # tools: Only the sensitive action — no extra helper tools needed.
    tools=[send_email],
)
