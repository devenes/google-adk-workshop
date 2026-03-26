# calculator_basics

**Level:** Beginner (first tools after a plain chat agent).

**Goal:** Show that **docstrings + types** become tool metadata. No network calls; safe for classrooms.

**Try:** “What is (19.5 + 2) times 3?” (model should chain tools.)

**Upstream reference:** Tool patterns in [hello_world](https://github.com/google/adk-python/blob/main/contributing/samples/hello_world/agent.py).

**Eval:** `__init__.py` exists so `adk eval` can load this app like upstream samples. Sample set: [`eval/calculator_basics_smoke.evalset.json`](../../eval/calculator_basics_smoke.evalset.json) — see [`EVAL.md`](../../EVAL.md).
