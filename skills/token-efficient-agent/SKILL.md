---
name: token-efficient-agent
description: Use this skill at the start of any non-trivial coding task, long debugging session, multi-file refactor, test/build loop, codebase search, or when context may grow large. Applies delegation, model tiering, scratch notes, and compact/restart hygiene in one pass.
---

# Token-efficient agent: apply all patterns

This is the orchestrator skill. It does not add new rules — it activates the three underlying skills together so you don't have to remember to invoke them separately.

## Apply on every non-trivial task

At task start:
1. **[[scratch-context]]** — check `.agent-scratch/notes.md`, `decisions.md`, `dead-ends.md` before reading any code.
2. **[[tier-model]]** — decide up front which model handles each piece of work. Default: Haiku for lookup/iteration, Sonnet for judgment, Opus only after Sonnet stalls twice.
3. **[[delegate-work]]** — spawn subagents for search, grep, file reads >2, test/build runs, and fix loops. Enforce the return contract on every spawn.

During work:
- Append non-obvious findings to `.agent-scratch/notes.md` as you go.
- Record every ruled-out hypothesis in `.agent-scratch/dead-ends.md` immediately.

At task end:
- Write one-line decisions with rationale to `.agent-scratch/decisions.md`.
- If the user starts an unrelated new task, suggest `/compact` or a fresh session.

## When to invoke this skill

- Any task that will touch more than two files
- Any debugging session where the root cause is unknown
- Any test/build/lint fix loop
- Any codebase search or "find where X is defined/used" question
- Any session you expect to run longer than ~10 turns

## When NOT to invoke

- One-liner edits to a file already in context
- Direct questions answerable from the current conversation
- Tasks where context growth is clearly not a risk

## See also

- [[delegate-work]] — subagent patterns and return contract
- [[tier-model]] — model selection decision table
- [[scratch-context]] — externalize state to `.agent-scratch/`
