---
gmd: "0.1"
id: gmd-readme
title: "GMD — Graph Markdown Tooling"
tags: [readme, gmd, tooling]
---

# GMD — Graph Markdown Tooling {#root}

Graph Markdown (GMD) is a Markdown-compatible convention for documents that
carry **stable block IDs**, **wikilink references**, and **typed edges**.
A GMD file renders cleanly in any Markdown viewer; GMD-aware tools read it as
a graph. It is designed for Claude project docs (`CLAUDE.md`, `SKILL.md`,
memory files, ADRs, notes) where prose gets edited constantly but references
must not rot.

Normative spec: [SPEC.md](SPEC.md) (draft v0.1).

## The three constructs {#constructs}

| Construct | Syntax | Meaning |
|-----------|--------|---------|
| Anchor | `## Heading {#stable-id}` | Stable node id on a heading, paragraph, or list item |
| Wikilink | `[[#id]]` / `[[doc-id#id]]` | Same-doc or cross-doc reference to an anchored node |
| Typed edge | `rel: <verb> -> [[target]] [{attrs}]` | Directed, typed relation from the enclosing block to target |

A document is GMD when its YAML frontmatter contains `gmd: "0.1"`. Frontmatter
`id` is the document's cross-doc address; `imports: [...]` lets `[[id]]`
resolve without a doc prefix.

Minimal example:

```markdown
---
gmd: "0.1"
id: project-alpha
title: Project Alpha
tags: [planning]
---

# Problem {#p1}

Users lose context across sessions.

rel: motivates -> [[#s1]]

# Solution {#s1}

Persistent memory layer keyed by stable IDs.

rel: supersedes -> [[old-design#stateless]] {confidence=high}
```

## Repository layout {#layout}

| Path | Role |
|------|------|
| `SPEC.md` | GMD v0.1 conformance spec (file format, IDs, references, edges, verb vocabulary, conformance levels) |
| `gmd` | Bash dispatcher: `gmd init` / `gmd lint` / `gmd slice` / `gmd version` |
| `lint.py` | Validator. Doc-level and cross-doc checks, exit 1 on errors |
| `slice.py` | Query-driven retrieval of a relevant subgraph from one GMD doc |
| `init.py` | Scaffold a project for GMD authoring (CLAUDE.md section, `.gmd/`, memory migration, agent splices, optional rmx wiring) |
| `migrate_memory.py` | Bulk-add `gmd:` + `id:` frontmatter to existing Claude memory files |
| `lint-memory.sh` | Lint a `~/.claude/projects/<encoded-path>/memory/` tree with the matching project root as resolution scope |
| `examples/viascope/` | Real-world rendering of a 485-line `CLAUDE.md` plus three supporting instruction files in GMD form |

## Quick start {#quick-start}

```bash
# validate one file or a whole tree
gmd lint path/to/doc.md
gmd lint docs/

# validate one file's cross-doc links against the whole repo + memory corpus
gmd lint path/to/doc.md --reconcile

# pull the relevant subset of a large doc for a query
gmd slice CLAUDE.md "release process" --k 5 --hops 1 --budget-tokens 2000

# scaffold a project (dry-run by default; add --apply to write)
gmd init ~/src/myproject --all
gmd init ~/src/myproject --all --with-rmx --apply
```

Without the dispatcher on `PATH`, call the scripts directly:
`python3 ~/claude_tools/gmd/lint.py <path>`.

## Lint {#lint}

`lint.py` runs two phases.

- **Phase 1, doc-level.** Always hard errors. Duplicate `{#id}`, malformed
  `rel:` lines, dangling same-doc `[[#id]]`, frontmatter sanity.
- **Phase 2, cross-doc.** Resolves `[[doc#id]]` across the scanned corpus.
  Hard errors when a directory is in scope; downgraded to warnings for
  single-file targets so a new file never fails on links it cannot see.

Flags:

| Flag | Effect |
|------|--------|
| `--phase1` | Force doc-level only |
| `--phase2` | Force cross-doc errors even for file targets |
| `--scope <path>` | Add files to the resolution set without reporting their issues |
| `--reconcile` | Auto-discover corpus: walk up to the git root, add that tree plus the project's Claude memory dir, force phase 2 |

Exit codes: `0` clean (warnings allowed), `1` errors, `2` invocation error.
Unrecognized `rel:` verbs warn but never fail, per spec §8.

## Slice {#slice}

`slice.py` is a standalone retriever (no index, no rmx). Given a doc and a
query it:

1. Parses the doc into heading-bounded nodes with anchors.
2. Scores nodes by TF-IDF term overlap with the query, title weighted 3x.
3. Takes the top-K as seeds.
4. Expands to all ancestors plus 1-hop `rel:`/wikilink neighbors.
5. Renders the selection in document order with gap markers.
6. Reports token estimates (chars/4) for full doc vs slice.

Options: `--k N`, `--hops N`, `--no-neighbors`, `--budget-tokens N`,
`--show-edges`, `--print-scores`.

## Init {#init}

`init.py` is idempotent, additive, and dry-run by default.

| Flag | Operation |
|------|-----------|
| (none) | Add an `## Authoring Format` section to `CLAUDE.md`; create `.gmd/` scaffolding |
| `--memory` | Migrate this project's Claude memory files to GMD frontmatter |
| `--agents` | Splice the GMD output-format contract into doc-writing agent definitions |
| `--with-rmx` | `rmx init`, hooks, and initial ingest |
| `--all` | `--memory` + `--agents` (not `--with-rmx`) |
| `--apply` | Actually write; otherwise print the plan |
| `--force` | Overwrite existing config |

## Memory tooling {#memory}

Claude memory files are the primary consumer of GMD. Two helpers target them:

- `migrate_memory.py <dir>` inserts `gmd: "0.1"` and `id: <filename-stem>`
  as the first two frontmatter keys of every memory file that lacks them.
  `MEMORY.md` index files are skipped. `--dry-run` supported.
- `lint-memory.sh <memory_dir>` decodes the project root from the encoded
  `~/.claude/projects/<path>/` name and passes that root's `CLAUDE.md` and
  `docs/` as `--scope`, so cross-tree links resolve instead of reporting as
  dangling.

Memory authoring rules (required frontmatter, `{#root}` anchor, typed edges
only, amend/supersede/overwrite decision tree) live in the user's
`~/.claude/MEMORY-RULES.md`.

## Examples {#examples}

`examples/viascope/` renders a real, dense project `CLAUDE.md` and its three
imported instruction files as a linked GMD corpus. It exercises cross-doc
`imports`, ADR-style `supersedes` edges, and multi-tier citation chains
against a non-toy document.

rel: mentions -> [[viascope-example-readme#root]]

## Conformance levels {#conformance}

| Level | Requirement |
|-------|-------------|
| Reader | Renders as Markdown; ignores or shows GMD syntax as text |
| Resolver | Reader + resolves `[[...]]` to anchors |
| Indexer | Resolver + extracts `rel:` edges and node tree into a queryable graph |
| Retriever | Indexer + returns subtree/ego-graph slices on demand |

`lint.py` is a Resolver. `slice.py` is a lightweight Retriever. Full Indexer
and Retriever behavior is provided by rmx when wired via `gmd init --with-rmx`.

## Status {#status}

Spec v0.1, draft dated 2026-05-16. Open questions for v0.2 are listed at the
end of [SPEC.md](SPEC.md): inline `rel:` shorthand, cross-project namespaces,
explicit vs implicit `parent` edges, duplicate-`id` conflict resolution, and
index format standardization.
