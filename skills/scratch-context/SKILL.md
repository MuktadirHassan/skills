---
name: scratch-context
description: Use this skill on any non-trivial task to externalize running notes, decisions, and ruled-out hypotheses to .agent-scratch/ instead of carrying them in the conversation. Invoke at task start (read prior notes), during work (append findings), and at task end (record decisions). Also use to detect when /compact or a session restart is warranted.
---

# Externalize state to .agent-scratch/

The supervisor's context window degrades over long sessions: re-reading the same files, re-investigating dead ends, losing the why behind earlier decisions. The fix is boringly mechanical — write things to disk and re-read them, instead of expecting the window to remember.

## The directory

```
.agent-scratch/
├── notes.md         # running notes for the current task (append-only)
├── decisions.md     # one line per decision with rationale
├── dead-ends.md     # hypotheses ruled out, with why
└── <task-id>.md     # oversized subagent outputs (see delegate-work)
```

Add `.agent-scratch/` to `.gitignore` unless you want it shared.

## When to read

- **At the start of any non-trivial task**, before reading code: check `notes.md`, `decisions.md`, `dead-ends.md` if they exist. Two minutes here saves re-deriving context that was already paid for in a previous session.
- **Before investigating a hypothesis**, check `dead-ends.md`. If it's listed, don't re-run the investigation.

> **If you installed this repo as the `te` plugin**, a `SessionStart` hook auto-injects the tail of `notes.md`, `decisions.md`, and `dead-ends.md` into context every time a session starts in a project that has a `.agent-scratch/` directory. You'll see the scratch content appear without having to remember to read it. Standalone-skill users get the discipline but have to read manually.

## When to write

- **Append to `notes.md`** when you learn something non-obvious about the current task — a constraint, a surprising behavior, a file that turned out to matter.
- **Append to `decisions.md`** when you make a choice that isn't obvious from the diff — "chose approach A over B because X". One line. Future-you will thank you.
- **Append to `dead-ends.md`** the moment you rule out a hypothesis. "Not a race condition — verified by Y." This is the single most under-used habit and the biggest defense against re-investigating the same wrong answer twice.

If you've re-read the same file twice in one task, that's the signal: write the relevant facts to `notes.md` and refer to that file instead.

## Format

Boring is fine. Append-only, dated, terse:

```markdown
## 2026-05-24

- Session expiry is enforced in middleware/auth.ts:88, NOT in the Session model.
- The migration in 0042_user_schema.sql is the one legal flagged. Don't touch
  without compliance sign-off.
- Ruled out: connection pool exhaustion. pool stats show 4/20 in use during repro.
```

## Compact and restart triggers

Tell the user it's time for `/compact` or a fresh session when:

- A task completes and the user starts an unrelated new task.
- You catch yourself re-reading the same file across turns despite having scratch notes.
- The conversation has gone through multiple subagent batches and the supervisor is referencing things from "earlier" that it can no longer fully see.

Suggest it explicitly — models don't volunteer this often enough.

## Anti-patterns

- **Treating `notes.md` like a journal.** It's a working memory aid. Terse bullets, not narration.
- **Writing notes nobody (including future-you) will read.** If it's obvious from the code or the diff, skip it. Write the *why* and the *gotchas*, not the *what*.
- **Forgetting to record dead ends.** The whole point is avoiding repeat investigations.

## See also

- [[delegate-work]] — subagents write oversized outputs to `.agent-scratch/<task>.md`
- [[scout-codegraph]] — for *structural* facts about the codebase, query the graph; scratch is for *task-specific* learnings
