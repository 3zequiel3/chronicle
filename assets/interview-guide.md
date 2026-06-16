# Strategic Questions — el interrogatorio de Mode B (y el discovery)

En Mode B no generás archivos de entrada: actuás como **arquitecto senior + product manager** que obliga al usuario a clarificar su pensamiento *antes* de documentar. Las preguntas no son un trámite — son la herramienta que evita documentar una idea floja.

> Principio rector: **la situación se detecta, la intención se pregunta.** Lo que la huella del filesystem ya resolvió (`detection-funnel.md`) se confirma, no se vuelve a preguntar.

---

## Reglas para preguntar

1. **Máximo 3-5 preguntas por ronda.** Más que eso es ruido y el usuario se satura.
2. Cada pregunta lleva **opciones (a/b/c)** y un **"por qué importa"** explícito.
3. Priorizá lo que **bloquea decisiones de arquitectura**, no lo estético.
4. **Cazá los supuestos disfrazados.** Si el usuario dice "obvio que va con Postgres", preguntá por qué — puede ser un sesgo, no un requisito.

### Poda adaptativa (no preguntes lo que ya sabés)

Antes de cada pregunta, chequeá el discovery que ya tenés de la Capa 0:

- Si el `stack` ya salió de un `package.json`, **no preguntes P4** — confirmá: *"Detecté Next.js + Prisma, ¿hay alguna restricción más que no esté en el código?"*.
- Si los nombres de carpeta ya revelan los dominios, **acortá P3** a confirmar actores, no a relevarlos de cero.
- Solo `intent`, `trajectory`, `maintenance_context` y `language` se preguntan **siempre** (son intención humana, nunca detectables — el idioma no se infiere del repo por el riesgo de *espanglish*, ver `conventions.md` §6).

Cada pregunta que podés saltar es una ronda menos y tokens menos.

---

## Q-INTENT — Router de intención

Se resuelve apenas termina el embudo de detección. Si el contexto ya es inequívoco, anunciá el modo en vez de preguntar.

> ¿Qué querés hacer?

| Opción | Setea | Rutea a |
|---|---|---|
| (a) Crear KB desde cero | `intent = create` | Mode B |
| (b) Generar KB desde `docs/` | `intent = ingest` | Mode A |
| (c) Documentar una funcionalidad del código | `intent = reverse` | Mode C |
| (d) Actualizar / mejorar una KB existente | `intent = update` | Mode Update |
| (e) Auditar la KB existente | `intent = audit` | Mode Audit |

---

## Preguntas de discovery

Recomendadas en todo run de Mode B; en Mode C, `system_type`/`scale`/`stack` ya vienen de la Capa 0 y solo se confirman.

### Q-idioma — Idioma de la KB (se pregunta SIEMPRE, en todos los modos)

> ¿En qué idioma querés la documentación?

- (a) Español → `language = es`
- (b) English → `language = en`

**Por qué importa**: define nombres de archivo y contenido de toda la KB. **No se infiere del repo** (el *espanglish* da señal ambigua y errar = regenerar todo). Es la única pregunta que se hace **incluso en Mode A** silencioso, porque es estructural y barata. Se cachea y no se vuelve a preguntar. Ver `conventions.md` §6.

### P0-sys — Tipo de sistema

> ¿Qué tipo de sistema estamos documentando?

- (a) Aplicación web (frontend + backend con UI)
- (b) API / backend puro (sin frontend propio)
- (c) CLI / herramienta de línea de comandos
- (d) Aplicación móvil
- (e) SaaS multi-tenant (múltiples organizaciones aisladas)
- (f) Otro (describilo)

**Por qué importa**: condiciona patrones de arquitectura, autenticación y qué documentación tiene valor. Setea `system_type` → activa el **set canónico adaptativo** (un CLI no lleva RBAC; un SaaS suma tenancy).

### P0-scale — Escala de operación

> ¿A qué escala opera (o se espera que opere)?

- (a) Usuario único o equipo chico (< 50)
- (b) Organización mediana (100-10k)
- (c) Público multi-usuario (> 10k, un solo tenant)
- (d) Multi-tenant (varias organizaciones, cada una con sus usuarios)

**Por qué importa**: determina decisiones de DB, caché, colas y separación de datos por tenant. Setea `scale` → ajusta la profundidad con que se documentan datos e infraestructura.

### Q-trayectoria — Hoy y a dónde va

> ¿Qué es esto hoy y a dónde va?

- (a) Demo / PoC que probablemente se descarta → `trajectory = descartable`
- (b) Semilla de un producto real → `trajectory = semilla`
- (c) Producto ya en producción → `trajectory = produccion`

**Por qué importa**: es distinta de `scale` (dónde está hoy) — es la **ambición**. Efectos: `descartable` → estructura plana, sin governance, sin sección de escalado; `semilla` → **activa el checklist de escalado** (los techos detectados van al `10` como riesgos, jamás al `08` como implementados); `produccion` → tratamiento completo.

### Q-maintenance — Quién mantiene la doc

> ¿Quién va a mantener esta documentación?

- (a) Yo solo / proyecto personal o freelance → `maintenance_context = solo`
- (b) Un equipo, o se entrega a un cliente → `maintenance_context = team`

**Por qué importa**: gatea la **gobernanza**. El driver no es el tipo de empleo sino "¿una persona o equipo/handoff?". `solo` → metadata de ownership OFF, changelog opcional. `team` → governance ON. El compliance es un eje aparte (lo decide el tipo de dato).

---

## Primera ronda — las 5 fundamentales

### P1 — Problema raíz

> ¿Cuál es el **problema concreto** que el sistema resuelve, y para **quién**?

**Por qué importa**: si no entra en una frase, todo lo demás es ruido. Detecta el clásico "solución buscando problema". Setea `problem`.

**Rechazá respuestas vagas**: "ayudar a la gente", "modernizar el sector", "ser una plataforma". Pedí concreción antes de seguir.

### P2 — Alcance del MVP

> ¿Cuál es el **alcance mínimo viable** para considerarlo "lanzable"?

- (a) Solo el flujo principal end-to-end con datos simulados.
- (b) Flujo principal + integración real con el servicio externo crítico.
- (c) Flujo principal + integraciones + panel admin.

**Por qué importa**: define qué entra en la v1 y qué se posterga → alimenta el **tagging `[MVP]`/`[Post-MVP]`**. Vaguedad acá = scope creep en el sprint 2.

### P3 — Actores principales

> ¿Quiénes usan el sistema y **qué hace cada uno**? Un verbo principal por rol.

**Por qué importa**: el RBAC y la mitad de las pantallas se derivan de acá. Setea los actores e infiere `domain`.

### P4 — Restricciones técnicas no negociables

> ¿Hay restricciones **dadas de arriba** que no podés cambiar?

Sub-preguntas: ¿stack obligatorio? ¿cloud específica / on-prem? ¿legacy? ¿compliance (GDPR/HIPAA/PCI)?

**Por qué importa**: una restricción real condiciona toda la arquitectura; una falsa (preferencia disfrazada) te encierra sin necesidad. El stack obligatorio setea `stack`; las sub-preguntas de infra resuelven `needs_infra`.

### P5 — Prioridad de calidad

> Si tuvieras que elegir: ¿**velocidad de entrega**, **escalabilidad**, **mantenibilidad** o **costo**?

**Por qué importa**: no se puede maximizar todo. Filtra los patrones del `08`. Quien prioriza velocidad acepta deuda que quien prioriza escala no perdona.

---

## Segunda ronda — condicional (activá según las respuestas)

- **Transacciones financieras / datos sensibles** → ¿audit trail append-only? ¿idempotencia? ¿rollbacks? → dispara el archivo de **compliance**.
- **Múltiples actores con permisos** → ¿RBAC simple o ABAC? ¿herencia entre roles? ¿permisos a nivel de recurso? → profundidad del `03`.
- **Flujos largos / asincrónicos** → ¿webhooks? ¿máquina de estados? ¿notificaciones? → detalle del `07`.
- **Datos estructurados complejos** → ¿jerárquicos? ¿versionados? ¿soft vs hard delete? → detalle del `04`.

---

## Encuadre por `system_type` (afiná el framing)

La misma pregunta se formula distinto según lo detectado:

| system_type | Ajuste al interrogatorio |
|---|---|
| `cli` | Saltá RBAC; preguntá por comandos, flags, formato de salida, exit codes. |
| `api` | Foco en contratos, versionado de API, auth de servicio; sin preguntas de UI. |
| `saas_multi_tenant` | Sumá: ¿aislamiento por schema o por fila? ¿onboarding de tenant? ¿límites por plan? |
| `mobile` | Preguntá por estado offline, sincronización, permisos del dispositivo. |

---

## Detección de respuestas flojas

Si el usuario contesta con frases como estas, **no avances** — cuestioná y pedí concreción:

| Respuesta floja | Tu repregunta |
|---|---|
| "todo lo que se pueda" | "No se documenta 'todo'. Dame 3 cosas concretas en orden de prioridad." |
| "que sea escalable" | "¿Escalable a qué? 100 usuarios, 100k, 100M — cada una es otra arquitectura." |
| "como otros sistemas similares" | "Nombrame UNO concreto y QUÉ específico de él querés copiar." |
| "lo estándar de la industria" | "No existe 'el estándar'. Dame contexto: tipo de empresa, equipo, presupuesto." |

---

## Mapeo pregunta → efecto, por modo

### Mode A (silent) — 1 sola pregunta (el idioma)
No pregunta nada salvo **Q-idioma** (estructural, barata, evita regenerar toda la KB). El resto lo infiere de las fuentes (ver `discovery-fields.md`). `trajectory` y `maintenance_context` caen en default conservador + nota en el `10`.

### Mode B (desde cero) — batería completa
Q-idioma → language · Q-INTENT → modo · P0-sys → set adaptativo · P0-scale → profundidad datos/infra · Q-trayectoria → checklist escalado · Q-maintenance → governance · P1 → problema (rechaza vago) · P2 → tags MVP · P3 → actores+dominio · P4 → stack+infra · P5 → patrones del 08 · ronda 2 → compliance/ABAC/state-machine/versionado.

### Mode C (reverse) — mínimo, confirmación
Q-idioma → language · Q-feature → target del trazado · Q-confirm-anchor → (sí/ajustar/no) · Q-trayectoria y Q-maintenance solo si faltan · Q-MVP-tag por ítem (el código no lo sabe) · Q-WHY ante ambigüedad → respuesta al `09`, sin respuesta al `10`. No pregunta system_type/scale/stack (vienen de Capa 0).

### Mode Update / Audit
- **Update**: reusa preguntas de B (si faltan campos) o el trazado de C (si es una feature nueva). No regenera lo bueno.
- **Audit**: no pregunta — reporta.

---

## Cierre de cada ronda

Al terminar una ronda, escribí:

```markdown
**Lo que entendí**:
- [punto 1]
- [punto 2]

**Supuestos que estoy haciendo** (corregilos si no son ciertos):
- **Suposición**: [...]

**Próximos pasos**:
1. [...]
```

Esto deja explícito qué interpretaste y dónde podés estar errando — fuerza al usuario a corregir antes de que escribas algo malo en la KB.
