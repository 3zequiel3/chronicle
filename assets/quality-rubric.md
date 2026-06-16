# Quality Rubric — completeness score per node

Concrete criteria for scoring how complete the KB is. Used by **Mode Audit** for reporting, and by all generator modes for the **final self-check** before closing.

---

## How scoring works

Each node is evaluated against its **checklist** (defined in `node-templates.md`). The score is the percentage of checklist items satisfied:

```
score(node) = items_satisfied / total_items_in_checklist
```

Quality bands:

| Score | Status | Action |
|---|---|---|
| ≥ 80% | ✅ Complete | none |
| 50-79% | ⚠️ Partial | list what is missing |
| < 50% | ❌ Insufficient | mark as priority |

---

## Criteria per node

| Node | Checklist items |
|---|---|
| 01 Vision | purpose in 1 sentence · explicit scope · out-of-scope |
| 02 Description | stack per layer · diagram · integrations |
| 03 Actors | RBAC matrix · public routes *(N/A for CLI)* |
| 04 Data | ERD · entities with attributes+relations · request/response contracts |
| 05 Rules | every rule with code · MVP tag · justification |
| 06 Features | US-NNN format · acceptance criteria · link to rules |
| 07 Flows | trigger+actor · sequence diagram · error cases |
| 08 Architecture | justified patterns · security · env vars with sensitivity |
| 09 Decisions | alternatives+trade-offs · assumptions with validation |
| 10 Questions | inconsistencies with impact · prioritized questions |

> Nodes that the **profile** of `system_type` deactivates (e.g. RBAC on a CLI, UI-flows on a library, user stories on a pipeline — see `node-templates.md` §Axis 1) do not penalize the score: they are marked **N/A**, not 0%. Only **active** profile slots are scored.

---

## Cross-cutting checks (in addition to per-node score)

These are not about completeness but about **integrity**, and they apply to Mode Audit:

1. **Cross-consistency** — every referenced `RN-XX-NN`, `US-NNN`, `DD-NN` exists and resolves.
2. **Internal drift** — no contradictions between nodes (e.g. entity count in 04 vs 02).
3. **Live links** — references to entity/domain files point to real paths.
4. **MVP tags** — items in 05/06/07 have a scope tag (or a note explaining why not).
5. **Citation coverage** (see `provenance.md`) — every factual claim carries a source citation. Metric: `cited_claims / factual_claims`. A claim without a citation or `inferred` mark is a **defect**. Extraction regex: `\[(code|doc|user|inferred) · ([^\]]+)\]`.
6. **Test coverage** (see `reverse-documentation.md` §Tests as source) — what percentage of rules (`05`) are backed by a test vs. implementation only. Mechanical metric: count rules with a test citation vs. rules with `⚠ no test`. Not a defect — it is **visible risk**: it shows which rules have no safety net.

---

## Report format (Mode Audit and self-check)

```markdown
## Completeness

| Node | Score | Missing |
|---|---|---|
| 05 rules | 60% ⚠️ | domains without code RN; no MVP tags |
| 07 flows | 40% ❌ | missing error cases in 3/5 flows |

## Integrity
- ❌ US-014 references RN-PAGOS-09 which does not exist in 05.
- ⚠️ 04 declares 8 entities; 02 mentions 11.

## Provenance
- Citation coverage: 84% (47/56 claims).
- ❌ 9 claims with no citation or `inferred` mark → defect.

## Test coverage
- Rules backed by a test: 18/25 (72%).
- ⚠️ 7 rules `no test` → visible risk (not a defect).

## Correctness (only if deep Audit was requested — see verification.md)
- Verified coverage: 40/120 (budget exhausted).
- ✅ 37 confirmed · ❌ 2 contradicted · ⚠️ 1 unsupported.

## Priority
1. [High] Resolve missing RN-PAGOS-09.
2. [Medium] Complete error cases in 07.
```

In generator modes, the self-check runs this rubric **against its own output** before closing; if anything falls below 50%, it notes it in `10_preguntas_abiertas.md` rather than pretending it is complete.
