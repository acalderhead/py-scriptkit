# Changelog

All notable changes to `scriptkit` are documented here. Versions follow
[Semantic Versioning](https://semver.org). Each released version has a git tag
(`vX.Y.Z`) that scripts pin against.

## [Unreleased]

## [0.2.1] — 2026-07-24

### Changed
- `--help` now preserves the script docstring's layout (section headings and
  line breaks) instead of reflowing it into a single paragraph, while still
  showing each option's default. (New `_ScriptHelpFormatter`.)

### Fixed
- `get_logger` derives the logger name correctly on any OS when given a
  Windows-style path (previously only split on the host OS's separator).

## [0.2.0] — 2026-07-24

First published release: the common single-file-script infrastructure as an
installable, versioned package.

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
