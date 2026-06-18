# Automation — freshness checks, wherever you want (no LLM)

Exposes cheap checks as a **mechanical, deterministic command** that runs on any surface (CI, hooks, manual, or by asking the agent). **Zero tokens**: it is git + regex + hash, not LLM.

> chronicle is a skill (instructions for an agent), not a binary. That is why the **expensive** parts (generating, verifying correctness) require the agent and run on-demand/async; the **cheap** parts (freshness, coverage, cross-reference consistency) are mechanical and **can** be a real CI gate with an exit code.

---

## Two levels

| Level | What it includes | Cost | Use |
|---|---|---|---|
| **Mechanical** | citation coverage · cross-reference consistency · staleness (`git diff`) | free, deterministic | **blocking gate** (PR/commit/manual) |
| **LLM** | correctness verification · generate/update doc | tokens, slow | on-demand / scheduled, **never** a blocking gate |

The gate on each commit/PR burns **zero tokens** because only the mechanical level runs.

---

## The mechanical check (no LLM)

| Check | How (mechanical) | Fails if… |
|---|---|---|
| **Citation coverage** | extracts citations with `\[(code\|doc\|user\|inferred) · [^]]+\]`; counts factual claims without a citation | coverage < threshold |
| **Cross-reference consistency** | resolves each referenced `RN`/`US`/`DD` | there is a broken reference |
| **Staleness** | `git diff <ref> --name-only` → changed files → affected citations → normalized fingerprint vs ledger | there are `stale`/orphaned claims on touched code |
| **Test coverage** | counts rules with a test citation vs rules with `⚠ no test` | (risk metric; blocks only if a minimum is configured) |

**Staleness** is the star check: it implements *"you touched documented code and did not update the doc"* — see `staleness.md`. Works the same in a PR as in a pre-commit for a solo developer.

---

## Machine-readable contract

Report (consumable by any surface):

```json
{
  "status": "pass | fail",
  "checks": {
    "citation_coverage": { "value": 0.86, "threshold": 0.80, "pass": true },
    "cross_ref":         { "broken": 0, "pass": true },
    "staleness":         { "stale": 2, "orphaned": 1, "pass": false, "items": ["RN-PAGOS-01", "RN-STOCK-03"] }
  }
}
```

**Exit codes**: `0` = all pass · `1` = staleness · `2` = coverage · `3` = consistency · (combinable by bitmask if needed). Detail always goes in the report.

**Optional config** (`knowledge-base/.chronicle/checks.json`) — thresholds and what blocks:

```json
{ "coverage_threshold": 0.80, "block_on_stale": true, "block_on_broken_ref": true }
```
Without config, sensible defaults (coverage 0.80, staleness and broken refs block).

---

## Surfaces (PRs are optional)

| Your workflow | Artifact |
|---|---|
| **Generation close** | the **same checker** runs at the end of any generator mode, **fail-closed** (early catch — see `edge-cases.md` §Final self-check and `checker-spec.md` §8) |
| Team with PRs | GitHub Action / GitLab CI on the PR or push |
| **Solo / no PRs** | **pre-commit** or **pre-push** hook (local, stops the bad commit) |
| No hooks | **manual command** whenever you want |
| Zero automation | **ask the agent**: "is the doc stale?" → interactive Mode Audit |
| Scheduled | cron / scheduled agent (for the deep LLM level) |

Nobody is required to use PRs: the capability is the check; the surface is your choice, or none. The generation close is the early catch; CI/pre-commit is the reproducible enforcement (same binary in both).

---

## Generated to spec

chronicle **does not ship a fixed script** (that would lock you to a runtime and bring cross-platform headaches back). Instead, it **emits an artifact tailored to your project** when asked ("set up the CI check"), implementing the runtime-agnostic contract from `checker-spec.md`:

- detects your CI and stack (from Layer 0),
- generates the checker in the **runtime your project already uses** (Node → node, Python → python, Go → go) + the GitHub Action / hook that invokes it,
- cross-platform by construction (Windows/Linux/macOS per target),
- applying the **security rules** from the checker (`checker-spec.md` §5: argv-arrays, parse-no-exec, confinement to the root),
- using the search preflight from `reverse-documentation.md` §0 when the check needs to search.

> **Self-verification before trusting (not optional).** As soon as you generate the checker, run it against the golden fixture (`assets/conformance/sample-kb/`) and compare with `assets/conformance/expected.json`. If it does not match exactly, the checker was generated incorrectly → **regenerate it**. See `checker-spec.md` §7. This way correctness is **verified by generation**, not assumed.

The check is thus turnkey **without** a script that chronicle has to maintain, and without imposing Python or any runtime foreign to the project.

---

## Freshness watch (one-command hook)

The mechanical staleness check (git fast-path, `staleness.md`) is cheap enough to run **on every commit**. The **watch** packages it as a one-command-install hook so "you touched documented code and didn't update the doc" is caught automatically, without anyone remembering to ask.

**Setup** — the user says *"set up the freshness watch"* (or *"watch the docs"*). chronicle, reusing **Generated to spec** above:

- detects the runtime + CI from Layer 0,
- generates the staleness checker (runtime-native, `checker-spec.md`) **and** a `pre-commit` (or `pre-push` / CI) hook that invokes it,
- self-verifies the checker against the conformance fixture before trusting it (`checker-spec.md` §7),
- installs the hook (or prints the one install command), applying the security rules (`checker-spec.md` §5).

**On each commit** the hook runs the git fast-path — `git diff <ref> --name-only` → changed files → cited symbols on them → normalized fingerprint vs ledger — touching only what changed (near-free). Then, per config:

| `on_stale` | Behavior |
|---|---|
| `nudge` (default) | **non-blocking**: prints `N nodes stale (RN-…, US-…) → chronicle update --codes …` and lets the commit through. The doc-fix is the human's call. |
| `block` | **fail-closed**: stops the commit until the stale nodes are updated (or explicitly waived). |
| `sync` | triggers a **headless delta sync** — builds `chronicle.run: { mode: update, scope: { change_diff, codes } }` from the staleness output and invokes chronicle (the post-apply adapter path). Auto-keeps the KB fresh. |

```json
{ "on_stale": "nudge", "block_on_broken_ref": true, "watch_paths": ["src/"] }
```

Defaults: `nudge` (visible but never in your way). Nobody is forced onto PRs or blocking gates — the watch is a capability; the surface (pre-commit / pre-push / CI / none) and the strictness are the user's choice. The hook burns **zero tokens** (mechanical); only `on_stale: sync` spends the LLM, and only on the nodes that actually drifted.

## The LLM level (separate, never a gate)

Correctness verification (`verification.md`) and auto-update run **on-demand or on a schedule** — for example, a nightly headless agent that audits in depth and opens an issue/PR with findings. Never as a synchronous blocking check, because it costs tokens and is non-deterministic.
