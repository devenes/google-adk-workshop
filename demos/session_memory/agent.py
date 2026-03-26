"""Session-scoped memory via ToolContext.state (workshop)."""

# Agent is the core ADK class.
from google.adk import Agent

# ToolContext is automatically injected by ADK when a tool function includes it as a parameter.
# It gives tools access to the current session's state dictionary and other runtime information.
from google.adk.tools.tool_context import ToolContext


# --- Tool: remember_display_name ---
# When ADK calls this function, it injects a ToolContext object for the `tool_context` parameter.
# The state dictionary (tool_context.state) persists for the entire conversation session.
def remember_display_name(display_name: str, tool_context: ToolContext) -> str:
  """Store the user's preferred display name for this session.

  Args:
      display_name: Name the user wants to be called.

  Returns:
      Confirmation message.
  """
  # Strip leading/trailing whitespace from the name before storing it.
  # tool_context.state is a dict that survives across multiple turns in the same session.
  tool_context.state["user_display_name"] = display_name.strip()

  # Return a friendly confirmation — the agent will relay this to the user.
  return f"Got it — I'll remember you as {display_name.strip()} for this session."


# --- Tool: recall_display_name ---
def recall_display_name(tool_context: ToolContext) -> str:
  """Recall the display name stored for this session, if any."""
  # Look up the name stored by remember_display_name.
  # dict.get() returns None (not an error) if the key hasn't been set yet.
  name = tool_context.state.get("user_display_name")

  # If no name is stored yet, tell the agent so it can ask the user.
  if not name:
    return "No display name is stored yet. Ask the user what to call them."

  # Return the stored name so the agent can use it in its response.
  return f"The user's display name is: {name}"


# --- Agent definition ---
root_agent = Agent(
    # name: Unique identifier for this agent.
    name="session_memory_workshop_agent",

    # model: Gemini model that decides when to call the memory tools.
    model="gemini-2.5-flash",

    # description: Short summary for orchestrators.
    description="Remembers a display name for the conversation using session state.",

    # instruction: Tells the model when to call each memory tool.
    instruction="""
You help users with a simple personal memory demo.
- When they give a name or ask you to remember what to call them, use remember_display_name.
- When they ask what you remember, use recall_display_name.
Keep replies short and friendly.
""",

    # tools: Both memory tools are registered so the model can call either one.
    tools=[remember_display_name, recall_display_name],
)
