# 02-calculator_basics

**Level:** Beginner (first tools after a plain chat agent).

**Goal:** Show that **docstrings + types** become tool metadata. No network calls; safe for classrooms.

## Architecture

```text
┌─────────────────────────────────────────────┐
│          calculator_basics_agent             │  ← root agent
│          model: gemini-flash-lite            │
│                                             │
│  ┌──────────────────┐  ┌──────────────────┐ │
│  │   add_numbers()  │  │ multiply_numbers()│ │  ← function tools
│  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────┘
```

## Try it

```text
What is (20.5 + 2)?
times 3?
```

```text
Divide 144 by 12, then subtract 5.
```

```text
If I start with 100 and multiply by 1.08 three times, what do I get?
```

**Upstream reference:** Tool patterns in [hello_world](https://github.com/google/adk-python/blob/main/contributing/samples/hello_world/agent.py).

**Eval:** `__init__.py` exists so `adk eval` can load this app like upstream samples. Sample set: [`eval/calculator_basics_smoke.evalset.json`](../../eval/calculator_basics_smoke.evalset.json) — see [`EVAL.md`](../../EVAL.md).
