# Node templates — non-web profile variants (lazy-loaded)

Loaded **only** when `system_type` ∈ {`cli`, `library_sdk`, `data_pipeline`} (token economy: `web_app`/`api`/`mobile`/`saas_multi_tenant` never load this). It complements `node-templates.md` (core taxonomy + base `web_app` templates + filename pin + file↔folder rules), which is always loaded in write modes.

When the profile (`node-templates.md` §Axis 1) reframes a slot, **use the variant below instead of the base template** — same slot number, different form. Slots not listed for a profile use the base template; slots marked ✗ in the profile table are omitted. **Provenance is equally mandatory** (citation per item). Filenames stay pinned per slot (`node-templates.md` §Canonical filenames) — the variant changes the *content*, never the filename.

### `library_sdk`

- **04 · Public API surface** *(collection)* — replaces "data model". Per exported symbol:
  ```markdown
  ## `exportedFunction(args)` → ReturnType   `[code · src/index.ts#exportedFunction]`
  - **Signature**: parameters (type, optional/required), return, throws.
  - **Stability**: `stable` | `beta` | `deprecated` (+ since which version).
  - **Minimal example**: usage snippet.
  ```
  **Checklist**: every public symbol with signature · stability/semver · example · citation.
- **06 · Usage recipes** *(collection)* — replaces user stories. Per use case: goal, end-to-end snippet, notes/gotchas. `[code · …]`
- **07 · Call sequences** — the expected order of calls for a typical case (init → configure → use → release), with sequence diagram if applicable.
- **03 actors** and **07 UI flows**: ✗ (omit; consumers are not RBAC actors).

### `cli`

- **04 · Config/IO schema** — replaces entities: config files, env vars, input and output format (stdin/stdout/files), exit codes. `[code · …]`
- **06 · Commands** *(collection)* — replaces stories. Per command:
  ```markdown
  ## `my-cli <command> [flags]`   `[code · src/commands/cmd.ts#run]`
  - **Synopsis**: what it does in one sentence.
  - **Flags**: `--flag` (type, default, effect).
  - **Examples**: invocation → expected output.
  - **Exit codes**: 0 ok · N error.
  ```
- **07 · Execution flow** — from arg parsing to output/exit code.
- **03 RBAC**: ✗ (the caller is the user; there are no roles).

### `data_pipeline`

- **04 · Data contracts** *(collection)* — replaces entities. Per dataset/stream: schema (fields + types), format, source/sink, partitioning, SLA/freshness. `[code · …]`
- **06 · Stages / Jobs** *(collection)* — replaces stories. Per stage: input, transformation, output, idempotency/reprocessing. `[code · …]`
- **07 · DAG / lineage** — the dependency graph between stages + data lineage:
  ```markdown
  ## Pipeline DAG
  ```mermaid
  flowchart LR
      Ingesta --> Limpieza --> Enriquecido --> Carga
  ```
  - **Dependencies**: which stage waits for which.
  - **Lineage**: which source each output field comes from. `[code · …]`
  ```
- **03 actors** and **06 UI stories**: ✗ (operators/upstreams, not RBAC actors).

> `api`, `mobile` and `saas_multi_tenant` use the base templates with the profile table adjustments (emphasis on contracts, offline/sync, tenancy) — they don't need a full form variant, so they never load this file.
