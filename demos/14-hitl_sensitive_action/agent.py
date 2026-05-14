"""Simple HITL demo: agent asks the user for confirmation before sending an email."""

# Agent is the core ADK class.
from google.adk import Agent


# --- Simulated sensitive action ---
def _is_valid_email(address: str) -> bool:
  """Return True when the value looks like a simple recipient email address."""
  if not address or address.startswith("@") or address.endswith("@"):
    return False
  if " " in address or address.count("@") != 1:
    return False
  local, domain = address.split("@", 1)
  if not local or not domain:
    return False
  if (
      "." not in domain
      or domain.startswith(".")
      or domain.endswith(".")
      or local.startswith(".")
      or local.endswith(".")
      or domain.startswith("-")
      or domain.endswith("-")
  ):
    return False
  return True


def send_email(to: str, subject: str, body: str) -> str:
  """Send an email to the specified recipient (simulated).

  Args:
      to: Recipient email address.
      subject: Email subject line.
      body: Email body text.

  Returns:
      Confirmation string after the simulated send.
  """
  if not isinstance(to, str):
    return "Invalid recipient. Please provide a text email address."

  to_value = to.strip()
  if not to_value:
    return "Recipient email is required."

  if not _is_valid_email(to_value):
    return "Invalid recipient email. Please provide a valid email address."

  if not isinstance(subject, str):
    return "Invalid subject. Please provide the email subject as text."
  subject_value = subject.strip()
  if not subject_value:
    return "Email subject is required."

  if not isinstance(body, str):
    return "Invalid body. Please provide the email body as text."
  body_value = body.strip()
  if not body_value:
    return "Email body is required."

  # DEMO ONLY: returns a simulated response instead of sending a real email.
  return (
      f"(simulated) Email sent to {to_value!r} with subject {subject_value!r} — "
      f"body: {body_value!r}."
  )


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
