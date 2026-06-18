# Staleness — did the doc go stale? (cheap check, on-demand)

Detects when documentation has gone stale relative to the code, by comparing the **current** fingerprint of each cited source against the one stored in the ledger (`verification.json`). Without this, the doc silently lies when code changes.

> **Staleness ≠ verification.** Staleness asks *"did the source change?"* — a **mechanical** fingerprint comparison, cheap. Verification (#3) asks *"does the claim still match?"* — judgment, expensive. **Staleness is the cheap filter that tells #3 what to re-verify.**

Read-only, on-demand, in an **isolated sub-agent** (token-economy principle). Reuses the already-built ledger, **normalized** fingerprint, and search-first approach — no redesign needed.

---

## The pass

1. **Git fast-path** (if git is available, see below) → the list of candidate citations (those pointing to changed files). Without git → all `code` citations, bounded by budget.
2. For each candidate citation: re-locate the symbol (search-first), re-compute the **normalized fingerprint**, compare against the ledger.
3. **Classify:**

| Result | Meaning | Action |
|---|---|---|
| equal | the claim is still fresh | nothing |
| different | the symbol changed | **stale** → mark as suspect |
| gone | symbol deleted/renamed | **orphan** → flag |
| moved | symbol exists elsewhere | refresh the anchor (`~Lnn`/file) + review |

4. **Update the ledger** (status + new fingerprint/`ref`) and **report**. Writing to `verification.json` is done by the **mechanical checker**, never by the LLM directly (ledger ownership rule — see `checker-spec.md` §6 and `verification.md`).

---

## Git fast-path (the optimization that makes frequent runs viable)

The ledger stores the `ref` (commit) of the last run. With git:

```
git diff <ref> --name-only        # files changed since the baseline, includes uncommitted changes
```

Only citations pointing to **those files** are candidates; the rest are presumed fresh. Instead of re-fingerprinting 200 symbols you process ~5 touched files. **That is why it is cheap enough to run per-commit in CI** (#6).

> `git diff <ref>` (without `..HEAD`) compares the baseline against the **working tree**, so it **also catches uncommitted changes**. This closes the gap that a purely git-based fingerprint would have.

**Without git**: re-fingerprint all `code` citations, prioritized by risk and bounded by budget; report coverage. More expensive, but correct.

---

## What it produces (no auto-fix)

Read-only + non-destructive: **flags, does not rewrite.**

```markdown
## Staleness
- 6 stale (source changed) · 1 orphaned (symbol deleted) · 2 moved.
- ❌ RN-PAGOS-01 stale: `validateCoupon` changed since the last run.
- ⚠️ RN-STOCK-03 orphaned: `reserveStock` no longer exists.
→ Suggestion: Mode Update scoped ONLY to these 9 claims.
```

The user decides: trigger a **Mode Update** scoped to the stale items (not the whole KB). Optionally, the stale items are passed to **#3** to re-verify whether, beyond changing, they now **contradict** the doc.

---

## Composition with #3 (cheap filters the expensive)

```
staleness (cheap)  →  flags the 9 claims whose source changed
                          ↓
verification #3 (expensive)  →  runs ONLY on those 9, not on all 120
```

You don't re-verify what hasn't changed. The two make each other cheaper.

---

## Edge cases

| Case | What to do |
|---|---|
| `inferred` / `user` citation | Has no code source → staleness **does not apply**. |
| No prior ledger (never fingerprinted) | Nothing to compare against → first run a verification/fingerprint pass (#3) that **seeds** the ledger. |
| Huge repo | The git fast-path keeps it cheap; without git, budget-bounded + coverage report. |
| File changed but cited symbol did not | The fast-path marks it as a candidate, but the normalized fingerprint is **equal** → fresh. No false positive. |
| Symbol moved to another file | `moved` → update the citation anchor and flag for review, do not discard it. |

## Feeding the trust gate (beyond audit reporting)

When invoked from the orchestration trust gate, staleness does more than report: it
**classifies drift by node kind** (per the trust gate, `orchestration.md` §Trust gate) and emits a trust decision.
- Drift in rules/flows/models (04–07) → recommend/auto-flip `code_authoritative` for those nodes.
- Drift touching `system_type`/`kb_language` signals or identity nodes (01/02) → `partial` + risk;
  do not auto-proceed.
Interactive: ask before flipping. Headless: auto-flip and report in `risks`/`assumptions`.
This stays read-only: it decides trust, it does not rewrite.
