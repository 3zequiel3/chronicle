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

---

## Bordes de estructura

| Situación | Qué hacer |
|---|---|
| Colección cruza el umbral durante un Update | Promové archivo→carpeta y **actualizá las referencias cruzadas** (no las dejes rotas). |
| Una feature (Mode C) toca otra funcionalidad | Regla de frontera: cross-reference y parar, no documentar la otra. |
| Nodo omitido por `system_type` | Anotá la omisión en el índice; no dejes un archivo vacío. |
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

Corré esta verificación sobre tu **propio output** antes de devolverle al usuario:

1. **Completitud** — pasá el `quality-rubric.md`. Cualquier nodo < 50% → nota en `10`.
2. **Consistencia cruzada** — toda `RN`/`US`/`DD` referenciada existe.
3. **Enlaces** — las rutas a archivos de entidad/dominio resuelven.
4. **Regla madre** — ninguna suposición quedó escrita como hecho; ¿todas marcadas o en `09`/`10`?
5. **Sin código tocado** — confirmá que no se modificó ningún archivo de código fuente.
6. **Idioma** — un solo idioma en toda la KB.

Si algo falla, **arreglalo o anotalo** — no cierres declarando "completo" lo que no lo está. La honestidad del estado es parte del contrato.
