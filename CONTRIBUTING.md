# Cómo contribuir

¡Gracias por tu interés en Vivero Seedbank! El proyecto está en etapa alfa y cualquier aporte suma: código, pruebas con datos reales, documentación, traducciones o ideas.

## Antes de empezar

- Leé el [Código de conducta](CODE_OF_CONDUCT.md).
- Para preguntas o ideas generales, usá el [foro de Discussions](https://github.com/AdmGrow/vivero-seedbank/discussions).
- Para errores concretos o propuestas puntuales, abrí un [issue](https://github.com/AdmGrow/vivero-seedbank/issues) usando la plantilla que corresponda.
- Si encontrás un problema de seguridad, **no abras un issue público**: seguí [SECURITY.md](SECURITY.md).

## Cómo enviar un cambio (pull request)

1. Hacé un fork del repositorio y creá una rama con un nombre descriptivo (por ejemplo `validar-gramos`).
2. Hacé cambios chicos y enfocados en un solo tema.
3. Instalá en modo desarrollo y corré los tests: `pip install -e ".[dev]"` y `python -m pytest`. Si agregás funcionalidad, sumá tests en `tests/`.
4. Si cambiás el comportamiento, actualizá el `README.md` y agregá una línea en `CHANGELOG.md` (sección "Unreleased").
5. Abrí el pull request completando la plantilla.

## Estilo

- Python 3.10+, solo biblioteca estándar (sin dependencias externas salvo que se discuta antes). `pytest` es solo para desarrollo.
- El código está en `src/vivero_seedbank/` y los tests en `tests/`. El CI de GitHub Actions corre los tests en Python 3.10–3.13 en cada pull request.
- Código claro y nombres descriptivos. Comentarios y documentación en español (se agradece también en inglés).
- Mensajes de commit cortos que expliquen qué cambia, por ejemplo: `lots: validar que germinadas <= celdas`.

## Datos

No subas datos personales ni información privada (nombres de productores, direcciones, teléfonos, emails). Para ejemplos, usá datos inventados como los de `examples/lotes_ejemplo.csv`.

## Licencia

Al contribuir aceptás que tu aporte se publique bajo la [licencia MIT](LICENSE) del proyecto.

---

**English:** Contributions are welcome in English too. Use [Discussions](https://github.com/AdmGrow/vivero-seedbank/discussions) for questions, issues for bugs/features, and pull requests for small, focused changes. Follow the [Code of Conduct](CODE_OF_CONDUCT.md) and report security problems privately as described in [SECURITY.md](SECURITY.md). Contributions are licensed under MIT.
