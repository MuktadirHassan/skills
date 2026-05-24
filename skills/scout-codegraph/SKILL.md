---
name: scout-codegraph
description: Use this skill when you need to answer structural questions about the codebase — "who calls X", "what does this affect", "where is Y defined", "what are the callees of Z". Prefer CodeGraph MCP queries over grep/find/read loops; one query replaces 30+ tool calls. Falls back to a scout subagent only when the graph returns nothing.
---

# Scout with CodeGraph before greppping

[CodeGraph](https://github.com/colbymchenry/codegraph) is an MCP server that pre-indexes your codebase into a SQLite-backed knowledge graph using tree-sitter. Structural questions become single tool calls instead of grep-and-read loops.

This is the cheapest possible scout: no model tokens, no file reads, just a query.

## Install

Two steps. First, install the `codegraph` binary globally (one time, per machine):

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# Windows
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex

# Or via npm (any OS)
npm i -g @colbymchenry/codegraph
```

Second, build the index inside each project where you want to use it (one time, per project):

```bash
codegraph init -i
```

This creates `.codegraph/` (add it to `.gitignore`). A file watcher keeps the index fresh on save; run `codegraph sync` after branch switches or programmatic file regeneration.

> **If you installed this repo as the `te` plugin**, the MCP server is auto-wired via `.mcp.json` — you just need the two steps above. Standalone-skill users must also add the `mcpServers.codegraph` block to their Claude Code settings manually (see the [CodeGraph README](https://github.com/colbymchenry/codegraph) for the exact JSON).

## Use it for

- **"Where is this symbol defined?"** → `codegraph_search`
- **"What's the structure around this file?"** → `codegraph_context`
- **"Who calls this function?"** → `codegraph_callers`
- **"What does this function call?"** → `codegraph_callees`
- **"If I change this signature, what breaks?"** → `codegraph_impact`
- **"Trace this call path"** → `codegraph_trace`
- **"Give me details on this node"** → `codegraph_node`
- **"List files in the graph"** → `codegraph_files`
- **"Is the index ready?"** → `codegraph_status`
- **"Explore freely from a starting point"** → `codegraph_explore`

## Decision flow

```
Structural question about existing code?
├── YES → CodeGraph query (Tier 1)
│         ├── Got an answer? → use it
│         └── Empty/insufficient? → spawn scout subagent (Tier 2)
└── NO  → it's a judgment question; don't scout, think
```

Replace the "scout subagent" step in [[delegate-work]] with this skill whenever the question is structural. Only fall back to a Haiku scout subagent when CodeGraph returns nothing useful.

## Worked example: safe signature change

1. `codegraph_callers UserRepository.findById` → list of 14 call sites with file:line.
2. `codegraph_impact UserRepository.findById` → blast radius including transitive callers and tests.
3. *Now* read only the call sites that the impact query flagged as non-trivial.
4. Spawn an iterator subagent ([[delegate-work]]) to update them and re-run typecheck.

Without CodeGraph: grep → 40 hits → read each → realize half are unrelated → repeat. Easily 30+ tool calls of noise in the supervisor's window.

## Limits — know before you trust the graph

- **Tree-sitter only sees what it can parse.** Dynamic dispatch, runtime DI, monkey-patching, codegen, string-based routing — these are not edges. The graph is a *lower bound* on relationships.
- **Stale graph = confidently wrong.** Run `codegraph sync` after big file moves, branch switches, or codegen runs.
- **It's a young project.** Great for TS/Python/Go; verify before trusting on heavily metaprogrammed Ruby/Python codebases.

When the graph might be lying (heavy reflection, codegen, dynamic routes), fall through to a scout subagent and note it.

## See also

- [[delegate-work]] — fallback when CodeGraph can't answer
- [[tier-model]] — graph queries cost no tokens; even cheaper than Haiku
