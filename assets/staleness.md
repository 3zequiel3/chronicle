# Staleness — ¿la doc envejeció? (chequeo barato, on-demand)

Detecta cuándo la documentación quedó vieja respecto al código, comparando el fingerprint **actual** de cada fuente citada contra el guardado en el ledger (`verification.json`). Sin esto, la doc miente en silencio cuando el código cambia.

> **Staleness ≠ verificación.** Staleness pregunta *"¿la fuente cambió?"* — comparación **mecánica** de fingerprints, barata. La verificación (#3) pregunta *"¿la afirmación sigue coincidiendo?"* — juicio, cara. **El staleness es el filtro barato que le dice a la #3 qué re-verificar.**

Read-only, on-demand, en **subagente aislado** (principio token-economy). Reusa el ledger, el fingerprint **normalizado** y la búsqueda-primero ya construidos — no rediseña nada.

---

## El pase

1. **Git fast-path** (si hay git, ver abajo) → la lista de citas candidatas (las que apuntan a archivos cambiados). Sin git → todas las citas `code`, acotado por presupuesto.
2. Por cada cita candidata: re-localizá el símbolo (búsqueda-primero), re-calculá el **fingerprint normalizado**, compará con el del ledger.
3. **Clasificá:**

| Resultado | Significa | Acción |
|---|---|---|
| igual | la afirmación sigue fresca | nada |
| distinto | el símbolo cambió | **stale** → marcar sospechosa |
| desaparecido | símbolo borrado/renombrado | **huérfana** → marcar |
| movido | el símbolo existe en otro lado | refrescar el ancla (`~Lnn`/archivo) + revisar |

4. **Actualizá el ledger** (estado + nuevo fingerprint/`ref`) y **reportá**. La escritura del `verification.json` la hace el **checker mecánico**, nunca el LLM a mano (regla de propiedad del ledger — ver `checker-spec.md` §6 y `verification.md`).

---

## Git fast-path (la optimización que la hace viable correr seguido)

El ledger guarda el `ref` (commit) de la última corrida. Con git:

```
git diff <ref> --name-only        # archivos cambiados desde la línea base, incluye sin commitear
```

Solo las citas que apuntan a **esos archivos** son candidatas; el resto se presume fresco. De re-fingerprintear 200 símbolos pasás a los ~5 archivos que se tocaron. **Por eso es barato hasta para correr por commit en CI** (#6).

> `git diff <ref>` (sin `..HEAD`) compara la línea base contra el **working tree**, así que **también capta cambios sin commitear**. Eso resuelve el agujero que tendría un fingerprint puramente git-based.

**Sin git**: re-fingerprinteá todas las citas `code`, priorizado por riesgo y acotado por presupuesto; reportá cobertura. Más caro, pero correcto.

---

## Qué produce (no auto-arregla)

Read-only + no destructivo: **marca, no reescribe.**

```markdown
## Staleness
- 6 stale (fuente cambió) · 1 huérfana (símbolo borrado) · 2 movidas.
- ❌ RN-PAGOS-01 stale: `validateCoupon` cambió desde la última corrida.
- ⚠️ RN-STOCK-03 huérfana: `reserveStock` ya no existe.
→ Sugerencia: Mode Update scopeado SOLO a estas 9 afirmaciones.
```

El usuario decide: dispara un **Mode Update** acotado a lo stale (no a toda la KB). Y opcionalmente, las stale se pasan a la **#3** para re-verificar si, además de cambiar, ahora **contradicen** la doc.

---

## Composición con la #3 (lo barato filtra lo caro)

```
staleness (barato)  →  marca las 9 afirmaciones cuya fuente cambió
                          ↓
verificación #3 (cara)  →  corre SOLO sobre esas 9, no sobre las 120
```

No re-verificás lo que no cambió. Las dos se abaratan mutuamente.

---

## Casos borde

| Caso | Qué hacer |
|---|---|
| Cita `inferred` / `user` | No tiene fuente de código → staleness **no aplica**. |
| Sin ledger previo (nunca se fingerprinteó) | No hay contra qué comparar → primero corré una verificación/fingerprint inicial (#3) que **siembra** el ledger. |
| Repo enorme | El git fast-path lo hace barato; sin git, budget-bounded + reporte de cobertura. |
| El archivo cambió pero el símbolo citado no | El fast-path lo marca candidato, pero el fingerprint normalizado da **igual** → fresco. Sin falso positivo. |
| Símbolo movido a otro archivo | `movido` → actualizá el ancla de la cita y marcalo para revisión, no lo tires. |
