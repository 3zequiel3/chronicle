# Quality Rubric — completeness score por nodo

Criterios concretos para puntuar qué tan completa está la KB. Lo usa **Mode Audit** para reportar, y todo modo generador para el **auto-chequeo final** antes de cerrar.

---

## Cómo se puntúa

Cada nodo se evalúa contra su **checklist** (definido en `node-templates.md`). El score es el porcentaje de ítems del checklist cumplidos:

```
score(nodo) = ítems_cumplidos / ítems_totales del checklist
```

Banda de calidad:

| Score | Estado | Acción |
|---|---|---|
| ≥ 80% | ✅ Completo | nada |
| 50-79% | ⚠️ Parcial | listar lo faltante |
| < 50% | ❌ Insuficiente | marcar como prioridad |

---

## Criterios por nodo

| Nodo | Ítems del checklist |
|---|---|
| 01 Visión | propósito en 1 frase · alcance explícito · fuera-de-alcance |
| 02 Descripción | stack por capa · diagrama · integraciones |
| 03 Actores | matriz RBAC · rutas públicas *(N/A en CLI)* |
| 04 Datos | ERD · entidades con atributos+relaciones · contratos request/response |
| 05 Reglas | toda regla con código · tag MVP · justificación |
| 06 Funcionalidades | formato US-NNN · criterios de aceptación · enlace a reglas |
| 07 Flujos | disparador+actor · diagrama de secuencia · casos de error |
| 08 Arquitectura | patrones justificados · seguridad · env vars con sensibilidad |
| 09 Decisiones | alternativas+trade-offs · supuestos con validación |
| 10 Preguntas | inconsistencias con impacto · preguntas priorizadas |

> Los nodos omitidos por `system_type` (ej. RBAC en un CLI) no penalizan el score: se marcan **N/A**, no 0%.

---

## Chequeos transversales (además del score por nodo)

Estos no son de completitud sino de **integridad**, y valen para Mode Audit:

1. **Consistencia cruzada** — toda `RN-XX-NN`, `US-NNN`, `DD-NN` referenciada existe y resuelve.
2. **Drift interno** — sin contradicciones entre nodos (ej. cantidad de entidades en 04 vs 02).
3. **Enlaces vivos** — las referencias a archivos de entidad/dominio apuntan a rutas reales.
4. **Tags MVP** — los ítems de 05/06/07 tienen tag de alcance (o nota de por qué no).
5. **Cobertura de citas** (ver `provenance.md`) — toda afirmación factual lleva cita de origen. Métrica: `afirmaciones_citadas / afirmaciones_factuales`. Una afirmación sin cita ni marca `inferred` es un **defecto**. Extracción con `\[(code|doc|user|inferred) · ([^\]]+)\]`.
6. **Cobertura por test** (ver `reverse-documentation.md` §Tests como fuente) — qué porcentaje de reglas (`05`) está respaldado por un test vs solo por implementación. Métrica mecánica: contar reglas con cita a un test vs reglas con `⚠ sin test`. No es defecto, es **riesgo visible**: dice qué reglas no tienen red de seguridad.

---

## Formato de reporte (Mode Audit y auto-chequeo)

```markdown
## Completeness

| Nodo | Score | Faltante |
|---|---|---|
| 05 reglas | 60% ⚠️ | dominios sin código RN; sin tags MVP |
| 07 flujos | 40% ❌ | faltan casos de error en 3/5 flujos |

## Integridad
- ❌ US-014 referencia RN-PAGOS-09 que no existe en 05.
- ⚠️ 04 declara 8 entidades; 02 menciona 11.

## Procedencia
- Cobertura de citas: 84% (47/56 afirmaciones).
- ❌ 9 afirmaciones sin cita ni marca `inferred` → defecto.

## Cobertura por test
- Reglas respaldadas por test: 18/25 (72%).
- ⚠️ 7 reglas `sin test` → riesgo visible (no defecto).

## Correctitud (solo si se pidió Audit profundo — ver verification.md)
- Cobertura verificada: 40/120 (budget agotado).
- ✅ 37 confirmadas · ❌ 2 contradichas · ⚠️ 1 no soportada.

## Prioridad
1. [Alta] Resolver RN-PAGOS-09 faltante.
2. [Media] Completar casos de error del 07.
```

En modos generadores, el auto-chequeo corre este rubric **sobre el propio output** antes de cerrar; si algo queda < 50%, lo anota en `10_preguntas_abiertas.md` en vez de fingir que está completo.
