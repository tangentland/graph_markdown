---
gmd: "0.1"
id: viascope-example-readme
title: Viascope GMD Example — Notes
---

# Viascope GMD Example {#root}

GMD rendering of a real, complex `CLAUDE.md` from the Viascope project and its
three supporting instruction files. Demonstrates GMD spec v0.1 against a non-toy
document — 485-line root file, dense ADR cross-references, eliminated-concept
rules, multi-tier failure-mode citations.

Source files (originals, unmodified):

- `/Users/tholley/github/atollogy/bdep/viascope/CLAUDE.md`
- `/Users/tholley/github/atollogy/bdep/viascope/.rtk/CLAUDE.md`
- `/Users/tholley/github/atollogy/bdep/viascope/.refmatrix/CLAUDE.md`
- `/Users/tholley/github/atollogy/bdep/viascope/.claude/rules/openwolf.md`

GMD renderings here:

- [[viascope-claude#root]] — main file ([CLAUDE.md](CLAUDE.md))
- [[viascope-rtk#root]] — RTK commands ([RTK.md](RTK.md))
- [[viascope-refmatrix#root]] — refmatrix briefing ([REFMATRIX.md](REFMATRIX.md))
- [[viascope-openwolf#root]] — openwolf rules ([OPENWOLF.md](OPENWOLF.md))

## What this example exercises

| GMD feature | Where to see it |
|-------------|-----------------|
| Stable `{#id}` on every rule/concept | [[viascope-claude]] §Non-Negotiable |
| `supersedes` edges for eliminated concepts | [[viascope-claude#elim-handle]] [[viascope-claude#elim-vsdtn-id]] |
| `depends-on` edges from rules to ADRs | [[viascope-claude#adr-first-gate]] |
| `evidence-for` edges from incidents to rules | [[viascope-claude#failure-session-53]] |
| `contradicts` edges across docs | [[viascope-claude#tenet-ff]] |
| Cross-doc references via `imports` frontmatter | all four files |
| `part-of` hierarchy distinct from heading tree | [[viascope-claude#channel-invariants]] |
| Attribute lists on nodes (`kind=`, `adr=`) | throughout |

## Observations from authoring

1. **ADR citations finally first-class.** Originals say "ADR-0063 §4.1" in
   prose; GMD makes the edge `rel: defined-in -> [[adr-0063]]`. Tooling can
   crawl the graph instead of regex-scanning prose.
2. **Eliminated-concept rules collapse cleanly.** "Do not reintroduce X"
   becomes `supersedes` edges from the replacement to the dead concept. Future
   agents see graph, not English prohibition.
3. **Failure-mode incidents become evidence.** "Discovered session 53" lines
   were footnote-feeling in prose; as `evidence-for` edges they're first-class
   support for the rule that exists *because* of them.
4. **Cross-file edges replace `@import`.** `@.rtk/CLAUDE.md` directive still
   needed (Claude Code parses it), but semantic linkage is in frontmatter
   `imports:` and explicit `[[doc#id]]` references.
5. **The root file shrinks.** Long expository tables (ADR cross-reference,
   reading order) can be replaced with `rel:` chains and computed views once
   tooling exists. Kept verbose here for spec-conformance demo; production
   tooling would compute the table from the graph.

## What this example does NOT do

- No DuckDB index built. Pure text demonstration.
- No `gmd lint` run. Some cross-refs may dangle — that's the point: shows where
  validation tooling will earn its keep.
- Original files unchanged. This is a parallel rendering, not a migration.
