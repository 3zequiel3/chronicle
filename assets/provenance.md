# Provenance — citas de origen (el backbone verificable)

Toda afirmación factual en la KB lleva una **cita de origen** con un formato único y parseable por máquina. Esto convierte la regla madre ("nada se inventa") de una promesa en una **garantía verificable**, y es el contrato sobre el que se apoyan la verificación de correctitud, la detección de staleness y los chequeos de CI.

> Regla dura: **una afirmación factual sin cita es un defecto.** O cita su fuente, o se declara `inferred` y va al `09`/`10`. No hay tercer estado.

> Regla dura (anti-fabricación): una cita `code` **solo es válida si su símbolo fue realmente leído** — en Mode C, si está en el **mapa de traza** (la allowlist, ver `reverse-documentation.md` §3). Una cita a un símbolo que no se leyó es una **fabricación**, peor que la ausencia de cita porque simula autoridad. El `~Lnn` lo provee la herramienta de búsqueda, nunca el modelo de memoria. La cita es un subproducto de haber leído, no un campo que se completa al escribir.

---

## El formato de cita

Se renderiza como **código inline** (visualmente distinto y greppable):

```
[<tipo> · <ancla>]
```

| `tipo` | Significa | Forma del `ancla` |
|---|---|---|
| `code` | leído del código (Mode C / cross-check) | `ruta/archivo.ext#símbolo ~Lnn` |
| `doc` | de un documento fuente (Mode A) | `docs/archivo.ext §sección` |
| `user` | declarado por el usuario (Mode B / Q-WHY) | `usuario` (opcional: ronda/fecha) |
| `inferred` | sin fuente — deducido por el agente | `inferido → 09:DD-NN` o `→ 10` |

**Ancla de `code`** (decisión de diseño): el **símbolo** (función/clase/método) es la fuente de verdad — sobrevive a refactors y movimientos de línea. La línea (`~Lnn`) es solo una **pista de navegación**, nunca la referencia canónica.

### Gramática (para tooling — #3, #5, #6)

```
cita    = "[" tipo " · " ancla "]"
tipo    = "code" | "doc" | "user" | "inferred"
ancla_code     = ruta "#" símbolo [ " ~L" entero ]
ancla_doc      = ruta [ " §" sección ]
ancla_user     = "usuario" [ ":" referencia ]
ancla_inferred = "inferido → " destino     # destino: 09:DD-NN | 10
```
Regex de extracción: `\[(code|doc|user|inferred) · ([^\]]+)\]`

---

## Ejemplos

```markdown
- **RN-PAGOS-01**: el cupón no se aplica dos veces. `[code · src/payments/rules.ts#validateCoupon ~L42]`
- **Entidad Pago**: estados pending|paid|refunded. `[code · prisma/schema.prisma#Payment]`
- **RN-STOCK-03**: reserva expira a las 24h. `[doc · docs/spec.txt §Inventario]`
- **DD-02**: se eligió Postgres por consistencia transaccional. `[user]`
- **RN-PAGOS-07**: (posible) reintento idempotente. `[inferred · inferido → 10]`
```

---

## Qué lleva cita (por nodo)

| Nodo | ¿Cita? | Tipo típico |
|---|---|---|
| 04 entidades / contratos | **sí, por ítem** | `code` / `doc` |
| 05 reglas (RN) | **sí, por regla** | `code` / `doc` |
| 06 historias (US) | sí, por criterio derivado | `code` / `doc` / `user` |
| 07 flujos | **sí, por paso** | `code` (un tag por salto) |
| 09 decisiones (DD) | sí | `user` (nunca finge un `code`) |
| 01 visión · 03 actores | sí | `user` / `doc` |
| 02 · 08 (arquitectura) | sí donde es factual | `code` / `doc` / `user` |
| 10 preguntas | n/a (es el destino de lo no citable) | — |

> Los nodos de **PORQUÉ** (09) citan `user`, jamás un `code` — el código no contiene la intención. Inventar un `file#símbolo` para una decisión es una violación de la regla madre.

> **Tests = evidencia más fuerte.** Cuando una regla tiene un test que la respalda, citá el test (`[code · tests/…#"nombre del test"]`) antes que la implementación: el test es el contrato esperado, la implementación es solo el mecanismo. Si la regla sale **solo** de la implementación, marcala `⚠ sin test` (ver `reverse-documentation.md` §Tests como fuente).

---

## Comportamiento por modo

- **Mode A (ingest)**: cada afirmación cita `doc` (qué fuente la originó). Lo no rastreable a una fuente → `inferred → 10`.
- **Mode B (scratch)**: no hay sistema construido → las afirmaciones citan `user` (lo que el usuario decidió) o quedan como propuesta. No se fabrica `code`.
- **Mode C (reverse)**: el caso central. Cada claim del QUÉ cita `code` con ancla de símbolo. El PORQUÉ que el usuario responda (Q-WHY) cita `user`; lo que no responde → `inferred → 10`.
- **Mode Update**: las citas se mantienen y se actualizan al re-documentar; un claim re-derivado refresca su ancla.
- **Mode Audit**: no genera, pero **mide cobertura de citas** (ver `quality-rubric.md`).

---

## Casos borde (manejar todos)

| Caso | Qué hacer |
|---|---|
| El código no tiene un símbolo nombrable (config, SQL suelto) | Ancla = `ruta ~Lnn` sin `#símbolo`; preferí siempre el símbolo nombrado más cercano. |
| Una afirmación tiene **varias** fuentes | Listá varias citas: `` `[code · a.ts#x]` `[code · b.ts#y]` ``. |
| Flujo (07) que cruza lenguajes | Una cita `code` **por paso/salto** del flujo, cada una a su archivo/símbolo. |
| Regla que está implementada Y en un doc | Citá ambas: `` `[code · …]` `[doc · …]` `` — refuerza la confianza. |
| Símbolo renombrado/movido (en Update) | Re-trazá y actualizá el ancla; si ya no existe, marcá la afirmación como sospechosa → `10`. |
| Afirmación que el agente "sabe" pero no puede señalar | **No** la escribas como hecho: `inferred → 10`. Esto es el enforcement de la regla madre. |
| El símbolo que querés citar no está en el mapa de traza | No inventes la cita. O lo trazás (entra al mapa) o va como `inferred → 10`. Citar fuera de la allowlist es fabricación. |

---

## Por qué esto es el backbone

El formato es deliberadamente **parseable** porque tres features futuras lo consumen:

- **#3 Correctitud** — toma cada `code`/`doc` y verifica la afirmación contra su ancla.
- **#5 Staleness** — re-busca el `#símbolo`; si cambió o desapareció, marca la sección como sospechosa.
- **#6 CI** — parsea las citas y reporta cobertura (% de afirmaciones citadas) como métrica de calidad con exit code.

Diseñar la cita una sola vez, bien, es lo que hace que esas tres se enchufen sin rediseño.
