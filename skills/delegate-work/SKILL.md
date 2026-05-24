---
name: delegate-work
description: Use this skill when you are about to do work that is long, noisy, or iterative — codebase search, reading more than two files to answer one question, running tests/builds/linters with verbose output, summarizing long files or logs, or any feedback loop (typecheck → fix → retry). Delegates the work to a subagent with a strict return contract so the supervisor's context stays clean.
---

# Delegate work to subagents

The supervisor's context is precious. Most work that *looks* like it needs the supervisor actually doesn't — it just needs a worker that returns a summary.

## Always delegate

Spawn a subagent (do not do it yourself) for:

- Codebase search, grep, or "where is X defined/used"
- Reading more than two files to answer one question
- Running tests, builds, linters, or any command whose output is >50 lines
- Summarizing logs, transcripts, or files >500 lines
- Iterative fix loops: typecheck → fix → re-run, failing-test → fix → re-run
- Verifying external facts (library API shapes, docs lookups)

Do it yourself only when the work requires cross-cutting judgment or synthesizes results from multiple completed subagent runs.

## Enforce a return contract

Subagents must not return free-form prose. Tell the subagent in its prompt to reply with this schema:

```
STATUS: ok | needs_input | failed
SUMMARY: <= 3 sentences
ARTIFACTS: <list of file paths the subagent wrote>
SHORTCUTS_TAKEN:
  - <file:line, what was bypassed, why>  (or "none")
NEXT: <suggested next step, or "none">
```

If the subagent's full output exceeds ~500 tokens, it writes to `.agent-scratch/<task>.md` and returns the path. The supervisor reads the file only if needed.

The `SHORTCUTS_TAKEN` field is the single most important line. Models will not volunteer that they used `any`, added `@ts-ignore`, deleted assertions, or skipped a check — but they will honestly fill in a structured field that asks. This is how you catch quality erosion without re-reading the diff yourself.

## Pattern: iterator subagent

For typecheck, lint, test-fix, dependency-upgrade — anything with a feedback loop:

> Subagent runs the check → reads the output → fixes → re-runs → repeats until clean or stuck. Supervisor only judges the final outcome, never sees iterations 1–N.

Prompt template:

```
Run `<command>` and fix all errors. Rules:
- Do not use `any`, @ts-ignore, @ts-expect-error, eslint-disable, or delete assertions
  to silence errors. If you must, declare it in SHORTCUTS_TAKEN with justification.
- Run the relevant tests after fixing. Report pass/fail.
- Return in this format: <paste return contract>
- If your diff is larger than ~50 lines, save it to .agent-scratch/<task>.diff and
  return the path.
```

## Pattern: scout then surgeon

For any non-trivial edit to unfamiliar code:

1. Scout subagent (Haiku) returns a structured map: file paths, key symbols, line ranges of interest, tests covering them. 2–3 sentence summary.
2. Supervisor reads only the precise ranges the scout flagged.
3. Supervisor (or another subagent) does the edit.

The supervisor never loads the exploration noise — only the coordinates.

## Pattern: verifier

After the supervisor makes a change, a Haiku subagent runs all checks (typecheck, lint, test, build) and returns a one-line verdict. Prevents the supervisor from carrying check output forward across turns.

## Failure modes

- **Doing search yourself "because it's faster."** It isn't, over a session — the file contents stay in your window.
- **Letting subagents return prose.** Without a contract, they will dump everything.
- **Carrying old test output forward** after the test now passes. Drop it.
- **Spawning a subagent for a one-line lookup.** Overhead doesn't pay back. Use it for work that's noisy *or* iterative *or* long.

## See also

- [[tier-model]] — pick the cheapest model that can do the subagent's work
- [[scout-codegraph]] — for structural questions, skip the scout subagent entirely
- [[scratch-context]] — where subagents drop oversized artifacts
