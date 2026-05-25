---
name: tier-model
description: Use this skill when picking a model for a subagent or task — Haiku for mechanical work (search, test runners, log triage, scaffolds), Sonnet for judgment (debugging, architecture, multi-file changes), Opus only when Sonnet stalls. Apply at the start of any session, before spawning a subagent, or whenever a task's complexity is unclear.
---

# Pick the right model for the job

Most work in a session does not require the largest model. The supervisor often *is* Sonnet or Opus — fine, that's where judgment lives — but the subagents it spawns should usually be Haiku. Running every subagent on the supervisor's tier is the silent budget killer.

## Decision table

| Task | Model |
|---|---|
| File search, grep, path discovery | Haiku |
| Reading a file and summarizing it | Haiku |
| Running and interpreting tests/builds/linters | Haiku |
| Log triage, error extraction from CI | Haiku |
| Mechanical refactor with an explicit spec | Haiku |
| Single-file edits under a clear contract | Haiku |
| Scaffolds following an existing pattern | Haiku |
| Doc/API lookup and snippet extraction | Haiku |
| Verifier subagents (did the checks pass?) | Haiku |
| Debugging an unknown root cause | Sonnet |
| Architecture or design decisions | Sonnet |
| Multi-file changes requiring consistency | Sonnet |
| Code review with judgment (taste, trade-offs) | Sonnet |
| Performance investigation | Sonnet |
| Cross-system reasoning where Sonnet stalled twice | Opus |
| Novel algorithms or genuinely hard correctness work | Opus |

If unsure, **start with Haiku**. Escalate only if it returns `STATUS: needs_input` or visibly flounders.

## Why this matters for context, not just cost

Smaller models on focused tasks tend to return tighter outputs. A Haiku subagent told to "find where session expiry is enforced and return file:line" returns three lines. The same prompt to Opus often returns three lines *plus* unsolicited analysis and suggestions — which then enter the supervisor's window. Right-sizing the model is right-sizing the reply.

## Anti-patterns

- **Supervisor model = subagent model by default.** Override per-spawn.
- **Escalating preemptively** ("this might be hard, let's use Opus"). Run Haiku first; the failure mode is cheap.
- **Using Opus for exploration.** Exploration is structured lookup, not judgment. Haiku + a return contract beats Opus + freeform every time.

## See also

- [[delegate-work]] — most subagents spawned via this skill should be Haiku
- [CodeGraph](https://github.com/colbymchenry/codegraph) MCP — for structural code queries, graph lookups are model-free; cheaper than even Haiku
