# Changelog

All notable changes to `scriptkit` are documented here. Versions follow
[Semantic Versioning](https://semver.org). Each released version has a git tag
(`vX.Y.Z`) that scripts pin against.

## [Unreleased]

## [0.2.0] — 2026-07-24

First **published** release. (v0.1.0 was tagged locally during setup but never
pushed to GitHub; the first tag published to the remote is v0.2.0, so that is the
baseline every script pins against.)

Initial extraction of the common script infrastructure into an installable
package.

### Added
- `ScriptSettings` — frozen-dataclass config base with a `dir_base` → `data/` /
  `output/` path cascade.
- `build_parser_from_settings` / `parse_settings` — auto-generate a CLI and
  environment-variable wiring from a dataclass (precedence: CLI > env > default),
  now resolving `default_factory` fields such as `dir_base`.
- `get_logger` / `set_log_level` — RichLogger when installed, otherwise a stdlib
  fallback that still answers the semantic vocabulary (`stage`, `metric`, …) via
  `[TAG]` prefixes.
- `timestamp` — compact UTC stamps at year → second granularity.
- `scriptkit.azure.get_credential` — lazy `DefaultAzureCredential` helper.
- Thin `templates/script_template.py` with a PEP 723 header for `uv run`.
