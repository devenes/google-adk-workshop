"""Beginner/Intermediate demo: few-shot example prompting to enforce custom output format.

KEY CONCEPT — When to use few-shot examples vs. output_schema?

  Use output_schema (Pydantic) when:
    - You need machine-readable JSON that code will parse.
    - Field types and names must be rigidly enforced.
    - Downstream systems depend on exact schema contract.

  Use few-shot examples (this demo) when:
    - The format is human-readable text with custom structure.
    - You need inline tags, brackets, or markdown that Pydantic cannot model.
    - You want to guide tone/style in addition to structure.

HOW FEW-SHOT PROMPTING WORKS:
  The system instruction contains 3 explicit input→output examples.
  Gemini learns the pattern and replicates it for new inputs — no fine-tuning needed.
  Adding more examples (5-10) generally increases format adherence.
"""

from google.adk import Agent


# --- System Instruction with Few-Shot Examples ---
# The examples teach the model three things simultaneously:
#   1. FORMAT  — always emit [TONE:], [FR:], [DE:] bracket tags.
#   2. CONTENT — translate accurately into French and German.
#   3. STYLE   — identify emotional tone concisely and consistently.
#
# Note: using a module-level constant makes it easy to add examples or
# swap languages without touching the Agent definition.
_FEW_SHOT_INSTRUCTION = """\
You are a multilingual translation assistant that also identifies emotional tone.
Given a user message, produce EXACTLY this output format and nothing else:

[TONE: <one or two words describing the sentiment, e.g. Enthusiastic/Friendly>]
[FR: <French translation>]
[DE: <German translation>]

Do not add greetings, explanations, or any extra text outside the three bracket lines.

--- Examples ---

User: "I am really happy to meet you today!"
[TONE: Enthusiastic/Friendly]
[FR: Je suis vraiment ravi de vous rencontrer aujourd'hui !]
[DE: Ich freue mich sehr, Sie heute kennenzulernen!]

User: "This service is unacceptable. I want a refund."
[TONE: Angry/Dissatisfied]
[FR: Ce service est inacceptable. Je souhaite un remboursement.]
[DE: Dieser Service ist inakzeptabel. Ich möchte eine Rückerstattung.]

User: "Could you please tell me where the station is?"
[TONE: Polite/Inquiring]
[FR: Pourriez-vous me dire où se trouve la gare, s'il vous plaît ?]
[DE: Könnten Sie mir bitte sagen, wo der Bahnhof ist?]
"""


# --- Agent definition ---
root_agent = Agent(
    name="few_shot_translator",
    model="gemini-2.5-flash-lite",
    description=(
        "Translates input text into French and German, and tags the emotional tone, "
        "using few-shot examples to enforce a strict bracket output format."
    ),

    # instruction: The system prompt that includes the few-shot examples.
    # ADK passes this as the system instruction on every turn.
    instruction=_FEW_SHOT_INSTRUCTION,

    # No tools= needed — Gemini handles translation natively.
    # No output_schema — the format is text-based, not JSON.
)
