# Automation — chequeo de frescura, donde quieras (sin LLM)

Expone los chequeos baratos como un **comando mecánico y determinista** que corre en cualquier superficie (CI, hooks, manual, o preguntándole al agente). **Cero tokens**: es git + regex + hash, no LLM.

> chronicle es una skill (instrucciones para un agente), no un binario. Por eso lo **caro** (generar, verificar correctitud) necesita el agente y va on-demand/async; lo **barato** (frescura, cobertura, consistencia) es mecánico y **sí** puede ser un gate de CI real con exit code.

---

## Dos niveles

| Nivel | Qué incluye | Costo | Uso |
|---|---|---|---|
| **Mecánico** | cobertura de citas · consistencia cruzada · staleness (`git diff`) | gratis, determinista | **gate** bloqueante (PR/commit/manual) |
| **LLM** | verificación de correctitud · generar/actualizar doc | tokens, lento | on-demand / agendado, **nunca** gate bloqueante |

El gate de cada commit/PR quema **cero tokens** porque solo corre el nivel mecánico.

---

## El chequeo mecánico (sin LLM)

| Chequeo | Cómo (mecánico) | Falla si… |
|---|---|---|
| **Cobertura de citas** | extrae citas con `\[(code\|doc\|user\|inferred) · [^]]+\]`; cuenta afirmaciones factuales sin cita | cobertura < threshold |
| **Consistencia cruzada** | resuelve cada `RN`/`US`/`DD` referenciada | hay una referencia rota |
| **Staleness** | `git diff <ref> --name-only` → archivos cambiados → citas afectadas → fingerprint normalizado vs ledger | hay afirmaciones `stale`/`huérfanas` sobre código tocado |
| **Cobertura por test** | cuenta reglas con cita a un test vs reglas con `⚠ sin test` | (métrica de riesgo; bloquea solo si se configura un mínimo) |

El **staleness** es el chequeo estrella: implementa *"tocaste código documentado y no actualizaste la doc"* — ver `staleness.md`. Funciona igual en un PR que en un pre-commit de un solo dev.

---

## Contrato machine-readable

Reporte (lo consume cualquier superficie):

```json
{
  "status": "pass | fail",
  "checks": {
    "citation_coverage": { "value": 0.86, "threshold": 0.80, "pass": true },
    "cross_ref":         { "broken": 0, "pass": true },
    "staleness":         { "stale": 2, "orphaned": 1, "pass": false, "items": ["RN-PAGOS-01", "RN-STOCK-03"] }
  }
}
```

**Exit codes**: `0` = todo pasa · `1` = staleness · `2` = cobertura · `3` = consistencia · (combinables por bitmask si hace falta). El detalle siempre va en el reporte.

**Config opcional** (`knowledge-base/.chronicle/checks.json`) — thresholds y qué bloquea:

```json
{ "coverage_threshold": 0.80, "block_on_stale": true, "block_on_broken_ref": true }
```
Sin config, defaults razonables (cobertura 0.80, staleness y refs rotas bloquean).

---

## Superficies (PRs son opcionales)

| Tu workflow | Artefacto |
|---|---|
| Equipo con PRs | GitHub Action / GitLab CI en el PR o push |
| **Solo / sin PRs** | hook **pre-commit** o **pre-push** (local, frena el commit malo) |
| Sin hooks | **comando manual** cuando quieras |
| Cero automatización | **preguntale al agente**: "¿la doc quedó vieja?" → Mode Audit interactivo |
| Agendado | cron / agente programado (para el nivel LLM profundo) |

Nadie está obligado a usar PRs: la capacidad es el chequeo; la superficie la elegís vos, o ninguna.

---

## Generado a medida

chronicle **no incluye un script fijo** (te ataría a un runtime y traería los líos de cross-platform de vuelta). En cambio, **emite el artefacto a tu medida** cuando se lo pedís ("armá el chequeo de CI"), implementando el contrato runtime-agnóstico de `checker-spec.md`:

- detecta tu CI y stack (de la Capa 0),
- genera el checker en el **runtime que tu proyecto ya usa** (Node → node, Python → python, Go → go) + la GitHub Action / el hook que lo invoca,
- cross-platform por construcción (Windows/Linux/macOS según el target),
- aplicando las **reglas de seguridad** del checker (`checker-spec.md` §5: argv-arrays, parse-no-exec, confinamiento a la raíz),
- usando el preflight de búsqueda de `reverse-documentation.md` §0 cuando el chequeo necesita buscar.

> **Auto-verificación antes de confiar (no opcional).** Apenas generás el checker, corrélo contra el golden fixture (`assets/conformance/sample-kb/`) y compará con `assets/conformance/expected.json`. Si no coincide exacto, el checker está mal generado → **regeneralo**. Ver `checker-spec.md` §7. Así la correctitud queda **verificada por generación**, no asumida.

Así el chequeo es turnkey **sin** un script que chronicle tenga que mantener, y sin imponerte Python ni ningún runtime ajeno al proyecto.

---

## El nivel LLM (aparte, nunca gate)

La verificación de correctitud (`verification.md`) y el auto-update corren **on-demand o agendados** — por ejemplo, un agente headless nocturno que audita en profundidad y abre un issue/PR con los hallazgos. Nunca como chequeo síncrono y bloqueante, porque cuesta tokens y no es determinista.
