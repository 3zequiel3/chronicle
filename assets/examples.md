# Examples — an end-to-end walkthrough by mode (few-shot)

End-to-end examples, one per mode. **Load only the section for the active mode.** They serve as style and expected-flow references.

> The examples use the `web_app` profile (ecommerce) for concreteness. With a different `system_type` the flow is the same, but the **profile reframes the nodes** (`node-templates.md` §Axis 1): a library documents its public API in `04` and does not generate `03`/`07-UI`; a pipeline builds the DAG in `07` and stages in `06`; a CLI documents commands in `06`. The mechanics of each mode do not change.

---

## Mode A — silent ingest

**Input**: `docs/descripcion.txt`, `docs/historias.docx`. No `knowledge-base/` present.

**Flow**:
1. Layer 0 detects `docs/` with sources → proposes Mode A.
2. Reads sources, infers discovery (`discovery-fields.md`): `system_type: web_app`, `domain: ecommerce`, `stack: Django + React`.
3. `trajectory`/`maintenance_context` not inferable → conservative default + note in `10`.
4. Generates the 10 nodes. `04` has 5 entities → stays as a **file** (not a folder).
5. Self-check (`quality-rubric.md`); closes with summary table.

**Close**:
```markdown
## KB generada en knowledge-base/
| Nodo | Líneas | Temas |
| 01_vision_y_objetivos.md | 84 | propósito, 3 actores, alcance v1 |
| 04_modelo_de_datos.md | 120 | 5 entidades, ERD |
[DISCOVERY] trajectory/maintenance sin confirmar → ver 10_preguntas_abiertas.md
```

---

## Mode B — from scratch

**Input**: empty repo. User: "let's build the KB from scratch".

**Flow**:
1. Q-INTENT → `create`. Layer 0 detects no stack (no code).
2. Discovery round: P0-sys=(a) web_app, P0-scale=(b), Q-trayectoria=(b) seed → activates scaling checklist, Q-maintenance=(a) solo → governance OFF.
3. Round 1 (P1-P5). P1 is vague ("help sell things") → **rejected**, follow-up asked.
4. Round close with assumptions. Iterates node by node with validation.

**Example question**:
```markdown
**P2 — MVP scope**
What is the minimum "launchable" scope?
(a) catalog + cart + simulated checkout
(b) + real payment
(c) + admin panel
Why it matters: defines v1. Anything left out gets tagged [Post-MVP].
```

---

## Mode C — reverse by feature

**Input**: repo with code, no docs. User: "document the checkout".

**Flow**:
1. Layer 0: `package.json` → Next.js + Prisma. Folders `pagos/`, `stock/`.
2. **Anchoring**: searches "checkout" → finds `api/checkout.route.ts`.
3. **Confirmation**:
   ```
   Found checkout in: checkout.route.ts, payment.service.ts, stock.service.ts.
   Is this right? (yes / adjust / no)
   ```
4. **Scoped tracing** (read-only, cross-language if applicable). When `inventory` is touched → boundary: cross-reference, do not document it.
5. **Vertical-slice merge** with **per-claim citation**: writes `04/modelos/pago.md`, `05/pagos.md`, `06/pagos.md`, `07/pagos-checkout.md`. Example:
   ```markdown
   - **RN-PAGOS-01**: the coupon cannot be applied twice. `[code · src/payments/rules.ts#validateCoupon ~L42]`
   ```
6. An `if` validates the coupon twice and the reason is unclear → Q-WHY; no answer → `[inferred · → 10]`. **Does not invent.**

---

## Mode Update — non-destructive merge

**Input**: `knowledge-base/` exists. User: "update with the returns feature".

**Flow**:
1. Q-INTENT → `update`. Reads affected nodes.
2. Documents "returns" (reuses Mode C tracing).
3. When adding rules, `05` crosses the threshold (22 rules across 4 domains) → **promotion**: `05_reglas_de_negocio.md` → `05_reglas-de-negocio/` and **updates `RN-*` references** in 06/07.
4. Records the change in `CHANGELOG.md`. Respects what was already correct.

---

## Mode Audit — validate without generating

**Input**: `knowledge-base/` exists. User: "audit the KB".

**Flow**:
1. Q-INTENT → `audit`. Generates no content.
2. Runs `quality-rubric.md`: score per node + integrity checks.
3. Reports prioritized:
```markdown
## Completeness
| 07 flows | 40% ❌ | missing error cases |
## Integrity
- ❌ US-014 → RN-PAGOS-09 does not exist.
## Priority
1. [High] Resolve RN-PAGOS-09.
```
4. Does not touch the KB unless the user asks to switch to Mode Update with the findings.
