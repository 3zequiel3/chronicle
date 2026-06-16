# Discovery Fields — el modelo que guía cada run

chronicle establece un puñado de **hechos del proyecto** al arrancar (el discovery) y los usa durante todo el run para decidir cómo se comporta: qué nodos genera, si enciende governance, si activa el checklist de escalado, etc.

> Esto es **estado interno del run**, no se escribe a ningún archivo externo. chronicle es standalone: razona con estos campos en memoria y los refleja en la KB que produce.

---

## El set de campos

| Campo | Qué representa | Cómo se obtiene | Qué dispara |
|---|---|---|---|
| `intent` | La operación pedida | preguntado (Q-INTENT) | Elige el modo (create/ingest/reverse/update/audit) |
| `system_type` | Tipo de sistema | detectado (Capa 0) / preguntado (P0-sys) | Selecciona el **profile** (núcleo de 4 + variables 03-08) — ver `node-templates.md` §Eje 1 |
| `scale` | Escala actual | detectado / preguntado (P0-scale) | Profundidad de datos/caché/tenancy |
| `domain` | Dominio de negocio | detectado / inferido | Naming, agrupación de dominios |
| `trajectory` | Ambición (hoy → futuro) | preguntado (Q-trayectoria) | Checklist de escalado |
| `maintenance_context` | Quién mantiene la doc | preguntado (Q-maintenance) | Gate de governance |
| `stack` | Tecnologías por capa | detectado (manifests) | Tabla de stack, trazado cross-language |
| `needs_infra` | ¿Hay infra no trivial? | detectado / inferido | Extras de infra/despliegue |
| `language` | Idioma de la KB | **preguntado** (Q-idioma) | Nombres de archivo y contenido de toda la KB |

### Dos naturalezas

- **Detectables / inferibles**: `system_type`, `scale`, `domain`, `stack`, `needs_infra`. Salen de la huella del filesystem (`detection-funnel.md`) o de las fuentes. Se **confirman**, no se preguntan de cero.
- **Intención humana**: `intent`, `trajectory`, `maintenance_context`, `language`. **No** están en el código ni en los docs — se **preguntan**. Nunca se inventan. (`language` no se infiere del repo por el riesgo de *espanglish*: errar = regenerar toda la KB.)

---

## Inferencia en Mode A (silent, solo pregunta el idioma)

Mode A es fire-and-forget salvo por Q-idioma (ver más abajo). Los campos detectables/inferibles se sacan de las fuentes:

| Campo | Inferir de | Señal |
|---|---|---|
| `problem` | la visión generada | la primera frase declarativa sobre qué resuelve el sistema |
| `system_type` | la descripción/arquitectura | "web app", "REST API", "CLI", "mobile", "SaaS", "multi-tenant", "librería/SDK", "pipeline/ETL" |
| `domain` | actores + funcionalidades | nombres de actores y agrupación de features (ecommerce → productos/carrito; fintech → transacciones) |
| `scale` | actores + menciones de escala/RBAC | conteo de actores, complejidad de RBAC, keywords de escala |
| `stack` | la descripción general | frameworks, lenguajes, DB, servicios externos |
| `needs_infra` | descripción + arquitectura | `true` si hay Docker, DB, Redis, colas, cron o infra de despliegue |

### Regla de baja confianza

**Nunca pongas un valor con cara de certeza si no lo tenés.** Cuando un campo no se puede inferir con confianza razonable:

1. Poné el mejor esfuerzo marcado como incierto (ej. `"web_app (inferido, baja confianza)"`).
2. Registralo en `10_preguntas_abiertas.md`:
   ```
   [DISCOVERY] No se pudo inferir `<campo>` con confianza desde las fuentes.
   Confirmar: <qué hace falta saber>.
   ```
3. Seguí — nunca bloquees Mode A por un solo campo incierto.

### Campos de intención humana en Mode A

`trajectory` y `maintenance_context` **no** son inferibles de docs (son intención de producto/equipo, no contenido). Mode A los pone en **default conservador** — `trajectory` sin setear (sin checklist de escalado) y `maintenance_context = solo` (governance OFF) — y deja una nota `[DISCOVERY]` en `10_preguntas_abiertas.md` para que el usuario los confirme. Nunca los adivina.

`language` y `system_type` son la **excepción**: aunque Mode A es silencioso, antes de generar se **confirman** ambos en un solo paso. El idioma se pregunta (Q-idioma); el `system_type` se **infiere de las fuentes pero se confirma** porque ahora **selecciona el profile** (qué nodos existen) — inferirlo mal genera el set de nodos equivocado en silencio. Los dos son estructurales: errarlos obliga a regenerar toda la KB, y por eso no se dejan en default ni se asumen. Ver `interview-guide.md` §Mode A y `conventions.md` §6.
