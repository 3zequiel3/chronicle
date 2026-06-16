# Reverse Documentation — Mode C (read-only, por funcionalidad)

Mode C documenta un **sistema ya construido que no tiene documentación**, leyendo el código en modo **read-only** y scopeando **por funcionalidad** (un corte vertical que cruza carpetas/lenguajes), no por módulo.

> **Regla madre (no negociable)**: el código se LEE pero NUNCA se modifica. El código dice el **QUÉ**; el usuario dice el **PORQUÉ**; nada se inventa.

---

## Por qué por funcionalidad y no por módulo

Una funcionalidad es un **corte vertical**: el checkout no vive en `pagos/`, vive en `pagos/` + `stock/` + `users/` + `notifications/`. Documentar por módulo fragmenta la historia; documentar por funcionalidad sigue el flujo real. Además, mapea exacto a los nodos colección de la KB (04, 05, 06, 07), que ya están organizados por funcionalidad.

> La organización por funcionalidad es un **lente conceptual**, no un espejo de las carpetas del código. Aunque el código sea un monolito desprolijo, la KB le impone el orden que el código todavía no tiene. No necesitás un código bien modularizado para documentarlo bien.

---

## Protocolo: anclaje → confirmación → trazado acotado → merge

### 1. Anclaje
Del nombre de la funcionalidad ("el checkout"), extraé términos de búsqueda y localizá el **punto de entrada** con búsqueda read-only (un endpoint, una ruta, un controller, un service, un keyword). No abras todavía medio repo: encontrá el hilo del que tirar.

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

### 3. Trazado acotado
Desde el punto de entrada confirmado, seguí **solo la cadena relacionada** con esa feature. Leé lo que el flujo toca, no lo que importa transitivamente.

- **Cross-language**: seguí la funcionalidad a través del límite de servicio/lenguaje (llamada REST del front TS → handler en Go → job en Python). No frenes en el borde de un lenguaje.
- **Regla de frontera**: cuando el trazado choca con **otra funcionalidad** (checkout llama a `inventory`), **no te metas a documentarla** — poné un cross-reference y pará. Si no, terminás documentando todo el sistema en un solo pase.

### 4. Merge (corte vertical, no destructivo)
Documentar una funcionalidad es una **actualización quirúrgica de varios nodos a la vez**, nunca una regeneración total:

| Nodo | Qué se escribe para la feature |
|---|---|
| 04 modelos-apis | entidades y contratos que la feature toca (`modelos/pago.md`, `contratos-api/pagos.md`) |
| 05 reglas-de-negocio | reglas detectadas en el código (`pagos.md` → `RN-PAGOS-NN`) |
| 06 funcionalidades | la historia de usuario / épica (`pagos.md` → `US-NNN`) |
| 07 flujos-principales | el flujo extremo a extremo (`pagos-checkout.md`) |

Si el nodo es archivo (sistema chico) se mergea en el archivo; si es carpeta, se escribe el archivo de la unidad. Merge no destructivo: respetá lo que ya está, completá, marcá lo cambiado.

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
