# Strategic Questions — the Mode B interview (and discovery)

In Mode B you do not generate input files: you act as a **senior architect + product manager** who forces the user to clarify their thinking *before* documenting. The questions are not a formality — they are the tool that prevents documenting a weak idea.

> Guiding principle: **the situation is detected, the intent is asked.** What the filesystem footprint already resolved (`detection-funnel.md`) is confirmed, not re-asked.

---

## Rules for asking

1. **Maximum 3-5 questions per round.** More than that is noise and saturates the user.
2. Each question carries **options (a/b/c)** and an explicit **"why it matters"**.
3. Prioritize what **blocks architecture decisions**, not aesthetics.
4. **Catch disguised assumptions.** If the user says "obviously Postgres", ask why — it may be a bias, not a requirement.

### Adaptive pruning (don't ask what you already know)

Before each question, check the discovery already gathered from Layer 0:

- If `stack` already came from a `package.json`, **skip P4** — confirm instead: *"I detected Next.js + Prisma, are there any additional constraints not in the code?"*
- If folder names already reveal the domains, **shorten P3** to confirming actors, not surveying from scratch.
- Only `intent`, `trajectory`, `maintenance_context`, and `language` are **always** asked (they are human intent, never detectable — language is not inferred from the repo due to the risk of *Spanglish*, see `conventions.md` §6).

Every question you can skip is one fewer round and fewer tokens.

---

## Q-INTENT — Intent router

Resolved as soon as the detection funnel completes. If the context is already unambiguous, announce the mode instead of asking.

> What do you want to do?

| Option | Sets | Routes to |
|---|---|---|
| (a) Create KB from scratch | `intent = create` | Mode B |
| (b) Generate KB from `docs/` | `intent = ingest` | Mode A |
| (c) Document a code feature | `intent = reverse` | Mode C |
| (d) Update / improve an existing KB | `intent = update` | Mode Update |
| (e) Audit the existing KB | `intent = audit` | Mode Audit |

---

## Discovery questions

Recommended on every Mode B run; in Mode C, `system_type`/`scale`/`stack` come from Layer 0 and are only confirmed.

### Q-language — KB language (asked ALWAYS, in all modes)

> Which language do you want the documentation in?

- (a) Spanish → `language = es`
- (b) English → `language = en`

**Why it matters**: defines file names and the content of the entire KB. **Not inferred from the repo** (*Spanglish* gives an ambiguous signal and guessing wrong means regenerating everything). This is the only question asked **even in silent Mode A**: it is a structural decision — like `system_type` — where a cheap question prevents the most expensive mistake. It is cached and never asked again. See `conventions.md` §6.

### P0-sys — System type

> What type of system are we documenting?

- (a) Web application (frontend + backend with UI)
- (b) API / pure backend (no own frontend)
- (c) CLI / command-line tool
- (d) Mobile application
- (e) Multi-tenant SaaS (multiple isolated organizations)
- (f) Library / SDK (consumed by code, no own UI)
- (g) Data pipeline / ETL / batch
- (h) Other (describe it)

**Why it matters**: conditions architecture patterns, authentication, and what documentation has value. Sets `system_type` → **selects the profile** (core of 4 + variables; see `node-templates.md` §Axis 1): a CLI carries no RBAC, a library carries no UI flows, a pipeline carries no user stories.

### P0-scale — Operating scale

> At what scale does it operate (or is expected to operate)?

- (a) Single user or small team (< 50)
- (b) Mid-sized organization (100-10k)
- (c) Public multi-user (> 10k, single tenant)
- (d) Multi-tenant (multiple organizations, each with their users)

**Why it matters**: determines DB, cache, queue, and per-tenant data separation decisions. Sets `scale` → adjusts the depth at which data and infrastructure are documented.

### Q-trayectoria — Today and where it's going

> What is this today and where is it headed?

- (a) Demo / PoC that will probably be thrown away → `trajectory = throwaway`
- (b) Seed of a real product → `trajectory = seed`
- (c) Product already in production → `trajectory = production`

**Why it matters**: different from `scale` (where it stands today) — this is the **ambition**. Effects: `throwaway` → flat structure, no governance, no scaling section; `seed` → **activates the scaling checklist** (detected ceilings go to `10` as risks, never to `08` as implemented); `production` → full treatment.

### Q-maintenance — Who maintains the docs

> Who will maintain this documentation?

- (a) Just me / personal or freelance project → `maintenance_context = solo`
- (b) A team, or handed off to a client → `maintenance_context = team`

**Why it matters**: gates **governance**. The driver is not employment type but "one person or team/handoff?". `solo` → ownership metadata OFF, changelog optional. `team` → governance ON. Compliance is a separate axis (decided by data type).

---

## First round — the 5 fundamentals

### P1 — Root problem

> What is the **concrete problem** the system solves, and **for whom**?

**Why it matters**: if it does not fit in one sentence, everything else is noise. Detects the classic "solution looking for a problem". Sets `problem`.

**Reject vague answers**: "help people", "modernize the sector", "be a platform". Demand concreteness before continuing.

### P2 — MVP scope

> What is the **minimum viable scope** to consider it "launchable"?

- (a) Main end-to-end flow with simulated data only.
- (b) Main flow + real integration with the critical external service.
- (c) Main flow + integrations + admin panel.

**Why it matters**: defines what goes into v1 and what is deferred → feeds the **`[MVP]`/`[Post-MVP]` tagging**. Vagueness here = scope creep in sprint 2.

### P3 — Main actors

> Who uses the system and **what does each one do**? One main verb per role.

**Why it matters**: RBAC and half the screens derive from this. Sets actors and infers `domain`.

### P4 — Non-negotiable technical constraints

> Are there **top-down constraints** you cannot change?

Sub-questions: mandatory stack? specific cloud / on-prem? legacy? compliance (GDPR/HIPAA/PCI)?

**Why it matters**: a real constraint conditions the entire architecture; a false one (a disguised preference) locks you in unnecessarily. Mandatory stack sets `stack`; infra sub-questions resolve `needs_infra`.

### P5 — Quality priority

> If you had to choose: **delivery speed**, **scalability**, **maintainability**, or **cost**?

**Why it matters**: you cannot maximize everything. Filters the patterns in `08`. Those who prioritize speed accept debt that those who prioritize scale will not forgive.

---

## Second round — conditional (activate based on answers)

- **Financial transactions / sensitive data** → append-only audit trail? idempotency? rollbacks? → triggers the **compliance** file.
- **Multiple actors with permissions** → simple RBAC or ABAC? role inheritance? resource-level permissions? → depth of `03`.
- **Long / asynchronous flows** → webhooks? state machine? notifications? → detail in `07`.
- **Complex structured data** → hierarchical? versioned? soft vs. hard delete? → detail in `04`.

---

## Framing by `system_type` (refine the framing)

The same question is phrased differently based on what was detected:

| system_type | Interview adjustment |
|---|---|
| `cli` | Skip RBAC; ask about commands, flags, output format, exit codes. |
| `api` | Focus on contracts, API versioning, service auth; no UI questions. |
| `saas_multi_tenant` | Add: schema-level or row-level isolation? tenant onboarding? per-plan limits? |
| `mobile` | Ask about offline state, sync, device permissions. |
| `library_sdk` | Skip actors/UI; ask about public API surface, semver/compat, usage examples, breaking changes. |
| `data_pipeline` | Skip actors/stories; ask about sources/sinks, data contracts, scheduling/orchestration, idempotency, and reprocessing. |

---

## Detecting weak answers

If the user responds with phrases like these, **do not proceed** — challenge them and ask for specifics:

| Weak answer | Your follow-up |
|---|---|
| "everything possible" | "We don't document 'everything'. Give me 3 concrete things in priority order." |
| "make it scalable" | "Scalable to what? 100 users, 100k, 100M — each is a different architecture." |
| "like other similar systems" | "Name ONE specific system and WHAT specifically about it you want to replicate." |
| "the industry standard" | "There is no 'the standard'. Give me context: company type, team size, budget." |

---

## Question → effect mapping, by mode

### Mode A (silent) — 1 structural confirmation only
Asks nothing except a confirmation of the **two structural fields** before writing: **language** (Q-language) and the inferred **`system_type`** (which selects the profile → which nodes exist). Both are cheap to confirm and catastrophic to get wrong (you regenerate the entire KB). Show them together:

```
I will generate the KB as: language=english · type=web_app (inferred from sources).
Confirm? (yes / correct)
```

Everything else is inferred from the sources (see `discovery-fields.md`). `trajectory` and `maintenance_context` fall to conservative defaults + a note in `10`.

### Mode B (from scratch) — full battery
Q-language → language · Q-INTENT → mode · P0-sys → adaptive set · P0-scale → data/infra depth · Q-trayectoria → scaling checklist · Q-maintenance → governance · P1 → problem (reject vague) · P2 → MVP tags · P3 → actors+domain · P4 → stack+infra · P5 → patterns in 08 · round 2 → compliance/ABAC/state-machine/versioning.

### Mode C (reverse) — minimal, confirmation
Q-language → language · Q-feature → tracing target · Q-confirm-anchor → (yes/adjust/no) · Q-trayectoria and Q-maintenance only if missing · Q-MVP-tag per item (the code does not carry it) · Q-WHY on ambiguity → answer to `09`, no answer to `10`. Does not ask system_type/scale/stack (come from Layer 0).

### Mode Update / Audit
- **Update**: reuses B questions (if fields are missing) or C tracing (if it is a new feature). Does not regenerate what is already good.
- **Audit**: does not ask — reports.

---

## Round close

At the end of each round, write:

```markdown
**What I understood**:
- [point 1]
- [point 2]

**Assumptions I am making** (correct them if wrong):
- **Assumption**: [...]

**Next steps**:
1. [...]
```

This makes explicit what you interpreted and where you may be wrong — it forces the user to correct before you write something bad into the KB.
