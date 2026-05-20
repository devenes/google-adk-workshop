# few_shot_translator

**Level:** Beginner/Intermediate — **Few-Shot Example Prompting**.

This demo showcases how to guide an LLM to follow a highly custom output structure and style by including inline examples in the system instructions (known as few-shot prompting).

## Setup and Concepts

By showing the model exact patterns of input-to-output mapping, we instruct it how to:
1. Identify tone and label it consistently.
2. Structure output cleanly inside brackets (`[TONE: ...]`, `[FR: ...]`, `[DE: ...]`) without conversational filler.

This is a lightweight alternative to schema validation for text formatting tasks.

## Run and Try

Run the web interface:
```bash
cd demos && adk web .
```
And select `few_shot_translator`.
