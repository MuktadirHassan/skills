# Subagent return contract

Every subagent call must specify a return format. Paste this schema into the subagent prompt.

## Default schema

```
STATUS: ok | needs_input | failed
SUMMARY: <= 3 sentences
ARTIFACTS: <list of file paths the subagent wrote, or "none">
SHORTCUTS_TAKEN:
  - <file:line, what was bypassed, why>  (or "none")
NEXT: <suggested next step, or "none">
```

`SHORTCUTS_TAKEN` is the most important field. Models will not volunteer that they used `any`, added `@ts-ignore`, deleted assertions, or skipped checks — but they will honestly fill in a structured field that asks. Never omit it.

If the subagent has more than ~500 tokens of content to return, it writes to `.agent-scratch/<task-id>.md` and returns the path. The supervisor reads the file only if needed.

## Variant: iterator subagent (fix loop)

Use when the subagent must run a command, fix errors, and re-run until clean:

```
Run `<command>` and fix all errors. Rules:
- Do not use `any`, @ts-ignore, @ts-expect-error, eslint-disable, or delete
  assertions to silence errors. Declare any exception in SHORTCUTS_TAKEN.
- Run the relevant tests after fixing. Report pass/fail.
- Return in this format:
    STATUS: ok | needs_input | failed
    SUMMARY: <= 3 sentences
    SHORTCUTS_TAKEN: <file:line, what, why>  (or "none")
    NEXT: <suggested next step, or "none">
- If your diff is larger than ~50 lines, save it to .agent-scratch/<task>.diff
  and return the path.
```

## Variant: scout subagent (read-only)

Use before editing unfamiliar code:

```
Return only:
- File purpose (1 sentence)
- Key exports and their signatures relevant to <planned change>
- Line ranges of interest
- Tests covering those lines
- 2–3 sentence summary of what the supervisor needs to know before editing

Do not make any changes. Do not return full file contents.
```
