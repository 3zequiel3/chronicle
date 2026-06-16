# Lifecycle — Update, Governance & Audit

Cubre el mantenimiento de una KB que ya existe: el merge no destructivo (Mode Update), la gobernanza condicional, y la validación (Mode Audit).

---

## 1. Mode Update — merge no destructivo

Se dispara cuando `knowledge-base/` ya existe y el usuario pide actualizar/mejorar. **Nunca regenera la KB entera.**

### Algoritmo
1. Leé la KB existente (los nodos afectados, no todo si es scopeado a una feature).
2. **Respetá lo que está bien** — no reescribas contenido válido por gusto.
3. **Completá huecos** — agregá lo que falta.
4. **Marcá lo cambiado** — dejá rastro de qué se tocó (ver changelog, §2).
5. Si el cambio es por funcionalidad, reusá el trazado de Mode C (`reverse-documentation.md`); si es por campos discovery faltantes, reusá las preguntas de Mode B.

### Promoción de nodos
Si el update hace que una colección-archivo cruce su umbral (ver `node-templates.md` §Regla archivo↔carpeta), la skill **promueve el nodo a carpeta**: crea `0X_<nombre>/`, reparte el contenido por unidad, escribe el `README` con el mapa, y **actualiza todas las referencias cruzadas** a las rutas nuevas. Refactor de documentación, jamás de código.

### Regla de oro del merge
No destruir. Ante la duda entre pisar y conservar, conservá y marcá la divergencia como pregunta en `10_preguntas_abiertas.md`.

---

## 2. Gobernanza condicional (gate: `maintenance_context`)

La metadata de gobernanza solo tiene sentido cuando la doc la mantiene **más de una persona o hay handoff**. Gateada por `maintenance_context` (ver `interview-guide.md` §Q-maintenance):

| Elemento | `solo` | `team` |
|---|---|---|
| `owner` por nodo | ❌ off | ✅ on |
| `last-reviewed` (fecha) | ❌ off | ✅ on |
| `review-cadence` | ❌ off | ✅ on |
| Changelog de la KB | opcional | ✅ on |

Cuando está **on**, cada nodo lleva un bloque de metadata al inicio:

```markdown
> **Owner**: @equipo-pagos · **Last reviewed**: 2026-06-16 · **Cadence**: trimestral
```

### Changelog de la KB
Archivo `knowledge-base/CHANGELOG.md` que registra qué cambió entre regeneraciones/updates:

```markdown
## 2026-06-16
- [Update] 05_reglas-de-negocio/pagos.md — +3 reglas (RN-PAGOS-09..11) desde feature checkout.
- [Promote] 04 modelo de datos: archivo → carpeta (12 entidades).
```

> **Compliance es otro eje**: el archivo de seguridad/compliance NO lo gatea `maintenance_context`, lo gatea el **tipo de dato** (PII, pagos). Un freelance con un sistema de pagos igual lo necesita. Ver `node-templates`/SKILL §extras.

---

## 3. Mode Audit — validar sin generar

No produce contenido nuevo: **reporta**. Tres chequeos, todos documentales (no leen código salvo que el usuario lo pida explícito como cross-check):

### 3.1 Consistencia cruzada
Verifica que los códigos referenciados existan y resuelvan:
- toda `RN-XX-NN` citada en `06`/`07` existe en `05`,
- toda `US-NNN` enlazada resuelve a una historia en `06`,
- toda `DD-NN` referenciada existe en `09`,
- los enlaces a entidades (`04_modelos-apis/modelos/*.md`) resuelven a archivos reales.

### 3.2 Drift interno entre documentos
Detecta **contradicciones internas** entre nodos (sin mirar código):
- "el `04` declara 8 entidades pero el `02` menciona 11",
- "el `06` usa un actor que el `03` no define",
- "un flujo del `07` referencia una regla que no está en el `05`".

### 3.3 Completeness score por nodo
Reporta cobertura por nodo contra su template (`node-templates.md`):

```markdown
| Nodo | Score | Faltante |
|---|---|---|
| 05 reglas | 60% | dominios sin códigos RN; falta "excepciones globales" |
| 07 flujos | 40% | faltan casos de error en 3 de 5 flujos |
```

### Salida del Audit
Un reporte priorizado (Alta/Media/Baja) con hallazgos accionables. No modifica la KB salvo que el usuario pida pasar a Mode Update con esos hallazgos.
