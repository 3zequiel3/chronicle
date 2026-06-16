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

## Behavior by mode

- **Mode A (ingest)**: each claim cites `doc` (which source originated it). Anything not traceable to a source → `[inferred · → 10]`.
- **Mode B (scratch)**: no system is built yet → claims cite `user` (what the user decided) or remain as proposals. No `code` is fabricated.
- **Mode C (reverse)**: the central case. Each WHAT claim cites `code` with a symbol anchor. WHY answers the user gives (Q-WHY) cite `user`; unanswered WHYs → `[inferred · → 10]`.
- **Mode Update**: citations are kept and refreshed when re-documenting; a re-derived claim refreshes its anchor.
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

---

## Why this is the backbone

The format is deliberately **parseable** because three features consume it:

- **§3 Correctness** — takes each `code`/`doc` citation and verifies the claim against its anchor.
- **§5 Staleness** — re-resolves the `#symbol`; if it changed or disappeared, marks the section as suspect.
- **§6 CI** — parses citations and reports coverage (% of cited claims) as a quality metric with exit code.

Designing the citation format once, correctly, is what lets those three features plug in without redesign.
