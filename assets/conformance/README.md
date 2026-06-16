# Conformance fixture — golden test del checker

`sample-kb/` es una KB mínima con conteos **conocidos y deterministas**.
`expected.json` es la salida que un checker correcto debe producir sobre ella.

Uso (ver `../checker-spec.md` §7): cuando el agente genera el checker para un
proyecto, lo corre primero contra `sample-kb/` y compara con `expected.json`.
Si no coincide exacto, el checker está mal generado → regenerar.

Valida la lógica **pura-markdown y determinista**: extracción de citas
(cobertura) y consistencia cruzada (`sample-kb/` + `expected.json`), **más** la
normalización del fingerprint (`fingerprint/` + `fingerprint/expected.json`).
Lo único que no se fixtura es el `git diff` del staleness, que depende de un repo
git real y se valida en el repo objetivo.

Conteos esperados (por construcción de `sample-kb/`):
- 3 afirmaciones codificadas (`- **RN-...**`) en `05`; 2 con cita, 1 sin cita.
- `US-001` referencia `RN-PAGOS-01` (existe) y `RN-PAGOS-99` (no existe → rota).

Fingerprint esperado (`fingerprint/sample.js`):
- normalizar el cuerpo de `validateCoupon` (quitar comentarios, colapsar
  whitespace, trim) debe dar el string de `fingerprint/expected.json`, y su
  SHA-256 debe coincidir con el `fingerprint` de ese archivo. Así la parte más
  delicada del checker (normalización + hash) **sí** tiene golden test.
