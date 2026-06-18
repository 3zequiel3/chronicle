# Provenance — the verifiable backbone

Every factual claim in the KB carries a **provenance citation** in a single, machine-parseable format. This turns the master rule ("nothing is invented") from a promise into a **verifiable guarantee**, and is the contract on which correctness verification, staleness detection, and CI checks all rely.

> Hard rule: **a factual claim without a citation is a defect.** Either it cites its source, or it is declared `inferred` and goes to `09`/`10`. There is no third state.

> Hard rule (anti-fabrication): a `code` citation **is only valid if its symbol was actually read** — in Mode C, if it **resolves to a row in the trace map** (`reverse-documentation.md` §3). This is not discipline: it is a **mechanically verifiable foreign key**. The checker (`checker-spec.md` §2.5) flags as **orphan** any `code` citation without a row in `trace-map.json` → defect, no LLM required. The citation is rendered human-readable (`[code · file#symbol]`) but is backed by its row. The `~Lnn` is provided by the search, never by the model's memory. The citation is a byproduct of having read, not a field to fill in while writing.

---

## Citation format

Rendered as **inline code** (visually distinct and greppable):

```
[<type> · <anchor>]
```

| `type` | Meaning | `anchor` form |
|---|---|---|
| `code` | read from code (Mode C / cross-check) | `path/file.ext#symbol ~Lnn` |
| `doc` | from a source document (Mode A) | `docs/file.ext §section` |
| `user` | declared by the user (Mode B / Q-WHY) | `user` (optional: round/date) |
| `inferred` | no source — deduced by the agent | `→ 09:DD-NN` or `→ 10` |

**`code` anchor** (design decision): the **symbol** (function/class/method) is the source of truth — it survives refactors and line moves. The line number (`~Lnn`) is only a **navigation hint**, never the canonical reference.

### Grammar (for tooling — §3, §5, §6)

```
citation = "[" type " · " anchor "]"
type     = "code" | "doc" | "user" | "inferred"
anchor_code     = path "#" symbol [ " ~L" integer ]
anchor_doc      = path [ " §" section ]
anchor_user     = "user" [ ":" reference ]
anchor_inferred = "→ " destination     # destination: 09:DD-NN | 10
```
Extraction regex: `\[(code|doc|user|inferred) · ([^\]]+)\]`

---

## Examples

```markdown
- **RN-PAGOS-01**: coupon cannot be applied twice. `[code · src/payments/rules.ts#validateCoupon ~L42]`
- **Entity Payment**: states pending|paid|refunded. `[code · prisma/schema.prisma#Payment]`
- **RN-STOCK-03**: reservation expires after 24h. `[doc · docs/spec.txt §Inventario]`
- **DD-02**: Postgres was chosen for transactional consistency. `[user]`
- **RN-PAGOS-07**: (possible) idempotent retry. `[inferred · → 10]`
```

---

## What carries a citation (by node)

| Node | Citation? | Typical type |
|---|---|---|
| 04 entities / contracts | **yes, per item** | `code` / `doc` |
| 05 rules (RN) | **yes, per rule** | `code` / `doc` |
| 06 stories (US) | yes, per derived criterion | `code` / `doc` / `user` |
| 07 flows | **yes, per step** | `code` (one tag per hop) |
| 09 decisions (DD) | yes | `user` (never a fabricated `code`) |
| 01 vision · 03 actors | yes | `user` / `doc` |
| 02 · 08 (architecture) | yes where factual | `code` / `doc` / `user` |
| 10 questions | n/a (it is the destination for the uncitable) | — |

> **WHY nodes** (09) cite `user`, never `code` — code does not contain intent. Inventing a `file#symbol` for a decision is a violation of the master rule.

> **Tests = strongest evidence.** When a rule has a test backing it, cite the test (`[code · tests/…#"test name"]`) before the implementation: the test is the expected contract, the implementation is just the mechanism. If the rule comes **only** from the implementation, mark it `⚠ no test` (see `reverse-documentation.md` §Tests as source).

---

## Stable IDs — content-derived, append-only (determinism / P1)

Coded items carry a **stable ID** (`RN-{DOMINIO}-NN`, `US-NNN`, `DD-NN`, `SU-NN`, plus entity/endpoint headings). The **format does not change**; what changes is *how the suffix is assigned*: from the item's **content**, never from generation order. This is what makes a re-run idempotent and two from-scratch runs agree on the same codes.

### Natural key (the identity of an item)

| Item kind | Natural key | Source |
|---|---|---|
| `code`-cited (RN / US / entity / endpoint / flow step) | the cited `file#symbol` | the trace-map row (`reverse-documentation.md` §3) |
| `user` / `doc`-cited (DD decisions, SU assumptions) | a normalized **slug/short-hash of the canonical statement** | the decision/assumption title |

The key is **stable across refactors** for code items (the symbol survives line moves — same rationale as the citation anchor) and **stable across prose drift** for WHY items (the hash is of the canonical statement, not the surrounding paragraph).

### Scope token (the `{DOMINIO}` in `RN-{DOMINIO}-NN`) — also content-derived

The domain token is **not** a free semantic paraphrase (that is where `RN-TODOS` vs `RN-TODO` drift comes from — singular/plural, synonyms). Fix it deterministically:

- **Functionality given** (the normal Mode C / orchestrated case — the user or `scope` names the slice "pagos", "checkout") → the domain **is that name**, normalized (uppercase, ASCII, no pluralization changes). Deterministic by input.
- **No functionality name** (e.g. a headless whole-repo run) → derive the domain from a **code anchor**: the slug of the rules' shared **module / directory** (the `file` in the trace-map row), uppercased. Symbols in `src/payments/rules.ts` → `RN-PAYMENTS-NN`; symbols in `src/rules.js` → `RN-RULES-NN`. Never singularize/pluralize or re-word.

Same principle as the suffix: the token is a function of a stable anchor (input name or module path), never of how the model phrases the domain this run.

### Suffix assignment (canonical sort + append-only registry)

The numeric suffix is **not** the order the LLM wrote things. It is assigned mechanically:

1. **Canonical sort** — within a scope (a domain for `RN-{DOMINIO}`, the whole collection for `US`/`DD`/`SU`), sort the natural keys deterministically.
2. **Registry lookup** — `knowledge-base/.chronicle/registry.json` maps `(scope, key) → ID`, **append-only**:
   - key already in the registry → **reuse** its ID (idempotency);
   - new key → assign `max(seq in scope) + 1` and **append** (never insert-and-shift);
   - item deleted → its number is **retired**, never reused.
3. **No renumbering, ever.** A rule inserted "in the middle" alphabetically still gets the next free number, not a shift of everything below it. The canonical sort decides *order on the page*; the registry decides *the number*.

> **From-scratch vs re-run.** On a first generation there is no registry: the canonical sort alone yields reproducible numbering (same traced symbols → same order → same `NN`), so two independent runs agree. On every later run the registry is the source of truth: reuse + append. Both paths converge on stable IDs.

> **Registry is tooling-owned** — same hard rule as the trace map and `verification.json` (`checker-spec.md` §6). Written by the checker / the deterministic close step, **never** by the LLM from memory. The writer **reads** it to reuse IDs; it does not hand-edit it.

---

## Behavior by mode

- **Mode A (ingest)**: each claim cites `doc` (which source originated it). Anything not traceable to a source → `[inferred · → 10]`.
- **Mode B (scratch)**: no system is built yet → claims cite `user` (what the user decided) or remain as proposals. No `code` is fabricated.
- **Mode C (reverse)**: the central case. Each WHAT claim cites `code` with a symbol anchor. WHY answers the user gives (Q-WHY) cite `user`; unanswered WHYs → `[inferred · → 10]`.
- **Mode Update**: citations are kept and refreshed when re-documenting; a re-derived claim refreshes its anchor. **IDs are reused** from the registry (§Stable IDs) — an updated item keeps its code; only genuinely new items append.
- **Mode Audit**: does not generate, but **measures citation coverage** (see `quality-rubric.md`).

---

## Edge cases (handle all)

| Case | What to do |
|---|---|
| Code has no nameable symbol (loose config, inline SQL) | Anchor = `path ~Lnn` without `#symbol`; always prefer the nearest named symbol. |
| A claim has **multiple** sources | List multiple citations: `` `[code · a.ts#x]` `[code · b.ts#y]` ``. |
| Flow (07) that crosses languages | One `code` citation **per step/hop** of the flow, each pointing to its file/symbol. |
| Rule that is both implemented AND in a doc | Cite both: `` `[code · …]` `[doc · …]` `` — reinforces confidence. |
| Symbol renamed/moved (in Update) | Re-trace and update the anchor; if it no longer exists, mark the claim as suspect → `10`. |
| Claim the agent "knows" but cannot point to | **Do not** write it as fact: `[inferred · → 10]`. This is the master rule enforcement. |
| The symbol you want to cite is not in the trace map | Do not fabricate the citation. Either trace it (it enters the map) or use `[inferred · → 10]`. Citing outside the allowlist is fabrication. |
| Code and doc **conflict** (not merely both present) | **Code wins for the WHAT.** Document the code version with `[code]`; record the conflict in `09`/`10` ("doc said X, code does Y → doc stale") citing both. Never keep the doc claim as fact; never overwrite silently. |

---

## Why this is the backbone

The format is deliberately **parseable** because three features consume it:

- **§3 Correctness** — takes each `code`/`doc` citation and verifies the claim against its anchor.
- **§5 Staleness** — re-resolves the `#symbol`; if it changed or disappeared, marks the section as suspect.
- **§6 CI** — parses citations and reports coverage (% of cited claims) as a quality metric with exit code.

Designing the citation format once, correctly, is what lets those three features plug in without redesign.
