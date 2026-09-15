---
gmd: "0.1"
id: viascope-claude
title: Viascope Project Instructions
tags: [project-instructions, architecture, governance]
imports: [viascope-rtk, viascope-refmatrix, viascope-openwolf]
---

# CLAUDE.md {#root}

@.rtk/CLAUDE.md
@.refmatrix/CLAUDE.md
@.refmatrix/PRIMER.md

## Rule Override Protocol {#override-protocol}

**Explain BEFORE breaking any rule in this file.** State which rule,
why no apply, what do instead. No retroactive justification. No silent deviation.

## Non-Negotiable {#non-negotiable}

### Discovery ladder {#rule-discovery-ladder}

`rmx context` → `rmx query` → `tldr` → `rtk grep`.
grep/find = LAST RESORT — only after rmx + tldr fail or target prose/non-symbol.
Raw grep without rtk forbidden. Full rules in `docs/SUBAGENT_INSTRUCTIONS.md`.

rel: depends-on -> [[viascope-rtk#root]]
rel: depends-on -> [[viascope-refmatrix#root]]
rel: contradicts -> [[#anti-pattern-bare-grep]]

### Agents edit, orchestrator thinks {#rule-agent-role}

Subagent prompts have exact file:line. No "find"/"investigate" in agent prompts.
Open-ended = orchestrator work.

### Test output to file {#rule-test-output}

All test runs: `2>&1 > /tmp/<id>.log`. Never inline.
Agents test only changed files. Orchestrator runs broad suite after merge.

### No silent errors {#rule-no-silent-errors}

Log AND surface. Bare `except: pass` = bug. No empty catch blocks.
No fallback values masking failures.

### Verify before claiming {#rule-verify-before-claim}

Never describe an action as done in a commit message unless the action is
verifiable in the diff. "Intuition seeded" → grep the log for the MCP call.
"Mock registry updated" → `git diff` shows the file changed. "Wired into
app.py" → the import exists in the diff. If the evidence isn't in the commit,
the claim is false.

rel: evidence-for -> [[#failure-plan-23a]] {confidence=high}

#### Failure: Plan 23.A {#failure-plan-23a}

#1 orchestrator failure pattern (6/6 DIRTY in Plan 23.A).

rel: motivates -> [[#rule-verify-before-claim]]

### ADR-FIRST gate {#adr-first-gate kind=hard-gate}

BEFORE CREATING ANY NEW CLASS, TYPE, INTERFACE, OR DATA STRUCTURE,
GREP `docs/architecture/adr/` FOR PRIOR ART. IF AN ACCEPTED ADR SPECIFIES
THE STRUCTURE, IMPLEMENT THE ADR — DO NOT INVENT A NEW DESIGN.

The authority hierarchy: ADR > concept doc > pseudocode > existing code.
Reading existing code patterns and copying them WITHOUT checking ADRs first
is the #1 systemic failure in this project.

rel: derives-from -> [[#adr-0087]]
rel: evidence-for -> [[#failure-session-53]] {confidence=high}
rel: contradicts -> [[#anti-pattern-code-copy]]

#### Failure: session 53 {#failure-session-53}

ADR-0087 specified Zone class (April 16). 52 sessions built 5 fragmented
alternatives by copying existing code patterns. None read the ADR. This rule
exists to prevent that from ever happening again.

rel: motivates -> [[#adr-first-gate]]

### All work concrete {#rule-all-concrete}

No stubs, placeholders, "coming soon," workarounds, or hardcoded placeholder
objects. If the real data source isn't ready, build it.

### No new stubs {#rule-no-stubs}

GraphQL resolvers must not return `[]`, `None`, `NotImplementedError`.
Frontend components must not render hardcoded data or "TODO" text.

rel: part-of -> [[#rule-all-concrete]]

### Pseudocode authority {#rule-pseudocode-authority}

Authority order: architecture docs > pseudocode > task spec > code.
Spec drift from cited `pseudocode/*.pseudo` lines = bug. Pseudocode pre-flight
runs BEFORE spec authoring; post-impl drift round-trips back to `.pseudo` in
same PR. See `docs/PLANNING_WORKFLOW.md`.

---

# Behavioral Guidelines {#guidelines}

Behavioral guidelines to reduce common LLM coding mistakes. Merge with
project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial
tasks, use judgment.

## 1. Think Before Coding {#g1-think-first}

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First {#g2-simplicity}

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes {#g3-surgical}

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution {#g4-goal-driven}

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

Strong success criteria let you loop independently. Weak criteria
("make it work") require constant clarification.

---

# DPath Is the System {#dpath-system}

**VSPN is the system.** VSPN = composition path through channel graph —
each segment edge, each edge transformation step, full path expresses
transformation of meaning from raw pixels to domain language. VSPN not one
axis among peers — it the substance. Other axes lenses on it.

rel: derives-from -> [[#adr-0063]]

## Four projections {#four-projections}

| Axis | Role | Relationship to VSPN |
|------|------|---------------------|
| **VSPN** | Composition path — chain of normalized conceptual labels | IS the system — machine representation of auth-UCLP |
| **VSDTN** | Type classification (`//`-prefixed type name) | Classifies each node on the path |
| **UCLP** | Authoritative chain of conceptual labels in domain language | VSPN is a normalization of auth-UCLP |
| **AID** | Concept identity (UUIDv7) | Identifies the concept the path produces |

rel: defined-in -> [[#adr-0063]]
rel: part-of -> [[#dpath-system]]

## Identity model {#identity-model adr=0063}

- VSPN = composition path — each segment edge, expresses transformation of meaning
- VSDTN classifies type (name, never identity — carried on node, no reach it)
- AID identifies concept (UUIDv7) — thing path produces, persists across restructuring
- UCLP reaches node in domain language
- `_system` definitional — definitions get names, not UUIDs. Only instances get UUIDs.
- **UUIDv7 sole UUID version** (ADR-0063 §4.1, 2026-04-21). v1/v3/v4/v5 prohibited.
- Path prefixes (`@`, `//`, `>>`, `<<`, `#`, `~`, `^`) never stripped.
- `@` = VSPN sentinel — always carried. `#` = Tag/Alias sentinel.
- Edges no get AIDs. If relationship needs identity, it channel.

rel: defined-in -> [[#adr-0063]]
rel: supersedes -> [[#elim-uuid-non-v7]]

# What Viascope Is {#what-is-viascope}

Industrial Machine Vision Data Acquisition. Organizing principle: end-user
**domain language** — common vocabulary of their domain, not ours.

## Channel primitive {#channel kind=primitive}

**Channel** = universal primitive — 4 components: cfg (config), observer
(process), data_node (persist), guide (forward). Linear chain: observe →
persist → forward. No bus. Guide-to-Guide for inter-channel communication.
Channel = composed runtime object — components NOT wired via event bus.

rel: defined-in -> [[#adr-0001]]
rel: part-of -> [[#what-is-viascope]]

## Channel invariants {#channel-invariants}

- **Persist-before-publish.** data_node must succeed before guide publishes downstream.
- **_pre/_work/_post lifecycle.** All four components follow uniform invocation contract.
  `_post()` ALWAYS runs (even on error) — cleanup unconditional.
- **Error propagation as failure records.** Observer errors persisted as structured
  failure entries by data_node. Guide does NOT publish error events to data subscribers.
- **Activation = peer channel, not component.** Activators = COLLECTION-domain channels.
- **Every camera gets DVR.** Every origin camera channel automatically gets
  `//collection.archive` sibling.

rel: part-of -> [[#channel]]
rel: defined-in -> [[#adr-0070]]

## Three-way data split {#data-split adr=0065}

- **Channel config** — parameters driving observer (calibration, weights, thresholds).
- **Dynamic results** — per-capture observer output. 32-field Lance result table (r5, 2026-05-09).
- **Facts** — external time-scoped assertions about world (lot, operator, shift).
  Separate Lance fact store, lazily hydrated along VSPN. Promotion from dynamic result
  to fact always explicit channel operation (validation channel), never silent
  auto-promotion.

rel: defined-in -> [[#adr-0065]]

## Priority tiers {#priority-tiers adr=0094}

- **Tier 0 (Inviolable):** DVR archive writes. Never throttled, never dropped.
- **Tier 1 (Durable):** Observer outputs. Durable queue with WAL spill.
- **Tier 2 (Best-effort):** Derived forwarding. Durable queue; forwarding may defer.
- **Tier 3 (Sheddable):** Health/UI/metrics. Only tier may drop, with structured warning.
- **Admission control:** every channel/archetype enablement capacity-gated.
  Mutations that would compromise Tier 0/1 reserves return `CapacityError`.

rel: defined-in -> [[#adr-0094]]

## Type authority {#type-authority adr=0078}

JSON Schema = canonical type definition source. Pydantic = runtime convenience
generated FROM schema.

rel: defined-in -> [[#adr-0078]]

## Persona {#persona}

**Single user persona — process engineer.** PLC/SCADA engineer does everything;
publishing gated by RBAC, not persona split.

## Frontend {#frontend-role}

Frontend = slave — derives ALL data from backend GraphQL APIs. No shadow copies.
Type registry bootstrapped from `ontologyTypes` query — one source of truth.

# How to Orient {#orientation}

## Mandatory reading order {#reading-order}

**BEFORE any implementation work**, consult the architecture in this order.
Token cost is irrelevant — getting the design wrong costs more.

| Need | Read FIRST | Then |
|------|-----------|------|
| **New class/type/interface** | grep ADRs → matching ADRs | Concept docs → pseudocode → code |
| **Architecture/planning** | `ARCHITECTURE_INDEX.md` → concept docs → ADRs | `how-viascope-works.md` |
| **Pseudocode work** | concept doc + ADR | pseudocode files |
| **Bug fix** | locate relevant pseudocode + ADR | existing code |
| **Spatial/geometry** | [[#adr-0087]], [[#adr-0043]] | `spatial.pseudo` |
| **Identity/UUID** | [[#adr-0063]], [[#adr-0098]], [[#adr-0100]] | `identifiers.pseudo` |
| **Observer/plugin** | [[#adr-0032]], [[#adr-0071]], [[#adr-0102]] | `observer.pseudo` |
| **Type system** | [[#adr-0040]], [[#adr-0041]], [[#adr-0042]] | `type-system.pseudo` |
| **Active plans** | `docs/plan-of-plans.md` | `docs/plans/<plan>-tasks/` |

rel: depends-on -> [[#adr-first-gate]]

## ADR authoring format {#adr-format}

ADRs must follow these conventions so rmx indexes them semantically
(not just as opaque prose). Full reference:
`~/claude_tools/refmatrix/docs/agent-doc-primer.md`.

- **Header fields** inline: `**Status:** Accepted`, `**Governs:** Zone, PathNode` — NOT H2 sections
- **`Governs:`** uses CamelCase concept tokens, not prose descriptions
- **Class specs** in fenced code blocks, `Name:` at column 0 — no `class`/`enum` prefix
- **Cross-references** use exact `ADR-NNNN` form — not "ADR 87" or "#0087"
- **Subclass trees** use `+-- Child(Parent)` notation
- **Verify after writing:** `rmx context <Concept>` must return your ADR.

rel: depends-on -> [[viascope-refmatrix#queries]]

## ADR cross-reference {#adr-xref}

These ADRs specify classes, interfaces, or data structures that MUST exist in code.

| ADR | Specifies | Domain |
|-----|-----------|--------|
| [[#adr-0001]] | Channel 4-component model | Core |
| [[#adr-0002]] | DPath, PathNode, four projections | Core |
| [[#adr-0040]] | 8 Domains, Domain enum | Core |
| [[#adr-0041]] | PathNode, DomainAuthority, Spec hierarchy | Core |
| [[#adr-0042]] | PropertyType enum, 6 PropertyValue models | Type system |
| [[#adr-0043]] | Spatial containment hierarchy (World→Zone→Place) | Spatial |
| [[#adr-0063]] | UUIDv7 sole UUID version | Identity |
| [[#adr-0064]] | ArchetypeStore, CompositionEngine, SpanNode | Archetype |
| [[#adr-0065]] | Three-way data split | Core |
| [[#adr-0070]] | Always-on DVR archive | Storage |
| [[#adr-0071]] | ObserverRequest, ObserverResponse, ObserverContext | Observer |
| [[#adr-0078]] | JSON Schema as type authority | Type system |
| [[#adr-0087]] | Zone, AnnotatedZone, ScoredZone, DetectionZone | Spatial |
| [[#adr-0094]] | Priority tiers, admission control | Capacity |
| [[#adr-0098]] | uuid_from_occurrence | Identity |
| [[#adr-0100]] | UpstreamRef, uuid_at_event | Identity |
| [[#adr-0101]] | Scene-ensemble slate closure pattern | Determination |

# Intent Over Code {#intent-over-code}

**THE ARCHITECTURE IS THE SYSTEM. THE CODE IMPLEMENTS THE ARCHITECTURE.**

Priority hierarchy — THIS ORDER IS ABSOLUTE, NOT ADVISORY:

1. **Architecture docs** (ADRs, concept docs) = what system MUST do
2. **Glossary / canonical vocabulary** = definitive terminology
3. **Design tenets** (A-Z, AA-FF) = structural invariants
4. **Pseudocode** = design-level implementation spec
5. **Existing code** = may have drifted, may predate the ADR

When code contradicts an Accepted ADR, **code is the bug.** Fix code to match ADR.
When pseudocode contradicts an ADR, **pseudocode is the bug.** Fix pseudocode.
When an agent pattern-matches existing code without checking the ADR,
**the agent is the bug.**

rel: contradicts -> [[#anti-pattern-code-copy]]

# VSPN Mechanical Maintenance {#vspn-maintenance}

VSPN maintained mechanically. `recompute_vspn(aid)` = ONE function — computes
`@`-prefixed dot-separated name chain by walking containment edges to root,
persists to `r_name`, cascades to all descendants. Called from every mutation
(create, rename, reparent, delete). `recompute_auth_uclp(aid)` mirrors it for
human label path.

## Eliminated concepts {#eliminated}

Do NOT reintroduce:

### Handle (eliminated) {#elim-handle status=eliminated}

Removed from architecture. `ChannelConfig.handle` → `ChannelConfig.vspn`.
`channel_id_from_handle()` deleted. Instances get UUIDv7 (AID), not
deterministic IDs from path strings. "handle" survives only in third-party
imports (`Handle` from `@xyflow/react`) and standard English verbs
(`handleClick`).

rel: supersedes -> [[#elim-handle-as-identity]]
rel: defined-in -> [[#adr-0063]]

### VSDTN as identity (eliminated) {#elim-vsdtn-id status=eliminated}

VSDTN is a TYPE CLASSIFICATION (`//`-prefixed name). It is NEVER instance
identity. AID (UUIDv7) is the sole instance identity. Code that uses VSDTN
to look up, key, or identify a specific instance is wrong. VSDTN tells you
WHAT something is; AID tells you WHICH one.

rel: supersedes -> [[#elim-vsdtn-as-key]]
rel: defined-in -> [[#adr-0063]]

### Non-v7 UUIDs (eliminated) {#elim-uuid-non-v7 status=eliminated}

v1/v3/v4/v5 all prohibited per ADR-0063 §4.1.

rel: defined-in -> [[#adr-0063]]

## Vocabulary rules {#vocab-rules}

- VSPN variable names contain `vspn` (e.g., `camera_vspn`, `channelVspn`)
- AID variable names contain `aid` (e.g., `parent_aid`, `parentAid`)
- VSPN values always `@`-prefixed (e.g., `@world.floor_1.camera_north`)
- **Prefixed values everywhere.** Every VSPN passed, stored, returned must carry sentinel.
  Raw VSPN string parsing belongs exclusively in DPath/PathNode.
  `lstrip()` always wrong for sentinels.
- `parentId` → `parentAid` in GraphQL schema

# Hard Rules {#hard-rules}

## ADR-FIRST gate (non-negotiable) {#hr-adr-first}

See [[#adr-first-gate]] above. Restated here as a hard gate:

BEFORE WRITING ANY NEW CLASS, TYPE, OR INTERFACE:
`grep -rl "<concept>" docs/architecture/adr/`. IF AN ACCEPTED ADR DEFINES IT,
IMPLEMENT THE ADR SPEC VERBATIM. DO NOT COPY EXISTING CODE PATTERNS THAT
PREDATE OR IGNORE THE ADR.

Every reviewer (vs-alignment, vs-architect, vs-bsd) MUST verify new classes
trace to an ADR or explicitly document why no ADR applies.

rel: supersedes -> [[#anti-pattern-code-copy]]

## ADR-MATERIALIZE gate {#hr-adr-materialize}

When an ADR is accepted, its specified classes, types, interfaces, and data
structures MUST be implemented in code BEFORE any new implementation work
begins that touches the same domain. Skeleton with correct signatures +
module placement is minimum.

**Sequence:** write ADR → implement ADR structures → then build features on top.

rel: depends-on -> [[#hr-adr-first]]

## Tenet check {#hr-tenet-check}

Before proposing a new mechanism, validate: does an existing primitive
already solve this? Read `docs/design/architecture-tenets-catalog.md`
(32 tenets, A-Z + AA-FF) and `docs/architecture/bedrock.md`
(42 trusted primitives).

### Tenet FF {#tenet-ff}

"New code composes existing primitives; it never adds adapters, framework
glue, or scaffolding." If you're building a registry, a framework, or an
adapter — stop and check whether a bedrock primitive already exists.

rel: contradicts -> [[#anti-pattern-adapter-glue]]

## Wire to production {#hr-wire-prod}

No stores without importers. No helpers without callers. If the caller
doesn't exist, build it. Before committing, grep for the new symbol in the
caller file. If zero hits, wiring is missing. vs-bsd audits this at plan
completion — findings persist to `docs/bullshit/`.

## Runtime acceptance {#hr-runtime-accept}

Every task must demonstrate its behavior in a running system
(`docker compose up dev` + trigger + observable output).
`pytest` passing alone is insufficient proof that code works.

## UI-surface assertions {#hr-ui-assert}

Every deliverable in a spec MUST include Playwright E2E assertions with exact
`data-testid` selectors, GIVEN/WHEN/THEN structure, and a specific mutation
that would break it.

**vs-bsd approval is a HARD GATE.** Every assertion must be APPROVED before
implementation can begin. vs-bsd validates that each assertion:
(a) targets an operational invariant, not existence;
(b) would FAIL against current broken/stubbed state;
(c) uses verified real `data-testid` selectors;
(d) cannot false-pass against stubs.

Infrastructure is not exempt. Features classified as "infrastructure"
(IPC wiring, dispatch layers, storage coordinators, reconciliation loops)
still require validation assertions based on operational invariants.

rel: evidence-for -> [[#failure-session-66]]

### Failure: session 66 {#failure-session-66}

vs-bsd audit of T23.1 found 7 BULLSHIT components — stub invoke functions,
hardcoded canned observers, commented-out connector managers — all passing
backend tests while completely dead at runtime.

rel: motivates -> [[#hr-ui-assert]]

## Mutation survival {#hr-mutation-survive}

Every test assertion must survive mutation. Mentally mutate the production
code (flip a comparison, delete a call, return early). If the test still
passes, the assertion is theater.

Anti-patterns: `assert x >= 0` (always true), `assert x is not None` on a
list (always true), raising your own exception and catching it.

rel: contradicts -> [[#anti-pattern-test-theater]]

## Mock registry {#hr-mock-registry}

Every mock/fake-impl needs a `docs/test_mock_registry.md` entry with
classification and graduation trigger in the same commit it's introduced.
Spy/verification mocks (AsyncMock for call counting) are permanent
ACCEPTABLE — state that explicitly. No `internal-pending` mocks from M7+.

## Writer/reviewer verification {#hr-writer-reviewer}

After implementation, run a verification pass in fresh context (not the same
agent). The reviewer checks: (a) every new function has a production caller,
(b) every test assertion survives mental mutation, (c) mocks are registered.
vs-bsd serves this role at plan completion.

## vs-bsd authoritative {#hr-vsbsd-auth}

Runs synchronously at plan completion. BULLSHIT findings block plan close.
SKETCHY must be addressed before close. Read `docs/bullshit/INDEX.md` at
session start; check IMPRESSIONS.md before spec authoring.

## C/H/M findings addressed {#hr-chm-addressed}

No deferral of CRITICAL, HIGH, or MEDIUM to future plans. LOW and OBS may
defer with rationale.

## Name/label never None {#hr-name-required}

Object cannot exist without name. Backend never returns None for name or
label — that's a data integrity bug.

## Regression tests on fixes {#hr-regression-test}

Test must fail before fix + pass after. No fix without regression test.

## No legacy patterns {#hr-no-legacy}

System pre-production. Hard cut on all migrations. No deprecated wrappers,
no backward-compat shims. Delete old approach.

## No false deferrals {#hr-no-false-defer}

Grep before claiming "blocked." If dependency exists, do task.

## Write decisions immediately {#hr-write-decisions}

Context compaction erases unwritten discussion.

## UI testing tiers {#hr-ui-tiers}

Playwright/Chromium = primary tier. JSDOM for pure logic only. Every UI
component must have functional tests covering navigable surfaces, golden
path workflows, data round-trips, error/empty states, and loading states.

# Anti-patterns {#anti-patterns}

Recorded as named entities so rules can reference them explicitly.

## Bare grep {#anti-pattern-bare-grep}

Using raw `grep`/`find` before exhausting `rmx context`, `rmx query`, `tldr`.

rel: contradicts -> [[#rule-discovery-ladder]]

## Code copy without ADR check {#anti-pattern-code-copy}

Pattern-matching existing code to decide on new class/type/interface design,
without first grepping `docs/architecture/adr/`.

rel: contradicts -> [[#adr-first-gate]]
rel: evidence-for -> [[#failure-session-53]]

## Adapter/framework glue {#anti-pattern-adapter-glue}

Building registries, adapters, framework scaffolding when a bedrock primitive
already exists.

rel: contradicts -> [[#tenet-ff]]

## Test theater {#anti-pattern-test-theater}

Assertions that always pass regardless of production behavior — `>= 0`,
`is not None` on a list, self-raised exceptions caught locally.

rel: contradicts -> [[#hr-mutation-survive]]

## Handle as identity (eliminated) {#elim-handle-as-identity status=eliminated}

Using path-string-derived deterministic IDs in place of UUIDv7 AIDs.

rel: supersedes -> []

## VSDTN as key (eliminated) {#elim-vsdtn-as-key status=eliminated}

Using type classification names to key, look up, or identify instances.

rel: supersedes -> []

# Development Environment {#dev-env}

**Docker-only for real codebase.** macOS lacks GStreamer + correct Python ABI.
This pseudocode repo = design-level companion to real viascope codebase.

Key constraints:
- UUIDs: types have names (VSDTN string), instances have IDs (UUIDv7 — sole version per [[#adr-0063]] §4.1). v1/v3/v4/v5 all prohibited.
- UI: Cancel on all modal steps, never "slug" in user-facing UI.

# Work Process {#work-process}

## Branch-first {#wp-branch-first}

`git checkout -b task-X.Y-description main` BEFORE any work.

## Task spec + review gate {#wp-spec-gate}

No implementation without (a) fresh pseudocode + (b) reviewed task spec.
Three phases: vs-alignment freshness → spec authoring → three-reviewer gate
(vs-alignment + vs-architect + vs-test-engineer). Full checklist in
`docs/PLANNING_WORKFLOW.md`.

**Lightweight gate** for plans with ≤ 3 tasks: orchestrator self-reviews
against pseudocode instead of spawning 3 reviewer agents.

## Self-contained task specs {#wp-self-contained}

Specs include ALL information the implementing agent needs — file paths,
current definitions, research findings. Implementing agent NEVER repeats
research orchestrator already did.

## Subagent instruction rule {#wp-subagent-rule}

Every Agent prompt MUST begin with:
`First read docs/SUBAGENT_INSTRUCTIONS.md and follow all instructions within.`
and include the discovery ladder instruction. No exceptions.

rel: depends-on -> [[#rule-discovery-ladder]]

## Reviews persist to disk {#wp-review-persist}

Write full report to `./review-output/<plan>-<phase>-<reviewer>.md` BEFORE
surfacing chat summary. Display-only reviews forbidden.

## Per-task loop {#wp-per-task}

branch → subagent → verify → commit+merge → update `docs/task-status.md` → next.

## Per-group loop {#wp-per-group}

review → address C/H → cleanup → update handoff.

## Task status tracking {#wp-task-status}

`docs/task-status.md` tracks Spec, Review, and Implementation axes per task.
Update in same commit as the underlying transition.

## Token discipline {#wp-token-discipline}

Delegate to subagents. Read with offset/limit. Batch parallel calls.

rel: depends-on -> [[viascope-rtk#root]]

## Git workflow {#wp-git}

`git checkout main && git merge --no-ff task-X.Y-description`.
Plan governance: draft → `docs/incomplete_plans/`; approved → `docs/plans/`;
done → `docs/completed_plans/`.

# Design Tenets {#design-tenets}

32 tenets (A-Z, AA-FF) in `docs/design/architecture-tenets-catalog.md`.
Before proposing new mechanisms, validate: does existing primitive already
solve this?

Existing primitives: channels, domains, DPath (VSPN/VSDTN/UCLP/AID), Specs,
observer contract, productions, domain type system, Guide subscriptions,
DataNode storage, archetypes (elemental + composite — [[#adr-0064]]).

## Archetype composition model {#archetype-model adr=0064}

Archetypes = concrete strategies — elemental (single-channel template) or
composite (span-structured pipeline). No batch compiler. Channels instantiate
on-demand from archetype templates as user makes decisions. Compositions use
spline + branches, bidirectional LTR/RTL construction, CEL at every joint,
`{variable:hint}` VSPN substitution markers. Lance-backed with JSON file
backup for recovery/export.

**Production lifecycle:** DRAFT → ACTIVE → PAUSED → ARCHIVED (no COMPILED state).

rel: defined-in -> [[#adr-0064]]

# Tools {#tools}

- **Web browsing:** Use `/browse` skill from gstack. NEVER use `mcp__claude-in-chrome__*` tools.

# Permissions {#permissions}

- NEVER commit to 'release' branch
- NEVER execute `rm -rf *`
- Allowed to make changes without asking within project

# Referenced ADRs {#adr-stubs}

External entity stubs so cross-file `[[adr-NNNN]]` links resolve. Real ADRs
live in `docs/architecture/adr/`. These nodes exist purely as link targets
for the graph.

## ADR-0001 {#adr-0001 kind=adr external=true}
Channel 4-component model.

## ADR-0002 {#adr-0002 kind=adr external=true}
DPath, PathNode, four projections.

## ADR-0032 {#adr-0032 kind=adr external=true}
Observer plugin contract baseline.

## ADR-0040 {#adr-0040 kind=adr external=true}
8 Domains, Domain enum.

## ADR-0041 {#adr-0041 kind=adr external=true}
PathNode, DomainAuthority, Spec hierarchy.

## ADR-0042 {#adr-0042 kind=adr external=true}
PropertyType enum, 6 PropertyValue models.

## ADR-0043 {#adr-0043 kind=adr external=true}
Spatial containment hierarchy (World→Zone→Place).

## ADR-0063 {#adr-0063 kind=adr external=true}
UUIDv7 sole UUID version. Identity model: VSPN, VSDTN, AID, UCLP.

## ADR-0064 {#adr-0064 kind=adr external=true}
ArchetypeStore, CompositionEngine, SpanNode. Archetype composition model.

## ADR-0065 {#adr-0065 kind=adr external=true}
Three-way data split: channel config, dynamic results, facts.

## ADR-0070 {#adr-0070 kind=adr external=true}
Always-on DVR archive sibling for every camera channel.

## ADR-0071 {#adr-0071 kind=adr external=true}
ObserverRequest, ObserverResponse, ObserverContext.

## ADR-0078 {#adr-0078 kind=adr external=true}
JSON Schema as canonical type definition source.

## ADR-0087 {#adr-0087 kind=adr external=true}
Zone (BBOX+POLYGON), AnnotatedZone, ScoredZone, DetectionZone.

## ADR-0094 {#adr-0094 kind=adr external=true}
Priority tiers (0-3), admission control, capacity envelope.

## ADR-0098 {#adr-0098 kind=adr external=true}
uuid_from_occurrence.

## ADR-0100 {#adr-0100 kind=adr external=true}
UpstreamRef, uuid_at_event.

## ADR-0101 {#adr-0101 kind=adr external=true}
Scene-ensemble slate closure pattern.

## ADR-0102 {#adr-0102 kind=adr external=true}
Observer extension surface.
