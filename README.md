# skills(claude-token-efficiency) (`te` plugin)

Opinionated skills, hooks, and MCP wiring for keeping Claude Code's context window lean on long sessions and large codebases. Public, MIT-licensed, drop-in.

The throughline: **the supervisor agent's context is RAM, not disk.** Anything that's long, noisy, iterative, or lookup-shaped should happen *outside* the supervisor's window — in a subagent, in a pre-built index, in a scratch file, or in a proxy that trims output before it ever lands.

## What's in here

| Component | Type | What it does |
|---|---|---|
| [`delegate-work`](skills/delegate-work/SKILL.md) | Skill | Spawn subagents for search, verification, and iteration loops. Enforces structured return contracts so the supervisor sees a summary, not the noise. |
| [`tier-model`](skills/tier-model/SKILL.md) | Skill | Decision table for Haiku vs Sonnet vs Opus. Default Haiku, escalate on judgment. |
| [`scratch-context`](skills/scratch-context/SKILL.md) | Skill + `SessionStart` hook | Externalize running notes, decisions, and ruled-out hypotheses to `.agent-scratch/`. The hook auto-injects them at session start. |

Plus [`templates/CLAUDE.md`](templates/CLAUDE.md) (drop-in operating rules) and [`templates/return-contract.md`](templates/return-contract.md) (subagent reply schemas).

### Recommended companion: [CodeGraph](https://github.com/colbymchenry/codegraph)

CodeGraph is a separate MCP server that pre-indexes your codebase as a SQLite knowledge graph. Structural questions ("who calls X", "what does Y affect") become one tool call instead of 30 greps. It ships its own Claude Code integration — the installer registers the MCP server and writes its usage instructions into `~/.claude/CLAUDE.md` globally, so there's nothing for this plugin to add. Install with `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh`, then run `codegraph init -i` per project.

### Recommended companion: [RTK](https://github.com/rtk-ai/rtk)

RTK is a separate tool that trims verbose Bash output (60–90% savings on `git`, `npm`, `cargo`, etc.) before the model sees it. Install it with `cargo install rtk && rtk init -g` and it ships its own Claude Code hook and its own `RTK.md` skill — there's nothing for this plugin to add. It pairs perfectly with the patterns here: our skills shrink *what enters the supervisor's window*, RTK shrinks *what the Bash tool returns*.

## Install — pick a tier

Three install paths. Pick based on commitment, not ambition. **Start at Tier 1** even if you plan to land on Tier 3 — it takes 5 minutes and tells you whether the patterns fit your workflow before you commit to hooks and MCP.

### Tier 1 — Try the patterns (5 min, zero install)

Copy the CLAUDE.md template into one project:

```bash
curl -fsSL https://raw.githubusercontent.com/MuktadirHassan/skills/main/templates/CLAUDE.md -o CLAUDE.md
```

That's it. No skills, no hooks. The system prompt now contains the delegation rules, model tiering, return contracts, and context-hygiene guidance. Use it on one project, see if it changes how Claude works for you.

### Tier 2 — Install the skills standalone (5 min)

Drop the skills into your global `~/.claude/skills/` so they're invokable everywhere with short names:

```bash
git clone https://github.com/MuktadirHassan/skills /tmp/te
cp -r /tmp/te/skills/* ~/.claude/skills/
```

Restart Claude Code. Run `/help` and you should see `/delegate-work`, `/tier-model`, `/scratch-context`.

This is skills-only — no hooks. The `scratch-context` skill works but you have to remember to read your notes manually. For structural code queries, install CodeGraph separately (see companion section above); for shell-output trimming, install RTK separately (`cargo install rtk && rtk init -g`).

### Tier 3 — Install as the `te` plugin (10 min, full stack)

This is the recommended path for serious use. Skills + hooks, one install.

**Prerequisites** (one-time, per machine):

```bash
# python3 — required for the SessionStart hook. Ships by default on
# macOS and most Linux distros; install separately on Windows if needed.
```

**Recommended companions (separate installs, each ships its own Claude Code integration):**

```bash
# CodeGraph — pre-indexed knowledge graph for structural code queries.
# Installer auto-registers the MCP server and writes usage instructions
# into ~/.claude/CLAUDE.md globally.
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

```bash
# RTK — transparent Bash output trimming. Independent of this plugin.
cargo install rtk           # see https://github.com/rtk-ai/rtk for current method
rtk init -g                 # installs the PreToolUse hook globally
```

**Install the plugin:**

```
/plugin install MuktadirHassan/skills
```

(Or, for local development: `claude --plugin-dir /path/to/this/repo`.)

**Per-project setup:**

```bash
echo ".agent-scratch/" >> .gitignore
# If you installed CodeGraph: also run `codegraph init -i` and add `.codegraph/` to .gitignore
```

Skills are now namespaced: `/te:delegate-work`, `/te:tier-model`, etc. The plugin's `SessionStart` hook injects `.agent-scratch/` notes automatically.

## Per-project vs global

- **`templates/CLAUDE.md`** → per project. Different codebases want different defaults (a TS monorepo isn't a Python script).
- **Plugin / standalone skills** → global. You want them everywhere.
- **`.agent-scratch/`** → per project, in `.gitignore`.

## Mental model

Four mechanisms for keeping context lean. This plugin covers three directly; the fourth (pre-computation) is provided by [CodeGraph](https://github.com/colbymchenry/codegraph) as a recommended separate install.

1. **Isolation** — subagents have their own context. Whatever they read, grep, or iterate on never enters the supervisor's window. Return contracts enforce that they reply with a summary, not a transcript. (`delegate-work`)
2. **Right-sizing** — Haiku for mechanical work, Sonnet for judgment, Opus only when you need it. Most exploration and verification is Haiku-shaped. (`tier-model`)
3. **Externalization** — notes, decisions, and dead ends belong on disk, not in the conversation. (`scratch-context`)
4. **Pre-computation** — structural questions about the codebase ("who calls X") should be answered by a pre-built index. Use [CodeGraph](https://github.com/colbymchenry/codegraph) — it ships its own MCP server and global instructions, no skill needed here.

[RTK](https://github.com/rtk-ai/rtk) sits underneath all of these as another optional companion: even when a command does run in the supervisor, RTK trims the output before the model sees it. Install separately; not part of this plugin.

## When this matters

Wins compound over session length and codebase size. Short single-file tasks won't show much. Long sessions on real codebases — debugging across services, multi-file refactors, dependency upgrades — are where the supervisor's context normally fills up with exploration noise, and where these skills pay back hard.

Two things to measure if you want to know it's working: tokens-per-completed-task, and how often you hit `/compact`. Both should drop noticeably. If you also installed RTK, `rtk gain` reports Bash-output savings directly.

## Repo layout

```
.claude-plugin/plugin.json   plugin manifest (name: te)
hooks/
  hooks.json                 SessionStart registration
  load-scratch.py            injects .agent-scratch contents on session start
skills/                      the three skills (work standalone or as plugin)
templates/
  CLAUDE.md                  drop-in operating rules
  return-contract.md         subagent reply schemas
```

The skills directory follows the same shape Claude Code expects in `~/.claude/skills/`, so the same files work as a standalone install and as part of the plugin — no duplication.

## License

MIT. See [LICENSE](LICENSE).
