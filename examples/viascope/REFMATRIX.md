---
gmd: "0.1"
id: viascope-refmatrix
title: refmatrix briefing for Claude (Viascope)
tags: [tooling, graph-index, discovery]
imports: [viascope-claude, viascope-rtk]
---

# refmatrix briefing {#root}

This project has a refmatrix index at `.refmatrix/` — a roaring-bitmap-backed
graph of docs, code, and concepts. Hooks keep it fresh on git operations and
on every Edit/Write tool call. **Trust the index.**

rel: instance-of -> [[#graph-index-tool]]

# When to reach for `rmx` instead of grep/Read {#when-to-use}

| Question | Command |
|---|---|
| "what calls X" / "where is X used" | `rmx neighbors X --depth 2` |
| "give me everything about X for an LLM" | `rmx context X` (token-budgeted) |
| "what changed since this branch diverged" | `rmx context --since main` |
| "find docs and code mentioning X" | `rmx query "mentions:X OR defines:X"` |
| "explain why an entity matched a query" | `rmx query "<dsl>" --explain` |
| "concepts that co-occur with X" | `rmx co-occur X --type mentions` |
| "rank entities by mention frequency" | `rmx top X --type mentions -k 10` |
| "what does this prompt's symbols touch" | (auto via `UserPromptSubmit` hook) |

`rmx context <symbol>` is the most token-efficient way to understand a symbol's
role — it bundles the symbol's tldr plus immediate neighbors per linkage with
their tldrs, capped by token budget. Prefer it over reading 5 files.

When a query result surprises you, **always re-run with `--explain`** — it
shows file:line evidence for each (linkage, concept) membership that qualified
the entity. That's the trust mechanism.

rel: part-of -> [[viascope-claude#rule-discovery-ladder]]

# Query syntax {#queries}

## DSL (infix set algebra) {#queries-dsl}

```
mentions:parser AND defines:parser
calls:foo OR (mentions:bar AND NOT imports:legacy)
mentions:keyword/data            # namespaced concept (auto-emitted by ingester)
imports:import/json              # python module concept
parser                            # bare term: union across all linkages
```

## PQL (Pilosa-style functions) {#queries-pql}

```
Row(defines, parser)
Intersect(Row(calls, foo), Row(mentions, bar))
Union(...)  Difference(A, B)  Xor(...)  TopN(<bm>, n)  Count(<bm>)
```

# Linkage taxonomy {#linkages}

Defaults: `defines`, `called_by`, `calls`, `mentions`, `imports`, `is_a`,
`related_to`. Plus any custom types added with `rmx add-linkage-type`.

`rmx list-linkages` shows what's actually defined in this project.

# Concept namespacing {#namespacing}

Auto-generated concepts are namespaced so they don't collide with your own:
- `keyword/<word>` — extracted from docstrings (noisy by design; mostly
  filtered out of the primer and `scan-prompt`)
- `import/<module>` — Python imports detected by the ast walker
- bare names — function-name concepts (from `tldr-warm`) and any concepts
  you added with `rmx add-concept`

To query a namespaced concept: `mentions:keyword/foo`, `imports:import/json`.

# Freshness contract {#freshness}

Hooks installed by `rmx install-hooks --apply`:
- `PostToolUse` on Edit/Write/MultiEdit/NotebookEdit → enqueues touched paths
- `Stop` / `SubagentStop` → flushes via `rmx sync --flush-queue`
- `SessionStart` (startup|resume) → flushes + regenerates `.refmatrix/PRIMER.md`
- `UserPromptSubmit` → `rmx scan-prompt` injects bundles for symbols you mention
- git `post-commit` / `post-merge` / `post-checkout` / `post-rewrite` → syncs
  paths changed since the relevant ref

## Diagnostics {#freshness-diag}

- `rmx queue` — pending paths waiting to flush
- `rmx stats --stale` — tracked files where on-disk mtime > last_synced
- `cat .refmatrix/sync.log` — append-only log of every sync, with timestamps
  and `+added ~updated -purged` counts

## Repair {#freshness-repair}

- `rmx sync --flush-queue` — force the pending flush
- `rmx vacuum` — drop empty-bitmap concepts and missing-file tracked rows
- `rmx prune-noise` — drop noise concepts by document-frequency
  (default: drop `keyword/X` with df<2 or df>25% of entities)
- `rmx ingest . --semantic` — full rebuild
- `rmx tldr-warm . --semantic` — fresh call graph from llm-tldr + rebuild

# What you can trust {#trust}

- Bitmap membership reflects state as of the last hook flush.
- `tldr` blobs on entities come from `--semantic` enrichment (Python imports
  + docstring keywords) or manual `rmx add-entity --tldr ...`.
- Function-name concepts come from `.tldr/cache/call_graph.json` if present.
- `linkage_evidence` table records file:line for every semantic linkage —
  shown by `rmx query --explain`.

# Quick reference {#quickref}

```
rmx info                            # active .refmatrix root
rmx stats                           # cardinalities per linkage
rmx stats --stale                   # ... plus drift detection
rmx list-entities --kind concept    # all concepts
rmx list-linkages                   # all linkage types
rmx context <symbol> --format json  # LLM-friendly bundle
rmx context --since <git-ref>       # branch-scoped bundle
rmx query "<dsl>" --explain         # results + linkage chains with file:line
rmx query "<dsl>" --ids-only        # raw entity ids for piping
rmx primer --top 50 --max-tokens 1500    # density-ranked symbol map
rmx scan-prompt --text "<prompt>"        # context for symbols in a prompt
```

# Auto-generated context {#auto-context}

- `.refmatrix/PRIMER.md` — top reference-dense symbols, regenerated on
  `SessionStart`. Add `@.refmatrix/PRIMER.md` to your project CLAUDE.md
  for cheap orientation. (~2K tokens, 150 symbols, no English noise.)
- `UserPromptSubmit` hook runs `rmx scan-prompt` so any symbol mentioned
  in your prompt gets a `rmx context` bundle injected before the turn.

If you're handed a symbol you've never seen, run `rmx context <name>`
explicitly — the hook only kicks in when the symbol appears verbatim.

# Ingest exclusions {#ingest-exclusions}

`rmx ingest .` walks the tree blindly and does NOT honor `.gitignore`. Two
stale mirror trees currently leak into the index and pollute `scan-prompt`
output for every concept (5x duplication per hit):

- `.claude/worktrees/agent-*/...` — abandoned agent worktrees from earlier
  sessions (the "no worktree agents" rule landed AFTER these were created)
- `docker/uat-workspace/...` — UAT snapshot copy, not the live source

Both are listed in `.gitignore` but rmx ingests them anyway. Until rmx ships
an ignore file, every re-ingest must use explicit subpaths:

```bash
# Re-ingest only canonical source trees
rmx ingest src/viascope
rmx ingest tests
rmx ingest docs
rmx ingest pseudocode
rmx ingest scripts
# NEVER bare `rmx ingest .` until the worktrees are removed and uat-workspace
# is moved out of the repo root.
```

rel: contradicts -> [[#anti-pattern-bare-ingest]]

## Purge procedure {#purge}

1. Audit: `sqlite3 .refmatrix/catalog.db "SELECT COUNT(*) FROM entities WHERE
   path LIKE '%.claude/worktrees/%' OR path LIKE '%docker/uat-workspace/%'"`
2. Confirm worktrees are removable (`git worktree list` — they may be locked
   from prior agent sessions; `git worktree remove --force <path>` after
   unlocking).
3. Rebuild rather than SQL-delete — bitmaps in `.refmatrix/bitmaps/` carry
   stale `entity_id` bits even if the entities row is deleted. Safer: drop
   the matrix and re-ingest the canonical subpaths above.

## Anti-pattern: bare ingest {#anti-pattern-bare-ingest}

Running `rmx ingest .` from the repo root. Pulls in stale worktrees and
UAT snapshot, 5x duplicates every concept hit.

rel: contradicts -> [[#ingest-exclusions]]

# Removal {#removal}

Delete `.refmatrix/`, the `rmx` lines from `.git/hooks/*`, and the rmx
entries from `.claude/settings.local.json`.

# External entities {#external}

## graph-index-tool {#graph-index-tool external=true}
Conceptual category for tools that maintain bitmap/graph indices over a
codebase (refmatrix, ctags-derived indices, language servers used as
indexers).
