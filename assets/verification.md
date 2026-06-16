# Verification — correctitud contra la fuente (Audit profundo, on-demand)

Verifica que la documentación **coincida con la realidad**, no solo consigo misma. Toma cada afirmación con cita `code`/`doc`, vuelve a la fuente citada, y dictamina si la afirmación se sostiene.

> Consistencia = la doc concuerda consigo misma. Completitud = tiene todas sus partes. **Correctitud = concuerda con la fuente.** Esto último es lo que verifica este pase.

Es una **profundidad opcional del Mode Audit**, no un modo nuevo. Lee código en modo **read-only** (consistente con la regla madre: leer sí, modificar nunca).

---

## Economía de tokens (principio de diseño, no opcional)

Verificar es lo que más fácil funde una sesión. Por eso el pase está acotado por diseño:

1. **On-demand** — corre solo cuando el usuario (o CI) lo pide. La generación nunca verifica contra código; solo auto-chequea la forma.
2. **Subagente aislado** — toda la lectura cara ocurre en un subagente con contexto propio que devuelve **solo veredictos compactos**. La sesión principal no se infla.
3. **Agrupar por fuente** — las citas se agrupan por `archivo#símbolo`; cada fuente se lee **una vez** y se verifican todas sus afirmaciones juntas.
4. **Leer la rebanada, no el archivo** — el ancla apunta a un símbolo; se lee esa función/región, no el archivo entero.
5. **Acotado por presupuesto y priorizado por riesgo** — verifica lo importante primero, corta al llegar al budget, y **reporta cobertura**. Nunca finge haber verificado todo.

---

## Mecánico primero, semántico después (división de trabajo)

La verificación tiene dos partes con costos y naturalezas distintas — **no las mezcles**:

- **Lo mecánico lo resuelve el checker** (`checker-spec.md`), determinista y sin tokens: ¿el símbolo citado **existe**? ¿su fingerprint **cambió** desde el ledger? Eso es un oráculo independiente, no opinión del modelo.
- **Lo semántico lo resuelve el LLM**, y **solo eso**: ¿la afirmación **coincide** con lo que el símbolo realmente hace? Es la única parte irreducible a regex.

El staleness (barato, mecánico) filtra qué llega al LLM: no re-verificás semánticamente lo que no cambió. Lo barato acota lo caro.

---

## El pase, paso a paso

1. **Recolectar** las citas `code`/`doc` del scope (toda la KB, un nodo, o una funcionalidad). Las `user`/`inferred` **no se verifican** — no hay fuente factual contra qué chequear.
2. **Filtro mecánico** — el checker resuelve existencia + cambio de fingerprint contra el ledger. Lo que existe y **no cambió** se reusa (veredicto cacheado); lo que desapareció ya queda marcado sin gastar LLM. Solo lo **cambiado o nunca verificado** pasa al juicio semántico.
3. **Agrupar** las afirmaciones pendientes por archivo (cada fuente se lee una vez).
4. **Priorizar** por riesgo: `RN` (reglas de negocio) → entidades/contratos (`04`) → flujos (`07`) → resto.
5. **Despachar al subagente para REFUTAR, no para confirmar.** El batch lleva `(afirmación, cita, ruta#símbolo)` y la instrucción: *"buscá evidencia de que la doc está MAL. Si no podés sostenerla con la fuente, el veredicto es `contradicted`/`unsupported`. Ante la duda, NO la confirmes."* El framing de refutación atrapa más que el de confirmación, al mismo costo. **Preferí el test como fuente**: si la afirmación tiene una cita a un test, verificá contra la aserción del test (el contrato), no contra la implementación. El subagente lee read-only solo esos símbolos y devuelve veredictos.
6. **Cortar** al agotar el presupuesto; lo no alcanzado queda `unverified` (reportado, no oculto).
7. **Persistir y reportar.** Los veredictos se escriben al ledger **a través del checker** (ver §propiedad del ledger), nunca editando el JSON a mano. Reportá cobertura.

### Veredictos

| Veredicto | Significa | Acción |
|---|---|---|
| `confirmed` | el código/doc sostiene la afirmación | nada |
| `contradicted` | la fuente dice otra cosa | registrar en `10` + marcar el ítem |
| `unsupported` | la cita no alcanza para sostenerla | revisar la cita o la afirmación |
| `unverified` | no se llegó (budget/sin fuente accesible) | reportado en cobertura |

---

## El ledger (mecanismo compartido con #5)

Se persiste en `knowledge-base/.chronicle/verification.json`. Markdown limpio; estado de tooling aparte.

> **Propiedad del ledger (regla dura).** El `verification.json` lo escribe **solo el checker mecánico** (`checker-spec.md` §6). El LLM **nunca lo edita a mano** — solo lo lee para decidir qué re-verificar. El estado de tooling es responsabilidad del tooling; mantenerlo en lenguaje natural deriva.

```json
{
  "version": 1,
  "verified_at": "<timestamp>",
  "ref": "<git commit en el que se fingerprinteó, si hay git>",
  "coverage": { "verified": 40, "total": 120, "unverified": 80 },
  "claims": [
    {
      "id": "RN-PAGOS-01",
      "node": "05_reglas-de-negocio/pagos.md",
      "citation": "code · src/payments/rules.ts#validateCoupon",
      "fingerprint": "<digest del cuerpo del símbolo citado>",
      "verdict": "confirmed",
      "note": ""
    }
  ]
}
```

**El `fingerprint`** es un hash del cuerpo del símbolo citado, **normalizado** — espacios, formato y comentarios colapsados — de modo que un reformateo o un comentario nuevo **no** cuentan como cambio (solo el cambio real de lógica). Se calcula con la herramienta de hashing disponible (`sha256sum`/`shasum` u otra); sin hashing, una firma estructural normalizada como fallback. El campo `ref` guarda el commit git de la corrida (si hay git), que la #5 usa de línea base. Es el backbone que comparten dos features:

- **#3 (este pase)** lo usa para **saltar** afirmaciones cuya fuente no cambió.
- **#5 (staleness)** lo compara contra el fingerprint actual: si difiere, la fuente cambió y la afirmación queda **sospechosa**.

Diseñar el fingerprint una sola vez es lo que hace que la #5 se enchufe sin rediseño.

---

## Casos borde

| Caso | Qué hacer |
|---|---|
| La fuente citada ya no existe (símbolo borrado) | `contradicted`/`unsupported` + nota; la #5 lo tomará como stale. |
| Afirmación con varias citas | se sostiene si **todas** sus fuentes la confirman; si una contradice, `contradicted`. |
| Cita `doc` (Mode A) | se verifica contra el documento fuente, igual que `code` contra código. |
| Sin presupuesto para todo | priorizá por riesgo y reportá `unverified` honestamente; nunca marques verde lo no verificado. |
| El usuario no tiene acceso al código (solo docs) | se verifican las `doc`; las `code` quedan `unverified`. |

---

## Salida

El Mode Audit incorpora una sección de correctitud al reporte (ver `quality-rubric.md`):

```markdown
## Correctitud (verificación profunda)
- Cobertura: 40/120 afirmaciones verificadas (budget agotado).
- ✅ 37 confirmadas · ❌ 2 contradichas · ⚠️ 1 no soportada.
- ❌ RN-PAGOS-07 contradicha: el código no reintenta de forma idempotente → 10.
```

El pase **no modifica la KB** por sí mismo; las contradicciones se registran en `10` y el usuario decide pasar a Mode Update.
