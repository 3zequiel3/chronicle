# Detection Funnel — Arranque barato y preciso (3 capas)

El arranque de la skill es lo que decide si es cara o barata. La regla: **el filesystem te dice el QUÉ-existe (se detecta); el usuario te dice el QUÉ-querés (se pregunta).** Nunca intentes inferir la intención leyendo código — no se puede y es carísimo.

Las tres capas van de lo más barato a lo más caro. No subas de capa hasta agotar la anterior.

---

## Capa 0 — Huella del filesystem (casi 0 tokens, SIN leer código fuente)

Antes de preguntar nada y antes de abrir un solo archivo de código fuente, escaneá la estructura.

### Stack vía manifests (detección por SEÑAL, no por lectura)

Un solo read de un archivo chico y denso resuelve el stack completo. Leer archivos de código fuente para "adivinar" la tecnología es tirar tokens.

| Señal (archivo) | Te dice |
|---|---|
| `package.json` | Node/TS + framework (react, next, express, nest…) + libs en `dependencies` |
| `tsconfig.json` | TypeScript |
| `go.mod` | Go + módulos y versión |
| `requirements.txt` / `pyproject.toml` / `Pipfile` | Python + deps |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` | Java / Kotlin |
| `composer.json` | PHP (+ Laravel/Symfony por deps) |
| `Gemfile` | Ruby (+ Rails) |
| `*.csproj` / `*.sln` | .NET / C# |
| `pubspec.yaml` | Dart / Flutter |
| `docker-compose.yml` / `Dockerfile` | infra, servicios, `needs_infra = true` |
| `prisma/schema.prisma` / `*.sql` / migraciones | DB + modelo de datos (insumo para nodo 04) |
| `openapi.*` / `swagger.*` | contratos de API (insumo para nodo 04) |

> Leé **solo la sección de dependencias** del manifest cuando alcance. No hace falta el archivo entero.

### Otras señales estructurales (gratis)

| Señal | Te dice |
|---|---|
| Nombres de carpetas (`pagos/`, `stock/`, `auth/`) | Dominios candidatos del sistema |
| Existencia de `docs/` con fuentes | Candidato a **Mode A** |
| Existencia de `knowledge-base/` | Candidato a **Mode Update / Audit** |
| Ausencia de ambos + presencia de código | Candidato a **Mode C** |
| Ausencia de todo | Candidato a **Mode B** |
| Conteo de archivos / LOC aproximado | Señal de **tamaño** → alimenta el umbral archivo↔carpeta y la pregunta demo-vs-grande |

**Salida de la Capa 0**: stack (estructurado por capa), dominios, modo propuesto, tamaño — todo **sin leer código fuente**.

---

## Capa 1 — Confirmar + preguntar SOLO los huecos

Mostrá lo detectado y pedí confirmación. Ejemplo:

```
Detecté: Next.js + Prisma + Postgres. Monorepo con módulos pagos/ y stock/.
~18 entidades. No hay docs/ ni knowledge-base/. ¿Es correcto?
```

Luego hacé **únicamente** las preguntas que ningún archivo puede responder (conocimiento humano puro): intención, trayectoria, mantenimiento, frontera MVP, y el problema raíz. Todo lo que la Capa 0 ya resolvió (`system_type`, `scale`, `stack`, `domain`) se **confirma**, no se pregunta.

El detalle de cada pregunta y su efecto por modo está en [`interview-guide.md`](interview-guide.md).

> **No-invención**: confirmar una inferencia con el usuario NO es opcional para campos que afectan estructura (`system_type`, `scale`). Una inferencia sin confirmar que cambia la KB se marca como `**Suposición:**` y, si el usuario no está disponible, va a `10_preguntas_abiertas.md`.

---

## Capa 2 — Lectura profunda, acotada

Leer código fuente de verdad ocurre **únicamente en Mode C**, y solo de la **funcionalidad puntual** que el usuario pidió documentar, siguiendo el trazado acotado de [`reverse-documentation.md`](reverse-documentation.md). **Nunca** "leo todo para entender".

Esto es lo que hace que documentar un proyecto gigante cueste casi lo mismo que uno chico: nunca lees el gigante entero, lees su huella barata (Capa 0) y después solo la rebanada que te piden (Capa 2).

---

## Resumen del embudo

```
Capa 0 (manifests + estructura, gratis)
   → Capa 1 (confirmar lo detectado + preguntar solo huecos humanos)
      → Capa 2 (lectura profunda SOLO de la feature pedida, solo en Mode C)
```
