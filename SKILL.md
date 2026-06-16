---
name: chronicle
description: >
  Builds and maintains a structured project knowledge base of 10 canonical nodes (files or folders) at knowledge-base/ (project root). Five modes: generate from source docs (silent), build from scratch (interactive), reverse-document existing code by functionality (read-only), update/improve an existing KB (non-destructive merge), and audit an existing KB (consistency + completeness). Reads code but NEVER modifies it.
  Trigger: When user asks to create, build, generate, update, improve, or audit a knowledge base; document a project from source documents (.txt, .docx, .pdf) or from existing code; or asks to "armar base de conocimiento" / "crear KB" / "documentar proyecto" / "documentar funcionalidad" / "actualizar la KB".
license: Apache-2.0
metadata:
  author: Ezequiel González
  version: "2.0"
---

## Master rule (governs every mode)

> **El código se LEE pero NUNCA se modifica.** Esta skill es read-only sobre el código fuente. Jamás edita, escribe ni refactoriza código de la aplicación. Solo produce documentación en `knowledge-base/`.

> **El código dice el QUÉ, el usuario dice el PORQUÉ, y nada se inventa.**
> - El código revela qué hace el sistema (entidades, rutas, reglas implementadas).
> - La intención, el porqué de una decisión, el roadmap y la frontera MVP **no están en el código** — los aporta el usuario.
> - Toda ambigüedad o suposición que no pueda confirmarse va a `09_decisiones_y_supuestos.md` (si es una decisión inferida) o a `10_preguntas_abiertas.md` (si es una duda). **Nunca se documenta una suposición como si fuera un hecho.**

Esta regla decide el comportamiento en cada modo: la skill es **notario** cuando documenta lo que existe, y solo se vuelve **consultor** cuando todavía no hay nada construido (Mode B).

---

## When to Use

- Generar una base de conocimiento estructurada y navegable para un proyecto.
- Convertir documentos monolíticos (`.txt`, `.docx`, `.pdf`, `.md` largos) en una KB temática.
- Documentar un sistema **desde cero** acompañando al usuario como socio estratégico.
- Documentar **una funcionalidad de un sistema ya construido** leyendo el código (read-only).
- **Actualizar o mejorar** una KB existente sin destruir trabajo previo.
- **Auditar** una KB existente: consistencia cruzada, drift interno y completitud.

**Don't use when:**
- El usuario pide modificar, refactorizar o escribir **código** — esta skill nunca toca código.
- El usuario pide UN documento aislado sin relación con la KB canónica.

---

## Step 0 — Detection funnel + intent router (corre SIEMPRE primero)

Antes de elegir modo o leer código fuente, ejecutá el **embudo de detección de 3 capas** (ver `assets/detection-funnel.md`). En resumen:

1. **Capa 0 — huella del filesystem (casi 0 tokens, sin leer código fuente)**: detectá stack vía manifests (`package.json`, `go.mod`, `pyproject.toml`, etc. — tabla en el asset), dominios vía nombres de carpetas, modo vía existencia de `docs/` y `knowledge-base/`, y tamaño vía conteo de archivos.
2. **Capa 1 — confirmar + preguntar solo los huecos**: mostrá lo detectado y hacé únicamente las preguntas que el filesystem no puede responder.
3. **Capa 2 — lectura profunda acotada**: solo en Mode C, y solo de la funcionalidad pedida.

Luego resolvé la **intención** (la situación se detecta; la intención se pregunta):

**Q-INTENT — ¿Qué querés hacer?**
| Opción | Modo |
|---|---|
| (a) Crear KB desde cero | **Mode B** |
| (b) Generar KB desde `docs/` | **Mode A** |
| (c) Documentar una funcionalidad del código | **Mode C** |
| (d) Actualizar / mejorar una KB existente | **Mode Update** |
| (e) Auditar la KB existente | **Mode Audit** |

La Capa 0 **propone** el modo; Q-INTENT lo **confirma**. Si el contexto ya es inequívoco (p. ej. `docs/` con fuentes y sin KB → Mode A), podés saltar la pregunta y anunciar el modo elegido.

---

## Operating Modes

### Mode A — From existing source docs (silent)

**Trigger**: `docs/` existe y contiene fuentes (`.txt`, `.docx`, `.pdf`, o `.md` distintos a un README), y el usuario no pidió otra cosa.

**Comportamiento**: leés todas las fuentes desde `docs/`, analizás, y generás la KB canónica completa en `knowledge-base/` **sin hacer preguntas**. Fire-and-forget. Los campos de discovery se **infieren** de las fuentes; los no inferibles (`trajectory`, `maintenance_context`) caen en defaults conservadores + nota en `10_preguntas_abiertas.md`. Ver `assets/discovery-fields.md`.

### Mode B — From scratch (interactive)

**Trigger**: no hay `docs/` con fuentes ni `knowledge-base/`, o el usuario dice "armemos desde cero".

**Comportamiento**: actuás como **arquitecto senior + product manager**. Corrés la batería de preguntas estratégicas (`assets/interview-guide.md`), proponés enfoques con pros/contras, e iterás nodo por nodo con validación. Es el único modo donde la skill **aconseja** (escalado, stack, patrones), porque el sistema todavía no existe.

### Mode C — Reverse-documentation by functionality (read-only)

**Trigger**: existe código pero no documentación, y el usuario pide documentar una funcionalidad ("documentá el checkout").

**Comportamiento**: leés el código en modo **read-only**, scopeado **por funcionalidad** (un corte vertical que cruza carpetas), y producís/actualizás los nodos correspondientes. Protocolo completo en `assets/reverse-documentation.md`: **anclaje → confirmación → trazado acotado → merge**. Documentás el QUÉ desde el código; el PORQUÉ lo pregunta o va al `10`.

### Mode Update — Improve an existing KB (non-destructive merge)

**Trigger**: `knowledge-base/` ya existe y el usuario pide actualizar/mejorar.

**Comportamiento**: leés la KB existente, respetás lo que está bien, completás huecos y marcás lo cambiado — **merge no destructivo**, nunca regeneración total. Incluye la **promoción dinámica** de nodos archivo→carpeta cuando crecen (ver `assets/node-templates.md`). Reusá las preguntas de Mode B o el trazado de Mode C según qué falte.

### Mode Audit — Validate an existing KB

**Trigger**: el usuario pide auditar/revisar la KB.

**Comportamiento**: **no genera contenido nuevo**, reporta. Chequea consistencia cruzada (códigos `RN`/`US`/`DD` que se referencian existen), drift interno entre documentos (contradicciones), y un **completeness score** por nodo. Devuelve un reporte priorizado.

---

## Critical Patterns

### Output location (todos los modos)
Todos los archivos de la KB van a `knowledge-base/` en la **raíz del proyecto**. **NUNCA** mezclar con `docs/` (que contiene los documentos fuente de Mode A).

### Canonical nodes (10 obligatorios — archivo o carpeta)

La KB **DEBE** contener estos 10 nodos canónicos. Cada nodo es un **archivo `.md`** o, si su contenido es una colección que crece, una **carpeta** con el mismo prefijo numérico (decisión condicional por tamaño — ver `assets/node-templates.md`).

| # | Nodo | Tipo | Contenido |
|---|------|------|-----------|
| 01 | `01_vision_y_objetivos.md` | mapa (archivo) | Propósito, objetivos por actor, alcance, fuera de alcance |
| 02 | `02_descripcion_general.md` | mapa (archivo) | Stack (estructurado por capa/servicio), arquitectura, integraciones |
| 03 | `03_actores_y_roles.md` | mapa (archivo) | Actores, matriz RBAC, permisos, rutas públicas |
| 04 | `04_modelo_de_datos.md` *o* `04_modelos-apis/` | **colección** | Entidades, ERD, relaciones + contratos de API |
| 05 | `05_reglas_de_negocio.md` *o* `05_reglas-de-negocio/` | **colección** | Reglas por dominio (códigos `RN-XX`) |
| 06 | `06_funcionalidades.md` *o* `06_funcionalidades/` | **colección** | Historias de usuario por épica |
| 07 | `07_flujos_principales.md` *o* `07_flujos-principales/` | **colección** | Flujos extremo a extremo |
| 08 | `08_arquitectura_propuesta.md` | mapa (archivo) | Patrones, estructura, seguridad, env vars |
| 09 | `09_decisiones_y_supuestos.md` *o* `09_decisiones/` | **colección (ADR)** | Decisiones (un archivo por decisión) + supuestos |
| 10 | `10_preguntas_abiertas.md` | backlog (archivo) | Inconsistencias + preguntas abiertas priorizadas |

Más un `README.md` índice en `knowledge-base/README.md`.

**Mapas vs colecciones**: los **mapas** (01, 02, 03, 08, 10) se leen enteros para tener la foto completa → archivo único. Las **colecciones** (04, 05, 06, 07, 09) son listas de unidades discretas que crecen y se navegan por unidad → se explotan en carpeta cuando cruzan el umbral. Ver `assets/node-templates.md`.

### Optional extras (permitidos)
Archivos extra con prefijo `1X_`/`2X_` y nombre kebab-case complementan los 10 canónicos, nunca los reemplazan. Ejemplos: `11_pagos_mercadopago.md`, `12_seguridad_compliance.md`, `13_glosario.md`.

### Tono según modo
- **Mode A / C / Update / Audit** (documentando lo que existe): eficiente, factual, **notario**. No prescribe arquitectura sobre lo ya construido.
- **Mode B** (desde cero): **consultor**. Cuestiona decisiones débiles, marca supuestos con `**Suposición:**`, propone alternativas, detecta riesgos.

---

## Asset loading map (token discipline)

**No cargues los assets de golpe.** El embudo de detección corre siempre; el resto de los assets se leen **solo cuando el modo activo los necesita**. Nunca se necesitan todos a la vez.

| Paso / Modo | Assets a cargar | NO cargar |
|---|---|---|
| Step 0 (siempre) | `detection-funnel.md` | el resto |
| Mode A (ingest) | `node-templates.md`, `discovery-fields.md`, `quality-rubric.md` | interview-guide, reverse-documentation, lifecycle |
| Mode B (scratch) | `interview-guide.md`, `node-templates.md`, `conventions.md` | reverse-documentation, lifecycle |
| Mode C (reverse) | `reverse-documentation.md`, `node-templates.md` | interview-guide (salvo Q-WHY) |
| Mode Update | `lifecycle.md`, `node-templates.md` | interview-guide, reverse-documentation |
| Mode Audit | `lifecycle.md`, `quality-rubric.md` | el resto |
| Bordes / dudas | `edge-cases.md` | — |
| Ejemplos (few-shot) | `examples.md` (solo la sección del modo activo) | otras secciones |

`conventions.md` (Mermaid, tagging, idioma, compliance) se consulta puntualmente cuando aplica, no entero.

---

## Resources

- **Detection funnel**: [assets/detection-funnel.md](assets/detection-funnel.md) — 3 capas + tabla manifest→stack.
- **Canonical templates**: [assets/node-templates.md](assets/node-templates.md) — estructura de los 10 nodos, regla archivo↔carpeta, promoción dinámica.
- **Strategic questions**: [assets/interview-guide.md](assets/interview-guide.md) — banco de preguntas (Mode B) + discovery + mapeo pregunta→efecto por modo.
- **Reverse documentation**: [assets/reverse-documentation.md](assets/reverse-documentation.md) — protocolo del Mode C (read-only por funcionalidad).
- **Lifecycle**: [assets/lifecycle.md](assets/lifecycle.md) — Mode Update (merge no destructivo + promoción), gobernanza condicional, Mode Audit.
- **Conventions**: [assets/conventions.md](assets/conventions.md) — Mermaid, tagging MVP/Post-MVP, set canónico adaptativo por `system_type`, compliance condicional, glosario, flag de idioma.
- **Discovery fields**: [assets/discovery-fields.md](assets/discovery-fields.md) — el modelo de discovery (estado interno), inferencia Mode A, regla de baja confianza.
- **Examples**: [assets/examples.md](assets/examples.md) — un ejemplo end-to-end por modo (few-shot). Cargá solo la sección del modo activo.
- **Quality rubric**: [assets/quality-rubric.md](assets/quality-rubric.md) — criterios del completeness score por nodo (Mode Audit y auto-chequeo).
- **Edge cases**: [assets/edge-cases.md](assets/edge-cases.md) — bordes de detección, conflictos, y el auto-chequeo final antes de cerrar.
