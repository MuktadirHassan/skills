---
name: use-rtk
description: Use this skill when running shell commands that produce verbose output (git, npm/bun/pnpm, cargo, test runners, build tools, package managers). RTK is a Rust CLI proxy that trims tool output before it reaches the model, typically 60–90% savings on dev operations. A Claude Code hook rewrites commands transparently after install; you mostly just need to know it's there.
---

# Route verbose commands through RTK

[RTK (Rust Token Killer)](https://github.com/rtk-ai/rtk) is a local CLI proxy that filters noisy command output before Claude sees it. Things like `git status` showing every untracked file, `npm install` dumping its dep tree, `cargo build` printing every crate — RTK trims these to the useful signal.

It complements the other skills: even when a command *must* run in the supervisor's context, RTK keeps the output that lands there small.

## Install

RTK installs its own Claude Code hook — you don't need to wire anything by hand, and the `te` plugin deliberately does not duplicate this (RTK's installer is authoritative and will stay in sync with new RTK versions).

```bash
# Install RTK (see https://github.com/rtk-ai/rtk for the current install command)
cargo install rtk
rtk --version

# Install the PreToolUse hook + RTK.md globally
rtk init -g

# Restart Claude Code to pick up the hook
```

After `rtk init -g`, any Bash command Claude runs (`git status`, `npm install`, etc.) is transparently rewritten to `rtk <cmd>` and the trimmed output is what reaches the model.

## Meta commands (call directly, not via hook)

```bash
rtk gain                  # show token savings analytics
rtk gain --history        # per-command usage and savings
rtk discover              # analyze your Claude Code history for missed wins
rtk proxy <cmd>           # run a raw command bypassing filters (debugging)
```

## Usage in practice

Once `rtk init -g` is run, you don't change how you write commands. `git status` is automatically rewritten to `rtk git status` and the model sees the trimmed output. Zero per-call cognitive overhead.

Note: RTK's hook only runs on the `Bash` tool. Built-in tools like `Read`, `Grep`, and `Glob` don't pass through it, so they're not auto-rewritten — that's fine, those tools already return scoped output by design.

What this means for you as the agent:

- **Trust the trimmed output.** RTK trims noise (untracked-file lists, dep trees, progress bars), not signal. If you need the raw output for a specific reason, use `rtk proxy <cmd>`.
- **Periodically run `rtk gain`** at the end of long sessions if the user is curious where the savings came from.
- **Run `rtk discover`** when onboarding to a new project to surface commands worth proxying.

## Name collision warning

There is another tool named `rtk` (reachingforthejack/rtk, "Rust Type Kit"). If `rtk gain` fails with "unknown subcommand", you have the wrong binary. Check with `which rtk` and the install URL above.

## Where RTK fits with the other skills

| Layer | Mechanism |
|---|---|
| Don't run the command at all | [[scout-codegraph]] for structural questions |
| Run it, but in a subagent | [[delegate-work]] — supervisor only sees the summary |
| Run it in the supervisor, with trimmed output | **RTK** |

Use them in that order of preference. RTK is the floor, not the ceiling — it makes the unavoidable cheap, but the bigger wins are upstream.

## See also

- [[delegate-work]] — for commands that should run inside a subagent loop
- [[scratch-context]] — dump RTK's full output to `.agent-scratch/` if you ever need the unfiltered version
