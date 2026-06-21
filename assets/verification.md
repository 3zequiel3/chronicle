# Verification — correctness against the source (deep Audit, on-demand)

Verifies that the documentation **matches reality**, not just itself. Takes each `code`/`doc`-cited claim, returns to the cited source, and rules on whether the claim holds.

> Consistency = the doc agrees with itself. Completeness = it has all its parts. **Correctness = it agrees with the source.** The latter is what this pass verifies.

This is an **optional depth of Mode Audit**, not a new mode. It reads code in **read-only** mode (consistent with the master rule: reading yes, modifying never).

---

## Token economy (design principle, not optional)

Verification is what most easily burns a session. The pass is bounded by design:

1. **On-demand** — runs only when the user (or CI) requests it. Generation never verifies against code; it only auto-checks form.
2. **Isolated sub-agent** — all expensive reading happens in a sub-agent with its own context that returns **only compact verdicts**. The main session does not inflate.
3. **Group by source** — citations are grouped by `file#symbol`; each source is read **once** and all its claims verified together.
4. **Read the slice, not the file** — the anchor points to a symbol; that function/region is read, not the whole file.
5. **Budget-bounded and risk-prioritized** — verifies the important claims first, stops at budget, and **reports coverage**. Never pretends to have verified everything.

---

## Mechanical first, semantic after (division of labor)

Verification has two parts with different costs and natures — **do not mix them**:

- **The mechanical part is handled by the checker** (`checker-spec.md`), deterministic and token-free: does the cited symbol **exist**? did its fingerprint **change** since the ledger? That is an independent oracle, not a model opinion.
- **The semantic part is handled by the LLM**, and **only that**: does the claim **match** what the symbol actually does? That is the only part irreducible to regex.

Staleness (cheap, mechanical) filters what reaches the LLM: you don't re-verify semantically what hasn't changed. The cheap bounds the expensive.

---

## The pass, step by step

1. **Collect** the `code`/`doc` citations within scope (the whole KB, a node, or a feature). `user`/`inferred` citations **are not verified** — there is no factual source to check against.
2. **Mechanical filter** — the checker resolves existence + fingerprint change against the ledger. What exists and **hasn't changed** is reused (cached verdict); what has disappeared is already flagged without spending LLM tokens. Only **changed or never-verified** items proceed to semantic judgment.
3. **Group** pending claims by file (each source is read once).
4. **Prioritize** by risk: `RN` (business rules) → entities/contracts (`04`) → flows (`07`) → rest.
5. **Dispatch to the sub-agent to REFUTE, not to confirm.** The batch carries `(claim, citation, path#symbol)` with the instruction: *"find evidence that the doc is WRONG. If you cannot support it with the source, the verdict is `contradicted`/`unsupported`. When in doubt, do NOT confirm it."* The refutation framing catches more than the confirmation framing at the same cost. **Prefer the test as source**: if the claim cites a test, verify against the test assertion (the contract), not against the implementation. The sub-agent reads only those symbols in read-only and returns verdicts.
6. **Stop** when the budget is exhausted; anything not reached stays `unverified` (reported, not hidden).
7. **Persist and report.** Verdicts are written to the ledger **through the checker** (see §ledger ownership), never by hand-editing the JSON. Report coverage.

### Verdicts

| Verdict | Meaning | Action |
|---|---|---|
| `confirmed` | the code/doc supports the claim | nothing |
| `contradicted` | the source says something else | log in `10` + flag the item |
| `unsupported` | the citation is insufficient to support it | review the citation or the claim |
| `unverified` | not reached (budget/source not accessible) | reported in coverage |

### Reinforced verification (multi-judge, optional — for high risk)

A single sub-agent judging "does it match?" is the same model family with the same blind spots. For **higher-risk claims** (business `RN` rules, or those the user marks critical), reinforce with **2-3 independent judges**, each using the refutation framing and **without seeing the others' verdicts**:

- A claim **holds only if the majority confirms it**. A single `contradicted` downgrades it to **suspect** (→ `10`), it does not confirm it.
- To diversify (not redundate), give them **different lenses** when applicable: one checks against the **test**, another against the **implementation**, another against the **contract/usage**. Different lenses catch failures that three identical judges miss.

It is **opt-in and budget-bounded** (token economy): reserved for high risk, not the whole KB. The default is single judge; multi-judge is requested ("verify reinforced") or triggered automatically on `RN` items when budget allows. Report how many judges voted per claim.

### Post-generation audit (adversarial sample, fresh-context)

This is the cheap **semantic complement** to the close-gate mechanical check (`edge-cases.md` §Final self-check). The mechanical gate checks whether the citation **exists and resolves** (form); this audit checks whether the **content** of the claim matches the source — the failure grep cannot see.

- **Trigger**: when closing a generator mode (optional), or when the user asks "audit what you generated".
- **Fresh-context**: run by a sub-agent **with no memory of having generated**. Fresh eyes catch the drift that the author cannot see in their own output (this is `requesting-code-review` applied to one's own output).
- **Sample, not exhaustive**: N high-risk claims (`RN` first), bounded by budget. Not the full pass — a cheap, early **spot-audit**.
- **Adversarial**: same refutation framing ("find evidence it is WRONG").
- **Reports, does NOT block**: this is LLM-level (costs tokens, non-deterministic) → **never** a blocking gate (rule from `automation.md`). The blocking gate is the mechanical one; this logs findings in `10`. If contradictions are found, the user decides whether to run the full pass or move to Mode Update.

---

## The ledger (shared mechanism with staleness)

Persisted at `.ledger/verification.json` (project-root tooling storage — `.ledger/`, a sibling of `knowledge-base/`, since a consumer without a KB may still need the ledger). The KB nodes stay clean Markdown; tooling state lives separately as JSON under `.ledger/`.

> **Ledger ownership (hard rule).** `verification.json` is written **only by the mechanical checker** (`checker-spec.md` §6). The LLM **never edits it by hand** — it only reads it to decide what to re-verify. Tooling state is the tooling's responsibility; keeping it in natural language drifts.

> **Shared fingerprint projection.** The fingerprint values in this rich ledger are also **mirror-projected** (merge, never overwrite) into `.ledger/fingerprints.json` — a flat, versioned map that an external consumer (e.g. the `herald` skill) reads without knowing chronicle's internals. Same algorithm, same ownership. Full contract + schema in `checker-spec.md` §6.

```json
{
  "version": 1,
  "verified_at": "<timestamp>",
  "ref": "<git commit at fingerprint time, if git is available>",
  "coverage": { "verified": 40, "total": 120, "unverified": 80 },
  "claims": [
    {
      "id": "RN-PAGOS-01",
      "node": "05_reglas-de-negocio/pagos.md",
      "citation": "code · src/payments/rules.ts#validateCoupon",
      "fingerprint": "<digest of the cited symbol's body>",
      "verdict": "confirmed",
      "note": ""
    }
  ]
}
```

**The `fingerprint`** is a hash of the cited symbol's body, **normalized** — spaces, formatting, and comments collapsed — so a reformat or a new comment does **not** count as a change (only real logic changes do). Calculated with the available hashing tool (`sha256sum`/`shasum` or equivalent); without hashing, a normalized structural signature as fallback. The `ref` field stores the git commit of the run (if git is available), used by staleness as baseline. This is the backbone shared by two features:

- **This pass (verification)** uses it to **skip** claims whose source has not changed.
- **Staleness** (`staleness.md`) compares it against the current fingerprint: if it differs, the source changed and the claim becomes **suspect**.

Designing the fingerprint once is what lets staleness plug in without redesign.

---

## Edge cases

| Case | What to do |
|---|---|
| The cited source no longer exists (symbol deleted) | `contradicted`/`unsupported` + note; staleness will treat it as stale. |
| Claim with multiple citations | holds only if **all** its sources confirm it; if one contradicts, `contradicted`. |
| `doc` citation (Mode A) | verified against the source document, just as `code` against code. |
| No budget for everything | prioritize by risk and honestly report `unverified`; never mark green what was not verified. |
| User has no code access (docs only) | `doc` citations are verified; `code` citations stay `unverified`. |

---

## Output

Mode Audit adds a correctness section to the report (see `quality-rubric.md`):

```markdown
## Correctness (deep verification)
- Coverage: 40/120 claims verified (budget exhausted).
- ✅ 37 confirmed · ❌ 2 contradicted · ⚠️ 1 unsupported.
- ❌ RN-PAGOS-07 contradicted: the code does not retry idempotently → 10.
```

The pass **does not modify the KB** by itself; contradictions are logged in `10` and the user decides whether to move to Mode Update.
