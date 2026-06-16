# Discovery Fields — the model that guides each run

chronicle establishes a handful of **project facts** at startup (the discovery) and uses them throughout the run to decide how it behaves: which nodes to generate, whether to enable governance, whether to activate the scaling checklist, etc.

> This is **internal run state**, not written to any external file. chronicle is standalone: it reasons with these fields in memory and reflects them in the KB it produces.

---

## The field set

| Field | What it represents | How it is obtained | What it triggers |
|---|---|---|---|
| `intent` | The requested operation | asked (Q-INTENT) | Selects the mode (create/ingest/reverse/update/audit) |
| `system_type` | System type | detected (Layer 0) / asked (P0-sys) | Selects the **profile** (core of 4 + variables 03-08) — see `node-templates.md` §Axis 1 |
| `scale` | Current scale | detected / asked (P0-scale) | Depth of data/cache/tenancy |
| `domain` | Business domain | detected / inferred | Naming, domain grouping |
| `trajectory` | Ambition (today → future) | asked (Q-trayectoria) | Scaling checklist |
| `maintenance_context` | Who maintains the docs | asked (Q-maintenance) | Governance gate |
| `stack` | Technologies per layer | detected (manifests) | Stack table, cross-language tracing |
| `needs_infra` | Non-trivial infra present? | detected / inferred | Infra/deployment extras |
| `language` | KB language | **asked** (Q-language) | File names and content of the entire KB |

### Two natures

- **Detectable / inferable**: `system_type`, `scale`, `domain`, `stack`, `needs_infra`. Come from the filesystem footprint (`detection-funnel.md`) or from the sources. They are **confirmed**, not asked from scratch.
- **Human intent**: `intent`, `trajectory`, `maintenance_context`, `language`. **Not** in the code or docs — they are **asked**. Never invented. (`language` is not inferred from the repo due to the risk of *Spanglish*: a wrong guess = regenerate the entire KB.)

---

## Inference in Mode A (silent, asks only for language)

Mode A is fire-and-forget except for Q-language (see below). Detectable/inferable fields are drawn from the sources:

| Field | Infer from | Signal |
|---|---|---|
| `problem` | the generated vision | the first declarative sentence about what the system solves |
| `system_type` | description/architecture | "web app", "REST API", "CLI", "mobile", "SaaS", "multi-tenant", "library/SDK", "pipeline/ETL" |
| `domain` | actors + features | actor names and feature grouping (ecommerce → products/cart; fintech → transactions) |
| `scale` | actors + scale mentions/RBAC | actor count, RBAC complexity, scale keywords |
| `stack` | general description | frameworks, languages, DB, external services |
| `needs_infra` | description + architecture | `true` if Docker, DB, Redis, queues, cron, or deployment infra are present |

### Low-confidence rule

**Never assign a value with apparent certainty if you do not have it.** When a field cannot be inferred with reasonable confidence:

1. Set the best-effort value marked as uncertain (e.g. `"web_app (inferred, low confidence)"`).
2. Record it in `10_preguntas_abiertas.md`:
   ```
   [DISCOVERY] Could not infer `<field>` with confidence from the sources.
   Confirm: <what needs to be known>.
   ```
3. Continue — never block Mode A over a single uncertain field.

### Human-intent fields in Mode A

`trajectory` and `maintenance_context` are **not** inferable from docs (they are product/team intent, not content). Mode A sets them to **conservative defaults** — `trajectory` unset (no scaling checklist) and `maintenance_context = solo` (governance OFF) — and leaves a `[DISCOVERY]` note in `10_preguntas_abiertas.md` for the user to confirm. Never guesses them.

`language` and `system_type` are the **exception**: even though Mode A is silent, both are **confirmed** in a single step before generating. Language is asked (Q-language); `system_type` is **inferred from sources but confirmed** because it now **selects the profile** (which nodes exist) — inferring it wrong generates the wrong node set silently. Both are structural: getting them wrong forces a full KB regeneration, which is why they are never left as defaults or assumed. See `interview-guide.md` §Mode A and `conventions.md` §6.
