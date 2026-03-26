"""Session-scoped memory via ToolContext.state (workshop)."""

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext


def remember_display_name(display_name: str, tool_context: ToolContext) -> str:
  """Store the user's preferred display name for this session.

  Args:
      display_name: Name the user wants to be called.

  Returns:
      Confirmation message.
  """
  tool_context.state["user_display_name"] = display_name.strip()
  return f"Got it — I'll remember you as {display_name.strip()} for this session."


def recall_display_name(tool_context: ToolContext) -> str:
  """Recall the display name stored for this session, if any."""
  name = tool_context.state.get("user_display_name")
  if not name:
    return "No display name is stored yet. Ask the user what to call them."
  return f"The user's display name is: {name}"


root_agent = Agent(
    name="session_memory_workshop_agent",
    model="gemini-2.5-flash",
    description="Remembers a display name for the conversation using session state.",
    instruction="""
You help users with a simple personal memory demo.
- When they give a name or ask you to remember what to call them, use remember_display_name.
- When they ask what you remember, use recall_display_name.
Keep replies short and friendly.
""",
    tools=[remember_display_name, recall_display_name],
)
