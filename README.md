# claude-token-efficiency (`te` plugin)

Opinionated skills, hooks, and MCP wiring for keeping Claude Code's context window lean on long sessions and large codebases. Public, MIT-licensed, drop-in.

The throughline: **the supervisor agent's context is RAM, not disk.** Anything that's long, noisy, iterative, or lookup-shaped should happen *outside* the supervisor's window — in a subagent, in a pre-built index, in a scratch file, or in a proxy that trims output before it ever lands.

## What's in here

| Component | Type | What it does |
|---|---|---|
| [`delegate-work`](skills/delegate-work/SKILL.md) | Skill | Spawn subagents for search, verification, and iteration loops. Enforces structured return contracts so the supervisor sees a summary, not the noise. |
| [`tier-model`](skills/tier-model/SKILL.md) | Skill | Decision table for Haiku vs Sonnet vs Opus. Default Haiku, escalate on judgment. |
| [`scout-codegraph`](skills/scout-codegraph/SKILL.md) | Skill + auto-wired MCP | Use the [CodeGraph](https://github.com/colbymchenry/codegraph) MCP server to answer "who calls X / what does Y affect" with one query instead of 30 greps. |
| [`scratch-context`](skills/scratch-context/SKILL.md) | Skill + `SessionStart` hook | Externalize running notes, decisions, and ruled-out hypotheses to `.agent-scratch/`. The hook auto-injects them at session start. |
| [`use-rtk`](skills/use-rtk/SKILL.md) | Skill (RTK installs its own hook) | Route shell commands through [RTK](https://github.com/rtk-ai/rtk), a proxy that trims verbose tool output before it reaches the model (60–90% savings on dev commands). RTK's own `rtk init -g` installs the PreToolUse hook — this plugin does not duplicate it. |

Plus [`templates/CLAUDE.md`](templates/CLAUDE.md) (drop-in operating rules) and [`templates/return-contract.md`](templates/return-contract.md) (subagent reply schemas).

## Install — pick a tier

Three install paths. Pick based on commitment, not ambition. **Start at Tier 1** even if you plan to land on Tier 3 — it takes 5 minutes and tells you whether the patterns fit your workflow before you commit to hooks and MCP.

### Tier 1 — Try the patterns (5 min, zero install)

Copy the CLAUDE.md template into one project:

```bash
curl -fsSL https://raw.githubusercontent.com/MuktadirHassan/claude-token-efficiency/main/templates/CLAUDE.md -o CLAUDE.md
```

That's it. No skills, no hooks. The system prompt now contains the delegation rules, model tiering, return contracts, and context-hygiene guidance. Use it on one project, see if it changes how Claude works for you.

### Tier 2 — Install the skills standalone (10 min)

Drop the skills into your global `~/.claude/skills/` so they're invokable everywhere with short names:

```bash
git clone https://github.com/MuktadirHassan/claude-token-efficiency /tmp/te
cp -r /tmp/te/skills/* ~/.claude/skills/
```

Restart Claude Code. Run `/help` and you should see `/delegate-work`, `/tier-model`, `/scout-codegraph`, `/scratch-context`, `/use-rtk`.

This is skills-only — no hooks, no MCP auto-wiring. Two of the skills (RTK and CodeGraph) require additional manual setup to deliver their full value; see their individual SKILL.md files. The `scratch-context` skill works but you have to remember to read your notes manually.

### Tier 3 — Install as the `te` plugin (30 min, full stack)

This is the recommended path for serious use. Skills + hooks + MCP wiring, one install.

**Prerequisites** (one-time, per machine — none are strictly required; the plugin degrades gracefully without them):

```bash
# RTK — for transparent Bash output trimming. RTK installs its OWN hook;
# the `te` plugin does not wire RTK itself.
cargo install rtk           # see https://github.com/rtk-ai/rtk for current method
rtk init -g                 # installs the PreToolUse hook globally

# CodeGraph — for structural code queries via MCP
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
# or: npm i -g @colbymchenry/codegraph
```

The `te` plugin requires `python3` on PATH for its `SessionStart` hook (`load-scratch.py`). Python 3 ships by default on macOS and most Linux distros; install separately on Windows if needed.

**Install the plugin:**

```
/plugin install MuktadirHassan/claude-token-efficiency
```

(Or, for local development: `claude --plugin-dir /path/to/this/repo`.)

**Per-project (CodeGraph index, one time per project):**

```bash
codegraph init -i
echo ".codegraph/" >> .gitignore
echo ".agent-scratch/" >> .gitignore
```

Skills are now namespaced: `/te:delegate-work`, `/te:tier-model`, etc. The plugin's `SessionStart` hook injects `.agent-scratch/` notes automatically. CodeGraph MCP is auto-registered; check with `/mcp`. RTK's command rewriting comes from RTK's own hook (`rtk init -g`), not from this plugin.

## Per-project vs global

- **`templates/CLAUDE.md`** → per project. Different codebases want different defaults (a TS monorepo isn't a Python script).
- **Plugin / standalone skills** → global. You want them everywhere.
- **`.agent-scratch/`** → per project, in `.gitignore`.
- **`.codegraph/`** → per project, in `.gitignore`.

## Mental model

Four mechanisms for keeping context lean. They compose; the plugin gives you all of them.

1. **Isolation** — subagents have their own context. Whatever they read, grep, or iterate on never enters the supervisor's window. Return contracts enforce that they reply with a summary, not a transcript. (`delegate-work`)
2. **Right-sizing** — Haiku for mechanical work, Sonnet for judgment, Opus only when you need it. Most exploration and verification is Haiku-shaped. (`tier-model`)
3. **Pre-computation** — structural questions about the codebase ("who calls X") should be answered by a pre-built index, not by re-deriving them every session. (`scout-codegraph`)
4. **Externalization** — notes, decisions, and dead ends belong on disk, not in the conversation. (`scratch-context`)

RTK sits underneath all of these: even when a command does run in the supervisor, RTK trims the output before the model sees it. (`use-rtk`)

## When this matters

Wins compound over session length and codebase size. Short single-file tasks won't show much. Long sessions on real codebases — debugging across services, multi-file refactors, dependency upgrades — are where the supervisor's context normally fills up with exploration noise, and where these skills pay back hard.

Two things to measure if you want to know it's working: tokens-per-completed-task, and how often you hit `/compact`. Both should drop noticeably. RTK also has `rtk gain` to report savings directly.

## Repo layout

```
.claude-plugin/plugin.json   plugin manifest (name: te)
.mcp.json                    auto-wires CodeGraph MCP server
hooks/
  hooks.json                 SessionStart registration
  load-scratch.py            injects .agent-scratch contents on session start
skills/                      the five skills (work standalone or as plugin)
templates/
  CLAUDE.md                  drop-in operating rules
  return-contract.md         subagent reply schemas
```

The skills directory follows the same shape Claude Code expects in `~/.claude/skills/`, so the same files work as a standalone install and as part of the plugin — no duplication.

## License

MIT. See [LICENSE](LICENSE).
