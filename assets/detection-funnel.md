# Detection Funnel — Cheap and precise startup (3 layers)

The skill's startup is what determines whether it's expensive or cheap. The rule: **the filesystem tells you WHAT-exists (detected); the user tells you WHAT-you-want (asked).** Never try to infer intent by reading code — it's impossible and prohibitively expensive.

The three layers go from cheapest to most expensive. Don't move up a layer until you've exhausted the previous one.

---

## Layer 0 — Filesystem footprint (near 0 tokens, WITHOUT reading source code)

Before asking anything and before opening a single source file, scan the structure.

### Stack via manifests (detection by SIGNAL, not by reading)

A single read of a small, dense file resolves the full stack. Reading source files to "guess" the technology is wasting tokens.

| Signal (file) | Tells you |
|---|---|
| `package.json` | Node/TS + framework (react, next, express, nest…) + libs in `dependencies` |
| `tsconfig.json` | TypeScript |
| `go.mod` | Go + modules and version |
| `requirements.txt` / `pyproject.toml` / `Pipfile` | Python + deps |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` | Java / Kotlin |
| `composer.json` | PHP (+ Laravel/Symfony via deps) |
| `Gemfile` | Ruby (+ Rails) |
| `*.csproj` / `*.sln` | .NET / C# |
| `pubspec.yaml` | Dart / Flutter |
| `docker-compose.yml` / `Dockerfile` | infra, services, `needs_infra = true` |
| `prisma/schema.prisma` / `*.sql` / migrations | DB + data model (input for node 04 — **extract, don't narrate**: see `reverse-documentation.md`) |
| `openapi.*` / `swagger.*` | API contracts (input for node 04 — **extract, don't narrate**) |
| `*.mmd` / `*.puml` / `*.dot` / `*.svg` / `*.drawio` / fenced `mermaid`/`plantuml` in `docs/` | **text/markup diagrams** (incl. SVG/drawio = XML) — input for nodes 04 (ERD), 07 (sequence), 08 (architecture); see `conventions.md` §1. Raster images (`.png`/`.jpg`) only if the host has vision, as low-confidence → node 10. |

> **Read only the dependencies section** of the manifest — not the whole file. A manifest is a signal to scan, not a document to ingest; pulling the full file into context is a token leak (`SKILL.md` §Token economy).

### Other structural signals (free)

| Signal | Tells you |
|---|---|
| Folder names (`pagos/`, `stock/`, `auth/`) | Candidate system domains |
| Presence of `docs/` with sources | Candidate for **Mode A** |
| Presence of `knowledge-base/` | Candidate for **Mode Update / Audit** |
| Absence of both + code present | Candidate for **Mode C** |
| Absence of everything | Candidate for **Mode B** |
| File count / approximate LOC | **Size** signal → feeds the file↔folder threshold and the demo-vs-large question |

**Layer 0 output**: stack (structured by layer), domains, proposed mode, size — all **without reading source code**.

---

## Layer 1 — Confirm + ask ONLY the gaps

Show what was detected and ask for confirmation. Example:

```
Detected: Next.js + Prisma + Postgres. Monorepo with modules pagos/ and stock/.
~18 entities. No docs/ or knowledge-base/. Is this correct?
```

Then ask **only** the questions no file can answer (pure human knowledge): **KB language** (Q-language — not inferred from the repo due to *Spanglish*), intent, trajectory, maintenance, MVP boundary, and the root problem. Everything Layer 0 already resolved (`system_type`, `scale`, `stack`, `domain`) is **confirmed**, not asked.

The detail of each question and its effect per mode is in [`interview-guide.md`](interview-guide.md).

> **Non-invention**: confirming an inference with the user is NOT optional for fields that affect structure (`system_type`, `scale`). An unconfirmed inference that changes the KB is marked as `**Assumption:**` and, if the user is unavailable, goes to `10_preguntas_abiertas.md`.

---

## Layer 2 — Deep, bounded reading

Reading actual source code happens **only in Mode C**, and only for the **specific functionality** the user asked to document, following the bounded tracing from [`reverse-documentation.md`](reverse-documentation.md). **Never** "read everything to understand".

This is what makes documenting a giant project cost nearly the same as a small one: you never read the giant in full, you read its cheap footprint (Layer 0) and then only the slice you're asked for (Layer 2).

---

## Funnel summary

```
Layer 0 (manifests + structure, free)
   → Layer 1 (confirm detected + ask only human gaps)
      → Layer 2 (deep reading ONLY of the requested feature, only in Mode C)
```
