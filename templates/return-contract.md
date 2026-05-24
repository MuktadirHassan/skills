# Subagent return contract

Paste this into any subagent prompt as the required reply format.

```
STATUS: ok | needs_input | failed
SUMMARY: <= 3 sentences. What you did and the outcome. No narration.
ARTIFACTS:
  - <path to any file you wrote or modified>
SHORTCUTS_TAKEN:
  - <file:line>, <what was bypassed>, <why it was necessary>
  (or the single word "none")
NEXT: <one suggested next step, or "none">
```

## Rules for the subagent (include verbatim)

- Do not return prose outside this schema.
- If your full output exceeds ~500 tokens, write the long form to `.agent-scratch/<task-id>.md` and put the path in `ARTIFACTS`. Keep `SUMMARY` to 3 sentences regardless.
- `SHORTCUTS_TAKEN` is mandatory and must be honest. Examples that count as shortcuts:
  - `any`, `unknown as T`, `@ts-ignore`, `@ts-expect-error`
  - `eslint-disable`, `// noqa`, `# type: ignore`
  - Skipping or weakening an assertion to make a test pass
  - Catching and swallowing an error
  - Mocking something that should have been wired up
  - Deleting code instead of fixing it
- If `STATUS: failed`, put the blocker in `SUMMARY` and what you tried in the scratch file.
- If `STATUS: needs_input`, ask exactly one question in `SUMMARY`.

## Variants

**Iterator (typecheck/test fix loop):**

```
STATUS: ok | needs_input | failed
ERRORS_BEFORE: <n>
ERRORS_AFTER: <n>
SUMMARY: <= 3 sentences
ARTIFACTS:
  - .agent-scratch/<task>.diff
SHORTCUTS_TAKEN: ...
TESTS_RUN: yes | no — <pass/fail counts>
NEXT: ...
```

**Scout (codebase exploration):**

```
STATUS: ok | failed
SUMMARY: <= 3 sentences on what the area does
COORDINATES:
  - <file:line-range> — <one-line purpose>
  - ...
TESTS:
  - <test file:line> — <what it covers>
NEXT: ...
```

**Verifier (post-edit checks):**

```
STATUS: ok | failed
TYPECHECK: pass | fail (<n> errors)
LINT: pass | fail (<n> issues)
TESTS: pass | fail (<n>/<m>)
BUILD: pass | fail
SUMMARY: <= 2 sentences. If any failed, the first error only.
```
