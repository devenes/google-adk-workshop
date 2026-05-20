# code_execution_agent

**Level:** Advanced — **Python Code Execution Sandbox** (`BuiltInCodeExecutor`).

This demo shows how to equip an agent with the ability to write and run Python code to solve complex, multi-step mathematical, analytical, or string manipulation queries.

## Architecture

```text
            [User Question]
                 │
                 ▼
┌──────────────────────────────────────────┐
│          code_execution_agent            │
│         model: gemini-2.5-flash-lite     │
│                                          │
│  Uses: BuiltInCodeExecutor (Gemini-side) │
└──────────────────────────────────────────┘
        │                        ▲
        ▼ (writes python)        │ (returns stdout)
┌──────────────────────────────────────────┐
│      Gemini Native Python Sandbox        │
└──────────────────────────────────────────┘
                 │
                 ▼
      [Precise validated response]
```

## Concepts

1. **`code_executor`**: Configuring an agent with `BuiltInCodeExecutor()` passes the code-execution tool declaration to the Gemini API.
2. **Accurate Computation**: Large Language Models are notoriously prone to math and logic errors. Code execution solves this by delegating computational work to a real Python interpreter.

## Run and Try

Run the web interface:
```bash
cd demos && adk web .
```
And select `code_execution_agent`. Try asking:
* "Find the sum of all prime numbers between 1 and 100."
* "Create a frequency table of characters in the word 'antigravity'."
