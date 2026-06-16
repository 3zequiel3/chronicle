# Checker Spec — el contrato del chequeo mecánico (runtime-agnóstico)

Define **qué debe hacer** el chequeo mecánico de `chronicle`, sin atarlo a ningún lenguaje. chronicle **no shippea un ejecutable** — genera el checker a medida en el runtime que el proyecto ya usa (Node, Python, Go…) y lo **auto-verifica contra un golden fixture** antes de confiar en él. Esto da portabilidad (Windows sin imponer Python), seguridad de cadena de contribuciones (la skill es solo-markdown, auditable a ojo) y correctitud verificada por generación.

> El checker es **mecánico y determinista**: git + regex + hash, **cero LLM, cero tokens**. Por eso puede ser un gate de CI real. Lo caro (verificar correctitud, generar doc) es otra cosa y vive en `verification.md` / la generación del agente.

---

## 1. Entradas

| Entrada | De dónde | Obligatoria |
|---|---|---|
| Directorio de la KB | `knowledge-base/` | sí |
| Config | `knowledge-base/.chronicle/checks.json` | no (defaults) |
| Ledger | `knowledge-base/.chronicle/verification.json` | no (staleness lo necesita) |
| `ref` de git | del ledger o argumento | no (sin git → modo full) |

---

## 2. Chequeos (todos mecánicos)

### 2.1 Cobertura de citas
Extrae las citas con la gramática de `provenance.md`:

```
\[(code|doc|user|inferred) · ([^\]]+)\]
```

**Unidad de afirmación** (definición determinista para contar): en los nodos 04-09, cada **ítem codificado** cuenta como una afirmación factual. Operacionalmente, una línea que empieza con `- **<CÓDIGO>**` (ej. `- **RN-PAGOS-01**`, `- **DD-02**`) o un heading de entidad/endpoint. Cada afirmación **debe** tener una cita en su bloque o estar marcada `[inferred · …]`.

- `claims` = total de unidades de afirmación.
- `cited` = las que tienen una cita (cualquier tipo) en su bloque.
- `uncited` = afirmaciones **sin cita ni marca `inferred`** → **defecto**.
- `value` = `cited / claims`.

### 2.2 Consistencia cruzada
Resuelve cada referencia a un código:
- toda `RN-XXX-NN` referenciada en 06/07 existe como definición en 05,
- toda `US-NNN` enlazada resuelve a una historia en 06,
- toda `DD-NN` referenciada existe en 09.

`broken` = cantidad de referencias que no resuelven; `items` = lista `"origen → destino-roto"`.

### 2.3 Staleness
Requiere ledger. Con git: `git diff <ref> --name-only` (sin `..HEAD`, capta lo no commiteado) → archivos cambiados → citas `code` que apuntan a esos archivos → re-calcular **fingerprint normalizado** (§4) y comparar con el del ledger. Sin git: re-fingerprintear todas las citas `code`, acotado por presupuesto. Ver `staleness.md`.

`stale` = fingerprint distinto; `orphaned` = símbolo desaparecido. La salida es marca, **no reescritura**.

### 2.4 Cobertura por test (métrica, no defecto)
Cuenta reglas (05) con cita a un test vs reglas con `⚠ sin test`. Riesgo visible, no bloqueante salvo que se configure un mínimo.

---

## 3. Salida y exit codes

Reporte machine-readable (mismo contrato que `automation.md`):

```json
{
  "status": "pass | fail",
  "checks": {
    "citation_coverage": { "claims": 3, "cited": 2, "uncited": 1, "value": 0.67, "threshold": 0.80, "pass": false },
    "cross_ref":         { "broken": 1, "items": ["US-001 → RN-PAGOS-99"], "pass": false },
    "staleness":         { "stale": 0, "orphaned": 0, "pass": true, "items": [] }
  }
}
```

**Exit codes** (combinables por bitmask): `0` = todo pasa · `1` = staleness · `2` = cobertura · `3` = consistencia. El detalle siempre va en el reporte JSON.

---

## 4. Algoritmo de fingerprint normalizado (estable entre corridas)

El fingerprint es lo que comparten verificación (#3) y staleness (#5); tiene que dar **igual** ante un reformateo y **distinto** solo ante un cambio de lógica real.

1. Localizá el cuerpo del símbolo citado (la función/clase/región, no el archivo entero).
2. Normalizá, en este orden:
   - quitar comentarios (de línea y de bloque, según el lenguaje),
   - colapsar todo run de whitespace (espacios, tabs, newlines) a un solo espacio,
   - trim de bordes.
3. Hasheá el resultado con una **librería de hashing** del runtime (SHA-256). Sin librería disponible, una firma estructural normalizada como fallback.

El digest es el `fingerprint`. El `ref` (commit git de la corrida) se guarda junto, como línea base para el git fast-path.

---

## 5. Reglas de seguridad (obligatorias en el checker generado)

El checker corre sobre repos no confiables y se genera por código → es superficie de inyección. El checker generado **debe**:

1. **argv-arrays, nunca `sh -c` con interpolación.** Los paths y nombres de símbolo se pasan como argumentos de proceso, jamás concatenados a un string de shell. (Defensa contra command-injection vía path/símbolo crafteado.)
2. **Parsear las citas, no ejecutarlas.** Una cita es texto a matchear con la regex, nunca algo que se evalúe.
3. **Confinamiento a la raíz del repo.** Una cita `[code · ../../etc/passwd#x]` se **rechaza**: resolvé y operá solo dentro de la raíz del proyecto. Cualquier path que escape se reporta como cita inválida, no se abre.
4. **Hashing por librería**, no shelleando `sha256sum`/`shasum` con input interpolado.
5. **Sin red, sin escritura fuera de `.chronicle/`.** El checker solo lee la KB + el código y escribe el ledger.

---

## 6. Propiedad del ledger (regla dura)

`verification.json` lo escribe **únicamente el checker mecánico**. El LLM **nunca lo edita a mano** — solo lo **lee** para decidir qué re-verificar. Esto elimina el drift de "modelo manteniendo JSON de memoria": el estado de tooling es responsabilidad del tooling, no del lenguaje natural.

---

## 7. Protocolo de conformancia (auto-verificación antes de confiar)

Cuando el agente **genera** el checker para un proyecto, antes de usarlo:

1. Corré el checker generado contra `assets/conformance/sample-kb/` y compará su salida con `assets/conformance/expected.json` (campos `claims`, `cited`, `uncited`, `broken`, `items`).
2. Corré la normalización + hash sobre `assets/conformance/fingerprint/sample.js` y compará con `assets/conformance/fingerprint/expected.json` (el string `normalized` **y** el `fingerprint` SHA-256).
3. **Si todo coincide exacto → conformante**, usalo. **Si no → regenerá** el checker y repetí. No uses un checker que no pasó el fixture.

El fixture es **data, no código** (markdown + JSON + un snippet), runtime-agnóstico. Valida las tres piezas deterministas: extracción de citas, consistencia cruzada **y la normalización del fingerprint** (la parte más delicada). Lo único que no se fixtura es el `git diff` del staleness, que necesita un repo git real y se valida en el repo objetivo.

> Así el chequeo es turnkey **sin** que chronicle mantenga un script por plataforma, y su correctitud queda **verificada por generación** en vez de asumida.

---

## 8. Dos superficies, un solo binario (cierre de run + CI)

El checker corre en **dos momentos**, y debe ser el **mismo binario** en ambos (si divergen, el cierre miente):

1. **Cierre de run (atrapada temprana)** — al terminar cualquier modo generador, antes de declarar la KB completa. Es el nivel mecánico del auto-chequeo final (`edge-cases.md`). **Fail-closed**: no se declara "completo" con el checker en rojo.
2. **CI / pre-commit (atrapada real)** — corre sin el modelo, reproducible por el usuario. Es el enforcement de verdad; el cierre de run es solo el adelanto.

> **Por qué las dos.** En una sesión pelada, "correr el checker" sigue siendo una instrucción que el LLM ejecuta — el determinismo solo muerde cuando hay una superficie independiente. Por eso el cierre de run **persiste** su resultado y CI lo **re-corre**: lo que una sesión saltee, lo caza el próximo commit.

### Persistencia del resultado

El checker escribe su última corrida en `knowledge-base/.chronicle/last-check.json` (distinto del `verification.json`, que es el ledger de verificación/staleness). Lo escribe **solo el checker**, nunca el LLM (misma regla que §6):

```json
{ "ran_at": "<timestamp>", "ref": "<git commit>", "status": "pass|fail",
  "checks": { "citation_coverage": {...}, "cross_ref": {...}, "existence": {...} } }
```

El próximo run y CI comparan contra este archivo. Si el proyecto aún no tiene checker generado, el cierre corre los chequeos con tools deterministas (grep/regex) como equivalente y **ofrece generar** el checker persistente para que CI los re-corra.
