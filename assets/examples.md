# Examples — un recorrido por modo (few-shot)

Ejemplos end-to-end, uno por modo. **Cargá solo la sección del modo activo.** Sirven de referencia de estilo y de flujo esperado.

---

## Mode A — silent ingest

**Entrada**: `docs/descripcion.txt`, `docs/historias.docx`. No hay `knowledge-base/`.

**Flujo**:
1. Capa 0 detecta `docs/` con fuentes → propone Mode A.
2. Lee las fuentes, infiere discovery (`discovery-fields.md`): `system_type: web_app`, `domain: ecommerce`, `stack: Django + React`.
3. `trajectory`/`maintenance_context` no inferibles → default conservador + nota en `10`.
4. Genera los 10 nodos. El 04 tiene 5 entidades → queda **archivo** (no carpeta).
5. Auto-chequeo (`quality-rubric.md`); cierra con tabla resumen.

**Cierre**:
```markdown
## KB generada en knowledge-base/
| Nodo | Líneas | Temas |
| 01_vision_y_objetivos.md | 84 | propósito, 3 actores, alcance v1 |
| 04_modelo_de_datos.md | 120 | 5 entidades, ERD |
[DISCOVERY] trajectory/maintenance sin confirmar → ver 10_preguntas_abiertas.md
```

---

## Mode B — desde cero

**Entrada**: repo vacío. Usuario: "armemos la KB desde cero".

**Flujo**:
1. Q-INTENT → `create`. Capa 0 no detecta stack (no hay código).
2. Ronda discovery: P0-sys=(a) web_app, P0-scale=(b), Q-trayectoria=(b) semilla → activa checklist de escalado, Q-maintenance=(a) solo → governance OFF.
3. Ronda 1 (P1-P5). P1 vago ("ayudar a vender") → **rechaza**, repregunta.
4. Cierre de ronda con supuestos. Itera nodo por nodo con validación.

**Ejemplo de pregunta**:
```markdown
**P2 — Alcance del MVP**
¿Qué es lo mínimo "lanzable"?
(a) catálogo + carrito + checkout simulado
(b) + pago real
(c) + panel admin
Por qué importa: define la v1. Lo que quede afuera se etiqueta [Post-MVP].
```

---

## Mode C — reverse por funcionalidad

**Entrada**: repo con código, sin docs. Usuario: "documentá el checkout".

**Flujo**:
1. Capa 0: `package.json` → Next.js + Prisma. Carpetas `pagos/`, `stock/`.
2. **Anclaje**: busca "checkout" → encuentra `api/checkout.route.ts`.
3. **Confirmación**:
   ```
   Encontré checkout en: checkout.route.ts, payment.service.ts, stock.service.ts.
   ¿Es esto? (sí / ajustar / no)
   ```
4. **Trazado acotado** (read-only, cross-language si aplica). Al tocar `inventory` → frontera: cross-reference, no lo documenta.
5. **Merge corte vertical** con **cita por afirmación**: escribe `04/modelos/pago.md`, `05/pagos.md`, `06/pagos.md`, `07/pagos-checkout.md`. Ej:
   ```markdown
   - **RN-PAGOS-01**: el cupón no se aplica dos veces. `[code · src/payments/rules.ts#validateCoupon ~L42]`
   ```
6. Un `if` valida el cupón dos veces y no se sabe por qué → Q-WHY; sin respuesta → `[inferred · inferido → 10]`. **No inventa.**

---

## Mode Update — merge no destructivo

**Entrada**: `knowledge-base/` existe. Usuario: "actualizá con la feature de devoluciones".

**Flujo**:
1. Q-INTENT → `update`. Lee los nodos afectados.
2. Documenta "devoluciones" (reusa trazado de Mode C).
3. Al agregar reglas, `05` cruza el umbral (22 reglas en 4 dominios) → **promoción**: `05_reglas_de_negocio.md` → `05_reglas-de-negocio/` y **actualiza referencias** `RN-*` en 06/07.
4. Registra el cambio en `CHANGELOG.md`. Respeta lo que ya estaba bien.

---

## Mode Audit — validar sin generar

**Entrada**: `knowledge-base/` existe. Usuario: "auditá la KB".

**Flujo**:
1. Q-INTENT → `audit`. No genera contenido.
2. Corre `quality-rubric.md`: score por nodo + chequeos de integridad.
3. Reporta priorizado:
```markdown
## Completeness
| 07 flujos | 40% ❌ | faltan casos de error |
## Integridad
- ❌ US-014 → RN-PAGOS-09 inexistente.
## Prioridad
1. [Alta] Resolver RN-PAGOS-09.
```
4. No toca la KB salvo que el usuario pida pasar a Mode Update con los hallazgos.
