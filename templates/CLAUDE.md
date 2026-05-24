# Agent operating rules

Context is RAM, not disk. Delegate aggressively.

- Spawn a subagent for: search, grep, reading >2 files, test/build runs, fix loops, log triage
- Do it yourself only when the work requires cross-cutting judgment or synthesizes subagent results
- Default model: Haiku. Escalate to Sonnet for judgment/trade-offs. Opus only after Sonnet stalls twice
- Before any non-trivial task, check `.agent-scratch/notes.md` and `decisions.md` if they exist
- After finishing, append what you learned to `.agent-scratch/notes.md`
