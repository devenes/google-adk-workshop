# 14-hitl_sensitive_action

**Level:** Advanced (human-in-the-loop / **instruction-enforced confirmation**).

**Goal:** The agent asks the user for explicit approval in the chat UI before calling a sensitive tool. No callbacks, no `App`, no `ResumabilityConfig` — just a clear instruction that forces a pause.

## How it works

1. User asks the agent to send an email.
2. Agent **stops and asks in the UI**: _"Are you sure you want to send this email to … ? Reply YES to confirm or NO to cancel."_
3. User replies **YES** → agent calls `send_email`.
4. User replies **NO** → agent cancels and confirms.

## Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│              hitl_email_agent  (root agent)                   │
│              model: gemini-2.5-flash-lite                     │
│                                                              │
│  instruction: "MUST ask user before calling send_email"       │
│                                                              │
│  ┌──────────────────────┐                                    │
│  │   send_email()        │                                    │  ← tool
│  │   (only after YES)    │                                    │
│  └──────────────────────┘                                    │
└──────────────────────────────────────────────────────────────┘
              │
              ▼  agent asks user in chat
   "Are you sure? Reply YES / NO"
              │
   YES → send_email()    NO → cancel
```

## Try it

```text
Send an email to alice@example.com with subject "Hello" and body "How are you?".
```

```text
Email bob@example.com: subject "Meeting tomorrow", body "Can we push to 3pm?".
```

**Checkpoint:** Agent asks for confirmation before sending; email only goes out after the user replies YES.

See [CHECKPOINTS.md](../CHECKPOINTS.md).
