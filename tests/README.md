# tests/ — red de regresión de la skill

`check_skill.py` valida la **integridad de la skill misma** y corre los goldens de
conformancia. Es dev-tooling del repo de chronicle (CI + contribuyentes), **no** el
checker que corre en proyectos de usuarios — los `assets/` siguen siendo
solo-markdown. Solo stdlib, sin dependencias.

## Correr

```bash
python3 tests/check_skill.py          # exit 0 si todo pasa, 1 si algo falla
python3 tests/check_skill.py --root /otra/copia
```

## Qué chequea

| Check | Qué atrapa |
|---|---|
| golden: KB conformance | que un checker conforme produzca `conformance/expected.json` desde `sample-kb/` (cobertura + cross-ref) |
| golden: fingerprint | normalización + SHA-256 contra `conformance/fingerprint/expected.json` |
| golden: trace-map resolution | resolución citación→mapa contra `conformance/trace-map/expected.json` (foreign key anti-fabricación) |
| links: asset references resolve | toda ruta `assets/*.md\|json\|js` citada en `SKILL.md`/`README`/assets existe (link roto = falla) |
| structure: frontmatter fields | `SKILL.md` tiene `name`/`description`/`version` |
| structure: version consistency | la versión de `SKILL.md` == el badge del `README` |
| anti-drift: no stale phrases | que no reaparezcan frases viejas ya corregidas (ej. "10 nodos canónicos") |

## Antes de un PR

Corré `python3 tests/check_skill.py` y que dé verde. CI lo corre solo en cada push/PR
(`.github/workflows/skill-check.yml`).

## Extender

Agregá una función `() -> (ok: bool, detalle: str)` y sumala a la lista `CHECKS`.
Lo que no se cubre todavía (mejora futura): validar referencias a secciones
(`archivo.md §N`) contra los headings reales del archivo target.
