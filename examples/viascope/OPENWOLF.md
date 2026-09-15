---
gmd: "0.1"
id: viascope-openwolf
title: OpenWolf Rules (Viascope)
tags: [memory, learning, bug-log]
imports: [viascope-claude]
---

# OpenWolf Rules {#root}

Memory + learning + bug-log workflow rules. Source: `.claude/rules/openwolf.md`.

# Read-before-act {#read-before-act}

## Check anatomy {#read-anatomy}

Check `.wolf/anatomy.md` before reading any project file.

## Check do-not-repeat {#read-dnr}

Check `.wolf/cerebrum.md` Do-Not-Repeat list before generating code.

rel: depends-on -> [[#dnr-list]]

## Check buglog {#read-buglog}

BEFORE fixing any bug or error: read `.wolf/buglog.json` for known fixes.

rel: depends-on -> [[#buglog-store]]

# Write-after-act {#write-after-act}

## Update anatomy and memory {#write-anatomy}

After writing or editing files, update `.wolf/anatomy.md` and append to
`.wolf/memory.md`.

## Update cerebrum on correction {#write-cerebrum-correction}

After receiving a user correction, update `.wolf/cerebrum.md` immediately
(Preferences, Learnings, or Do-Not-Repeat).

rel: part-of -> [[#cerebrum]]

## Log all bug fixes {#write-buglog}

AFTER fixing any bug, error, failed test, failed build, or user-reported
problem: ALWAYS log to `.wolf/buglog.json` with `error_message`,
`root_cause`, `fix`, and `tags`.

rel: part-of -> [[#buglog-store]]

# Learning {#learning}

## Low-threshold learning {#learn-low-threshold}

LEARN from every interaction: if you discover a convention, user preference,
or project pattern, add it to `.wolf/cerebrum.md`. Low threshold — when in
doubt, log it.

rel: part-of -> [[#cerebrum]]

## Repeated edits = bug {#learn-repeat-edit}

If you edit a file more than twice in a session, that likely indicates a
bug — log it to `.wolf/buglog.json`.

rel: part-of -> [[#buglog-store]]

# UI workflows {#ui-workflows}

## Design QC {#designqc}

When the user asks to check/evaluate UI design: run `openwolf designqc` to
capture screenshots, then read them from `.wolf/designqc-captures/`.

rel: part-of -> [[viascope-claude#hr-ui-tiers]]

## Framework change {#framework-change}

When the user asks to change/pick/migrate UI framework: read
`.wolf/reframe-frameworks.md`, ask decision questions, recommend a framework,
then execute with the framework's prompt.

# Stores {#stores}

## Anatomy {#anatomy-store kind=file path=.wolf/anatomy.md}

Project layout snapshot. Updated on file write/edit.

## Memory {#memory-store kind=file path=.wolf/memory.md}

Append-only log of agent activity. Written after every file change.

## Cerebrum {#cerebrum kind=file path=.wolf/cerebrum.md}

Three sections: Preferences, Learnings, Do-Not-Repeat.

### Do-Not-Repeat list {#dnr-list}

Patterns/approaches the user has corrected away from. Consulted before code
generation.

rel: contradicts -> [[viascope-claude#anti-patterns]]

## Buglog {#buglog-store kind=file path=.wolf/buglog.json}

Structured JSON log of bugs and fixes. Fields: `error_message`, `root_cause`,
`fix`, `tags`. Indexed by tag for retrieval.

rel: supports -> [[viascope-claude#hr-regression-test]]
