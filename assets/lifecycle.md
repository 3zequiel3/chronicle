# Lifecycle — Update, Governance & Audit

Covers maintenance of an existing KB: non-destructive merge (Mode Update), conditional governance, and validation (Mode Audit).

---

## 1. Mode Update — non-destructive merge

Triggered when `knowledge-base/` already exists and the user requests an update/improvement. **Never regenerates the entire KB.**

### Algorithm
1. Read the existing KB (the affected nodes, not everything if scoped to a feature).
2. **Respect what is correct** — do not rewrite valid content for its own sake.
3. **Fill gaps** — add what is missing.
4. **Mark what changed** — leave a trace of what was touched (see changelog, §2).
5. If the change is feature-driven, reuse the Mode C trace map (`reverse-documentation.md`); if it is about missing discovery fields, reuse the Mode B questions.

### Node promotion
If the update causes a file-collection node to cross its threshold (see `node-templates.md` §File↔folder rule), the skill **promotes the node to a folder**: creates `0X_<name>/`, distributes content by unit, writes the `README` with the map, and **updates all cross-references** to the new paths. Documentation refactor, never a code refactor.

### Golden rule of the merge
Do not destroy. When in doubt between overwriting and preserving, preserve and flag the divergence as a question in `10_preguntas_abiertas.md`.

### Delta sync (post-apply, orchestrated)

When `scope.change_diff` + `scope.codes` are provided (typically after `sdd-apply`):
read **only** the nodes those codes map to (via `knowledge-base/index.json`) plus the diff —
not the whole KB. Apply the standard non-destructive merge to those nodes, refresh their
fingerprints (ledger-owned) and the manifest, and return the result contract with
`codes_touched` set to the synced codes. This is the delta-targeted path; it never re-reads
untouched nodes (token economy).

### Open question resolution (living backlog)
`10` is a **living backlog, not a log**. When an Update resolves an open question (or an `SU-NN` assumption from `09`):
1. The answer **migrates to its own node** (decision → `09`, rule → `05`, entity → `04`, etc.).
2. The question/assumption **is deleted** from `10`/`09`.
3. The resolution is recorded in `CHANGELOG.md`.

This way `10` **shrinks** as items are resolved and never grows without bound. Same when a test is added to a `⚠ no test` rule: the Update **removes the marker** (self-cleaning).

---

## 2. Conditional governance (gate: `maintenance_context`)

Governance metadata only makes sense when the doc is maintained by **more than one person or involves handoffs**. Gated by `maintenance_context` (see `interview-guide.md` §Q-language):

| Element | `solo` | `team` |
|---|---|---|
| `owner` per node | ❌ off | ✅ on |
| `last-reviewed` (date) | ❌ off | ✅ on |
| `review-cadence` | ❌ off | ✅ on |
| KB changelog | optional | ✅ on |

When **on**, each node carries a metadata block at the top:

```markdown
> **Owner**: @equipo-pagos · **Last reviewed**: 2026-06-16 · **Cadence**: trimestral
```

### KB Changelog
File `knowledge-base/CHANGELOG.md` that records what changed between regenerations/updates:

```markdown
## 2026-06-16
- [Update] 05_reglas-de-negocio/pagos.md — +3 reglas (RN-PAGOS-09..11) desde feature checkout.
- [Promote] 04 modelo de datos: archivo → carpeta (12 entidades).
```

> **Compliance is a separate axis**: the security/compliance file is NOT gated by `maintenance_context` — it is gated by **data type** (PII, payments). A freelancer with a payments system still needs it. See `node-templates`/SKILL §extras.

---

## 3. Mode Audit — validate without generating

Produces no new content: **reports**. Documentary checks (does not read code unless the user explicitly requests it as a cross-check):

### 3.1 Cross-reference consistency
Verifies that referenced codes exist and resolve:
- every `RN-XX-NN` cited in `06`/`07` exists in `05`,
- every `US-NNN` linked resolves to a story in `06`,
- every `DD-NN` referenced exists in `09`,
- links to entities (`04_modelos-apis/modelos/*.md`) resolve to real files.

### 3.2 Internal drift between documents
Detects **internal contradictions** between nodes (without looking at code):
- "the `04` declares 8 entities but the `02` mentions 11",
- "the `06` uses an actor that `03` does not define",
- "a flow in `07` references a rule that is not in `05`".

### 3.3 Completeness score per node
Reports coverage per node against its template (`node-templates.md`):

```markdown
| Node | Score | Missing |
|---|---|---|
| 05 rules | 60% | domains without RN codes; missing "global exceptions" |
| 07 flows | 40% | error cases missing in 3 of 5 flows |
```

### 3.4 Provenance coverage
Measures what percentage of factual claims carry a source citation (see `provenance.md` and `quality-rubric.md` §5). Reports claims **without a citation or `inferred` marker** as defects — those are the ones that violate the master rule.

### 3.5 Correctness verification (deep, on-demand)
Checks 3.1-3.4 are cheap and measure **form** (consistency, completeness, citation coverage). **Substance** verification — that each cited claim matches its source — is **opt-in** because it is expensive: requested explicitly ("audit with verification"), runs in an isolated sub-agent bounded by budget, and persists in a ledger. Full contract in `verification.md`. This is what turns the Audit from "it is complete" to "it is correct".

### 3.6 Staleness (on-demand, cheap)
Detects whether **code has changed** since it was documented, by comparing fingerprints against the ledger — with the git fast-path, nearly free. Flags claims as `stale`/orphaned/moved (does not rewrite) and serves as a **cheap filter** for verification 3.5 (only what changed is re-verified). Full contract in `staleness.md`.

### Audit output
A prioritized report (High/Medium/Low) with actionable findings. Does not modify the KB unless the user requests moving to Mode Update with those findings.
