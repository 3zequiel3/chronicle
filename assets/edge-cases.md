# Edge Cases — boundaries and final self-check

What to do when the situation is not clean, and the verification the agent runs before closing. Load this asset when detection is ambiguous or before finalizing.

---

## Detection boundaries (Step 0)

| Situation | What to do |
|---|---|
| `docs/` **and** `knowledge-base/` both exist | Ask: update the KB (Update) or regenerate from docs (A)? Do not assume. |
| `docs/` with only a `README` | Not a source → treat as Mode B (from scratch), not Mode A. |
| `knowledge-base/` exists but is incomplete | Mode Update (fill gaps), not recreate from scratch. |
| No recognizable manifest (unknown stack) | Do not invent the stack → ask, or mark `stack: unknown` and add a note to `10`. |
| Polyglot monorepo | `stack` structured per service; in Mode C, trace cross-language. |
| Code with no docs and no concrete feature request | Mode C needs a target → ask which functionality to document first. |
| Ambiguous user intent | Resolve with an explicit Q-INTENT before acting. |
| No search tool available (Mode C, neither native nor `rg`/`git grep`/`grep`) | **Do not trace blindly.** Ask the user to install ripgrep with the OS-specific command and explain why (see `reverse-documentation.md` §0 Preflight). |
| Windows (path separator `\`) | Normalize citation paths to `/` for cross-OS stability. |

---

## Structural boundaries

| Situation | What to do |
|---|---|
| A collection crosses the threshold during an Update | Promote file→folder and **update cross-references** (do not leave them broken). |
| A feature (Mode C) touches another piece of functionality | Boundary rule: cross-reference and stop — do not document the other. |
| Node disabled by the `system_type` profile | Note the omission in the index; do not leave an empty file. See `node-templates.md` §Axis 1. |
| Mixed language in the existing KB | Detect the dominant language and keep it; do not mix (see `conventions.md`). |

---

## Content boundaries (master rule)

| Situation | What to do |
|---|---|
| The code does something and the reason is unclear | The WHAT goes in the node; the WHY → ask (→ `09`) or → `10`. Never invent. |
| Two sources contradict each other (Mode A) | Record it as `IN-NN` in `10`, do not choose silently. |
| Discovery field cannot be inferred | Conservative default + `[DISCOVERY]` note in `10` (see `discovery-fields.md`). |
| MVP/Post-MVP tag unknown in Mode C | No tag + doubt in `10`; the code does not carry roadmap intent. |

---

## Final self-check (before closing, all generator modes)

Closing has **two levels** — and the mechanical level takes authority.

### Mechanical level (AUTHORITY — run by the checker, not the LLM)

These checks are deterministic, so **the model does not "verify" them against itself**: they are run by the **mechanical checker** (`checker-spec.md`), the **same binary as the CI gate**. It is **fail-closed**: do not declare the KB complete if the checker is red.

1. **Cross-consistency** — every referenced `RN`/`US`/`DD` exists and resolves.
2. **Live links** — paths to entity/domain files resolve.
3. **Provenance coverage** — every factual claim carries a citation (`[code/doc/user]`) or is marked `[inferred → 10]`. No citation = defect (master rule, see `provenance.md`).
4. **Existence spot-check (anti-fabricated-citation)** — cited symbols **exist** at the cited path. Scales with size, not a fixed cap: **all** high-risk citations (`RN` + contracts/entities from `04`) always, + a proportional sample (~20%, minimum 10) of the rest, bounded by budget. Report actual coverage (`checked/total`); broken anchor → mark it and add to `10`.

**Persistence + enforcement.** The result is saved to `knowledge-base/.chronicle/last-check.json` with the git ref. If the project **does not yet have a generated checker**, run these four using your deterministic tools (grep/regex over the KB) as an equivalent, and **offer to generate the persistent checker** so CI/pre-commit can re-run them without you. The **real** catch is CI; the run close is the early catch. If anything is red: **fix it or mark it `inferred`/`→10`** and re-run — never close declaring "complete" over red.

### Judgment level (run by the LLM — not mechanizable)

5. **Completeness** — run `quality-rubric.md`. Any node < 50% → note in `10`.
6. **No source code touched** — confirm that no source code files were modified.
7. **Language** — a single language throughout the entire KB.

Honesty about status is part of the contract: report actual coverage, never "complete" over a partial sample.

> **Semantic complement (optional, non-blocking).** The mechanical gate sees form (exists/resolves), not content. To catch a claim that exists but is **wrong**, run the **post-generation audit** (`verification.md` §Post-generation audit): a fresh subagent adversarially audits a high-risk sample. Costs tokens → reports to `10`, does not block. The blocking gate remains the mechanical one.
