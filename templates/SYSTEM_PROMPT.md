# Extended agent rules (paste what you want into your CLAUDE.md)

Pick the sections relevant to your workflow. None are required — `templates/CLAUDE.md` covers the essentials.

---

## Model tiering

| Task type | Model |
|---|---|
| File search, grep, path discovery | Haiku |
| Running and interpreting tests/builds/linters | Haiku |
| Log triage, error extraction | Haiku |
| Mechanical refactor with explicit spec | Haiku |
| Single-file edits under a clear contract | Haiku |
| Scaffolds following existing patterns | Haiku |
| Verifier subagents | Haiku |
| Architecture, design, multi-file changes | Sonnet |
| Debugging unknown root cause | Sonnet |
| Anything requiring taste or trade-offs | Sonnet |
| Cross-system reasoning where Sonnet stalled twice | Opus |

---

## Subagent return contract

Every subagent call must specify a return format. Default schema:

```
STATUS: ok | needs_input | failed
SUMMARY: <= 3 sentences
ARTIFACTS: <list of file paths the subagent wrote>
SHORTCUTS_TAKEN:
  - <file:line, what was bypassed, why>  (or "none")
NEXT: <suggested next step, or "none">
```

If the subagent has more than ~500 tokens of content, it writes to `.agent-scratch/<task-id>.md` and returns the path. Do not pull the content into supervisor context unless you actually need it.

The `SHORTCUTS_TAKEN` field is mandatory. Models will not volunteer that they used `any`, added `@ts-ignore`, deleted assertions, or skipped checks — but they will honestly fill in a structured field that asks.

---

## Pre-flight for edits

Before editing any file you have not read this session:

1. Spawn a Haiku scout subagent to return: file purpose, key exports, lines relevant to the planned change, tests covering it.
2. Approve or revise the plan based on its summary.
3. Then do the edit yourself (or delegate if mechanical).

---

## Context hygiene

- If you've re-read the same file twice in one task, write the relevant facts to `.agent-scratch/notes.md` and refer to that instead.
- When a task completes and the user starts a new one, suggest `/compact` or a fresh session before continuing.
- Never paste full file contents into your own reasoning if a line range or summary would do.

---

## Failure modes to avoid

- Doing search yourself "because it's faster" — it isn't, over a session.
- Letting subagents return free-form prose.
- Carrying old test output forward after the test now passes.
- Re-exploring code you've already mapped — check `.agent-scratch/` first.
- Escalating to Opus preemptively. Haiku first; fail cheaply.
