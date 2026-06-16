# Reverse Documentation — Mode C (read-only, por funcionalidad)

Mode C documenta un **sistema ya construido que no tiene documentación**, leyendo el código en modo **read-only** y scopeando **por funcionalidad** (un corte vertical que cruza carpetas/lenguajes), no por módulo.

> **Regla madre (no negociable)**: el código se LEE pero NUNCA se modifica. El código dice el **QUÉ**; el usuario dice el **PORQUÉ**; nada se inventa.

---

## Por qué por funcionalidad y no por módulo

Una funcionalidad es un **corte vertical**: el checkout no vive en `pagos/`, vive en `pagos/` + `stock/` + `users/` + `notifications/`. Documentar por módulo fragmenta la historia; documentar por funcionalidad sigue el flujo real. Además, mapea exacto a los nodos colección de la KB (04, 05, 06, 07), que ya están organizados por funcionalidad.

> La organización por funcionalidad es un **lente conceptual**, no un espejo de las carpetas del código. Aunque el código sea un monolito desprolijo, la KB le impone el orden que el código todavía no tiene. No necesitás un código bien modularizado para documentarlo bien.

---

## Protocolo: preflight → anclaje → confirmación → trazado → merge

> Todo el trazado (búsqueda + lectura de rebanadas) corre en un **subagente aislado** (principio de economía de tokens, ver SKILL.md): la exploración cara ocurre afuera y devuelve un **mapa de traza** compacto. La sesión principal no se infla.

### 0. Preflight — capacidad de búsqueda

El trazado se apoya en **búsqueda rápida sobre el repo** (mapear por nombre sin leer cuerpos). Antes de trazar, asegurá la capacidad de búsqueda en este orden:

1. **Herramienta de búsqueda nativa del agente** (ej. la tool `Grep` del runtime) — portable, sin instalación, agnóstica del SO. Si está, usala. **Es la opción preferida** y resuelve el caso Windows sin depender de nada instalado.
2. Si hay que ir al shell: probá `rg` (ripgrep) → `git grep` (si es repo git) → `grep` (Unix) / `findstr` (Windows).
3. **Si no hay NINGUNA**, no traces a ciegas. **Pará** y pedí instalar ripgrep con el comando del SO y el porqué:

| SO | Comando |
|---|---|
| Windows | `winget install BurntSushi.ripgrep.MSVC` (o `scoop install ripgrep` / `choco install ripgrep`) |
| macOS | `brew install ripgrep` |
| Debian/Ubuntu | `sudo apt install ripgrep` |
| Fedora | `sudo dnf install ripgrep` |
| Arch | `sudo pacman -S ripgrep` |

> **Para qué se usa** (explicáselo al usuario): chronicle traza una funcionalidad **buscando nombres** (rutas, eventos, símbolos) en el código en vez de leer todo. La búsqueda rápida es lo que hace el trazado **barato y confiable**; sin ella, habría que leer archivos a ciegas — caro e incompleto.

> **Portabilidad Windows**: normalizá las rutas de las citas a `/` (forward slash) sin importar el SO, para que `[code · ruta#símbolo]` sea estable entre Windows y Unix.

### 1. Anclaje
Del nombre de la funcionalidad ("el checkout"), extraé **términos semilla** (entidades, rutas, keywords del dominio) y localizá el **punto de entrada** con búsqueda read-only (un endpoint, una ruta, un controller, un service). No abras todavía medio repo: encontrá el hilo del que tirar.

### 2. Confirmación (antes de trazar)
Mostrá al usuario qué encontraste y confirmá el alcance **antes** de documentar:

```
Encontré "checkout" en:
- src/api/checkout.controller.ts (entrada)
- src/services/payment.service.ts
- src/services/stock.service.ts
¿Es esta la funcionalidad que querés documentar? (sí / ajustar / no)
```

Esto evita documentar lo equivocado — riesgo real cuando el target viene en lenguaje natural.

### 3. Trazado acotado (híbrido, loop-until-dry)

Estrategia **híbrida**: búsqueda-primero para mapear el territorio + seguir-llamadas dentro de los archivos ya confirmados. Una **frontera** que se expande hasta secarse, con tope de presupuesto.

**El loop:**
1. Frontera inicial = términos semilla + el punto de entrada confirmado.
2. Por cada término sin explorar: **buscá** (no leas) sus ubicaciones en el repo.
3. Confirmá relevancia (mismo dominio/feature). Leé **solo la rebanada** del símbolo confirmado y, dentro de ese archivo, seguí las llamadas directas relacionadas.
4. Extraé términos nuevos del cuerpo: funciones llamadas, **eventos emitidos**, **colas/tópicos**, **claves de config**, interfaces. Agregalos a la frontera.
5. Repetí hasta que la frontera **se seque** (no aparecen términos nuevos = punto fijo) **o** se agote el presupuesto.
6. Si el budget cortó antes de secarse → reportá **trazado parcial** (qué quedó sin explorar). Nunca lo declares completo.

**Checklist de indirecciones** — lo que el seguimiento de llamadas se pierde; buscalo explícitamente **por nombre**:

| Indirección | Qué buscar |
|---|---|
| Inyección de dependencias | el nombre de la interfaz **+** sus implementaciones |
| Eventos / pub-sub | el nombre del evento, en **emisión Y suscripción** |
| Colas / mensajería | el nombre de la cola/tópico, en **productor Y consumidor** |
| Routing por config | la ruta/path en archivos de config (yaml/json/env) |
| Dispatch dinámico / reflexión | el string del método/handler resuelto en runtime |
| Middleware / decoradores | el decorador/middleware aplicado al handler |

**Cross-language**: los enlaces entre servicios (REST, gRPC, cola) se cruzan buscando el **contrato compartido** — el path del endpoint o el nombre del mensaje — en ambos lados del límite.

**Regla de frontera**: cuando un símbolo encontrado pertenece claramente a **otra funcionalidad**, no lo expandas — cross-reference y seguí. La frontera se decide por **dominio**, no por distancia de llamada.

**Salida — el mapa de traza**: el subagente devuelve la lista compacta de `(símbolo, rol, archivo)` confirmados + el estado (`completo` | `parcial`, con lo no explorado). Ese mapa es lo que **alimenta las citas `[code · #símbolo]`** del merge (paso 4): cada afirmación documentada sale de un nodo del mapa.

### 4. Merge (corte vertical, no destructivo)
Documentar una funcionalidad es una **actualización quirúrgica de varios nodos a la vez**, nunca una regeneración total:

| Nodo | Qué se escribe para la feature |
|---|---|
| 04 modelos-apis | entidades y contratos que la feature toca (`modelos/pago.md`, `contratos-api/pagos.md`) |
| 05 reglas-de-negocio | reglas detectadas en el código (`pagos.md` → `RN-PAGOS-NN`) |
| 06 funcionalidades | la historia de usuario / épica (`pagos.md` → `US-NNN`) |
| 07 flujos-principales | el flujo extremo a extremo (`pagos-checkout.md`) |

Si el nodo es archivo (sistema chico) se mergea en el archivo; si es carpeta, se escribe el archivo de la unidad. Merge no destructivo: respetá lo que ya está, completá, marcá lo cambiado.

> **Cita obligatoria al escribir (Mode C es el caso central de procedencia).** Cada afirmación que escribas lleva su cita `[code · ruta#símbolo ~Lnn]` apuntando al lugar exacto del que la derivaste — el **símbolo** que estás leyendo en ese momento es el ancla. Para flujos (07), una cita por paso. Lo que no puedas anclar a un símbolo concreto **no se escribe como hecho**: `[inferred · inferido → 10]`. Ver `provenance.md`.

---

## Tests como fuente (la mejor para reglas)

Un test es la fuente **más fuerte** de reglas de negocio: la implementación te dice qué hace el código (bugs incluidos), el test te dice qué **debería** hacer (el contrato). El nombre del test suele ser la regla en castellano y la aserción es un ejemplo concreto.

- **Durante el trazado**, buscá también los tests de la feature por convención: `*.test.*`, `*.spec.*`, `*_test.*`, `test/`, `tests/`, `__tests__/`, `spec/`.
- **Una regla derivada de un test cita el test**: `[code · tests/payments.test.ts#"no aplica cupón dos veces"]`. Mismo formato de procedencia, evidencia más fuerte.
- El test **rellena parte del PORQUÉ sin inventar** — el nombre codifica intención.

### Si no hay tests (manejar todos los casos)

| Caso | Qué hace |
|---|---|
| Hay tests de la feature | Fuente **primaria**; la regla cita el test. |
| **No hay tests** (el proyecto no tiene) | Deriva de la implementación, pero marca la regla **`⚠ sin test`** (documenta *lo que hace*, no *lo que debería*). |
| Hay tests, pero no de esta feature | impl-only para esta feature, marcada `⚠ sin test`. |
| Tests triviales / solo smoke | Evidencia **débil**: no afirmes intención que el test no prueba. |

El marcador **`⚠ sin test`** vive pegado a la regla y **se auto-limpia**: cuando se agrega el test, el próximo Update se lo saca. La métrica agregada (cuántas reglas tienen test) la reporta el Audit on-demand (ver `quality-rubric.md`). **No** se crea un archivo de "huecos de test" — se desincronizaría, justo lo que la skill combate.

---

## El QUÉ vs el PORQUÉ (no-invención)

El código te da el **QUÉ**: qué entidades hay, qué rutas existen, qué validaciones corren. No te da el **PORQUÉ**: por qué ese `if` valida dos veces el cupón, por qué esa decisión de diseño.

- ¿Pregunta respondible por el usuario? → preguntala; la respuesta va a `09_decisiones` (decisión documentada).
- ¿No hay respuesta o el usuario no está? → va a `10_preguntas_abiertas.md` como duda.
- **Suposiciones**: si inferís intención del código, marcala con `**Suposición:**` y registrala en `09` (con origen y cómo validarla). **Nunca** la escribas como hecho.

---

## Escalado en Mode C (notario, no consultor)

Documentando código existente sos **notario**: registrás la realidad. Si detectás un techo de escalado (estado en memoria, N+1, sin colas/caché), **no rediseñás** — lo registrás:
- como **riesgo** en `09` o **pregunta** en `10` (ej: "estado en memoria → bloquea escalado horizontal, ¿se va a multi-instancia?"),
- **nunca** en `08` como si la solución ya estuviera implementada.

Solo cuando `trajectory = semilla | produccion` se activa el **checklist de escalado** que dispara estas preguntas/riesgos. Una demo descartable no los genera.
