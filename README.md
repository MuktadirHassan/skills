# skills(claude-token-efficiency) (`te` plugin)

Keep Claude Code's context window lean on long sessions and large codebases.

**The core idea:** the supervisor agent's context is RAM, not disk. Anything long, noisy, or iterative should happen outside the supervisor's window — in a subagent, in a scratch file, or trimmed before it lands.

## Skills

| Skill | What it does |
|---|---|
| [`token-efficient-agent`](skills/token-efficient-agent/SKILL.md) | Meta/orchestrator — activates all three patterns at task start |
| [`delegate-work`](skills/delegate-work/SKILL.md) | Spawn subagents for search, iteration loops, and verification. Enforces structured return contracts. |
| [`tier-model`](skills/tier-model/SKILL.md) | Decision table: Haiku for mechanical work, Sonnet for judgment, Opus only when Sonnet stalls |
| [`scratch-context`](skills/scratch-context/SKILL.md) | Externalize notes, decisions, and dead ends to `.agent-scratch/` so they survive across turns |

## Install

### Option A — Plugin (recommended)

Install the plugin so skills are available everywhere and the `SessionStart` hook auto-injects scratch notes:

```
/plugin marketplace add MuktadirHassan/skills
/plugin install te@skills
```

Skills are then available as `/te:token-efficient-agent`, `/te:delegate-work`, etc.

Then per project, run two setup commands:

```bash
# 1. Add operating rules so Claude applies the patterns automatically
curl -fsSL https://raw.githubusercontent.com/MuktadirHassan/skills/main/templates/CLAUDE.md -o CLAUDE.md

# 2. Enable scratch note injection
mkdir .agent-scratch && echo ".agent-scratch/" >> .gitignore
```

Without step 1, the skills exist but Claude won't apply them unless you invoke them manually.

### Option B — Standalone skills (no hooks)

Copy the skills into your global `~/.claude/skills/`:

```bash
git clone https://github.com/MuktadirHassan/skills /tmp/te
cp -r /tmp/te/skills/* ~/.claude/skills/
```

Restart Claude Code. Skills show up in `/help` as `/token-efficient-agent`, `/delegate-work`, etc.

Then add operating rules to any project you want them active in:

```bash
curl -fsSL https://raw.githubusercontent.com/MuktadirHassan/skills/main/templates/CLAUDE.md -o CLAUDE.md
```

Note: with Option B, the `scratch-context` skill works but you have to read `.agent-scratch/` manually — there's no auto-injection hook.

## Templates

| File | Purpose |
|---|---|
| [`templates/CLAUDE.md`](templates/CLAUDE.md) | Drop-in operating rules (~5 lines). Copy to your project or `~/.claude/CLAUDE.md` |
| [`templates/SYSTEM_PROMPT.md`](templates/SYSTEM_PROMPT.md) | Extended rules: model tiering table, failure modes. Paste the sections you want. |
| [`templates/return-contract.md`](templates/return-contract.md) | Copy-paste subagent reply schemas (default, iterator, scout) |

## Recommended companions

- **[CodeGraph](https://github.com/colbymchenry/codegraph)** — pre-indexed knowledge graph for structural code queries ("who calls X", "what does Y affect"). One MCP call instead of 30 greps. Ships its own Claude Code integration.
- **[RTK](https://github.com/rtk-ai/rtk)** — trims verbose Bash output (60–90% savings on `git`, `npm`, etc.) before the model sees it. Ships its own hook.

## Repo layout

```
.claude-plugin/plugin.json        plugin manifest (name: te)
hooks/
  hooks.json                      SessionStart registration
  load-scratch.py                 injects .agent-scratch/ contents on session start
skills/
  token-efficient-agent/SKILL.md  meta/orchestrator
  delegate-work/SKILL.md          subagent patterns and return contract
  tier-model/SKILL.md             model selection decision table
  scratch-context/SKILL.md        externalize state to .agent-scratch/
templates/
  CLAUDE.md                       drop-in operating rules
  SYSTEM_PROMPT.md                extended rules
  return-contract.md              subagent reply schemas
```

## License

MIT. See [LICENSE](LICENSE).
