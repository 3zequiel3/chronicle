# Edge Cases — bordes y auto-chequeo final

Qué hacer cuando la situación no es limpia, y la verificación que corre el agente antes de cerrar. Cargá este asset cuando la detección sea ambigua o antes de finalizar.

---

## Bordes de detección (Step 0)

| Situación | Qué hacer |
|---|---|
| `docs/` **y** `knowledge-base/` existen | Preguntá: ¿actualizar la KB (Update) o regenerar desde docs (A)? No asumas. |
| `docs/` con solo un `README` | No es fuente → tratá como Mode B (desde cero), no Mode A. |
| `knowledge-base/` existe pero incompleta | Mode Update (completar huecos), no recrear desde cero. |
| No hay manifest reconocible (stack desconocido) | No inventes el stack → preguntá, o marcá `stack: desconocido` y nota en `10`. |
| Monorepo políglota | `stack` estructurado por servicio; en Mode C, trazá cross-language. |
| Código sin docs y sin pedido de feature concreta | Mode C necesita un target → pedí qué funcionalidad documentar primero. |
| Intención ambigua del usuario | Resolvé con Q-INTENT explícita antes de actuar. |
| Sin herramienta de búsqueda (Mode C, ni nativa ni `rg`/`git grep`/`grep`) | **No traces a ciegas.** Pedí instalar ripgrep con el comando del SO y el porqué (ver `reverse-documentation.md` §0 Preflight). |
| Windows (separador de rutas `\`) | Normalizá las rutas de las citas a `/` para que sean estables entre SO. |

---

## Bordes de estructura

| Situación | Qué hacer |
|---|---|
| Colección cruza el umbral durante un Update | Promové archivo→carpeta y **actualizá las referencias cruzadas** (no las dejes rotas). |
| Una feature (Mode C) toca otra funcionalidad | Regla de frontera: cross-reference y parar, no documentar la otra. |
| Nodo desactivado por el profile del `system_type` | Anotá la omisión en el índice; no dejes un archivo vacío. Ver `node-templates.md` §Eje 1. |
| Idioma mezclado en la KB existente | Detectá el idioma dominante y mantenelo; no mezcles (ver `conventions.md`). |

---

## Bordes de contenido (regla madre)

| Situación | Qué hacer |
|---|---|
| El código hace algo y no se entiende por qué | El QUÉ va al nodo; el PORQUÉ → preguntá (→ `09`) o → `10`. Nunca inventes. |
| Dos fuentes se contradicen (Mode A) | Registralo como `IN-NN` en `10`, no elijas en silencio. |
| Campo de discovery no inferible | Default conservador + nota `[DISCOVERY]` en `10` (ver `discovery-fields.md`). |
| Tag MVP/Post-MVP desconocido en Mode C | Sin tag + duda en `10`; el código no carga roadmap. |

---

## Auto-chequeo final (antes de cerrar, todo modo generador)

El cierre tiene **dos niveles** — y el mecánico manda.

### Nivel mecánico (AUTORIDAD — lo corre el checker, no el LLM)

Estos chequeos son deterministas, así que **no los "verifica" el modelo sobre sí mismo**: los corre el **checker mecánico** (`checker-spec.md`), el **mismo binario que el gate de CI**. Es **fail-closed**: no declares la KB completa si el checker está en rojo.

1. **Consistencia cruzada** — toda `RN`/`US`/`DD` referenciada existe y resuelve.
2. **Enlaces vivos** — las rutas a archivos de entidad/dominio resuelven.
3. **Cobertura de procedencia** — toda afirmación factual lleva cita (`[code/doc/user]`) o está marcada `[inferred → 10]`. Sin cita = defecto (regla madre, ver `provenance.md`).
4. **Spot-check de existencia (anti-cita-fabricada)** — los símbolos citados **existen** en la ruta citada. Escala con el tamaño, no es tope fijo: **todas** las citas de alto riesgo (`RN` + contratos/entidades del `04`) siempre, + muestra proporcional (~20%, mínimo 10) del resto, acotada por presupuesto. Reportá cobertura real (`chequeadas/total`); ancla rota → se marca y va al `10`.

**Persistencia + enforcement.** El resultado se guarda en `knowledge-base/.chronicle/last-check.json` con el git ref. Si el proyecto todavía **no tiene checker generado**, corré estos cuatro con tus tools deterministas (grep/regex sobre la KB) como equivalente y **ofrecé generar el checker persistente** para que CI/pre-commit los re-corra sin vos. La atrapada **real** es CI; el cierre de run es la atrapada temprana. Si algo está en rojo: **arreglalo o marcalo `inferred`/`→10`** y re-corré — nunca cierres declarando "completo" sobre rojo.

### Nivel de juicio (lo corre el LLM — no es mecanizable)

5. **Completitud** — pasá el `quality-rubric.md`. Cualquier nodo < 50% → nota en `10`.
6. **Sin código tocado** — confirmá que no se modificó ningún archivo de código fuente.
7. **Idioma** — un solo idioma en toda la KB.

La honestidad del estado es parte del contrato: reportá cobertura real, nunca "completo" sobre una muestra parcial.

> **Complemento semántico (opcional, no bloquea).** El gate mecánico ve forma (existe/resuelve), no contenido. Si querés cazar la afirmación que existe pero está **mal**, corré la **auditoría post-generación** (`verification.md` §Auditoría post-generación): un subagente fresco audita una muestra de alto riesgo, adversarial. Cuesta tokens → reporta al `10`, no bloquea. El gate que bloquea sigue siendo el mecánico.
