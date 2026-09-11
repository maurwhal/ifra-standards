# Changelog

Notable changes to this project. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- Reading a Standard's PDF for its Maximum Acceptable Concentrations (added
  briefly, commit e7857e4) moved out into its own project,
  [ifra-standards-maximum-acceptable-concentrations-MAC](https://github.com/maurwhal/ifra-standards-maximum-acceptable-concentrations-MAC).
  This project stays the simple one: the list only.

## [0.1.0] - 2026-09-08

First release.

### Added
- `ifra-standards fetch`: get the whole IFRA Standards list in one or two
  requests and save it as CSV, JSON, or Excel.
- The list is fetched by reading the public Standards Library page. The page's
  access token changes often, so the tool reads a fresh one each run.
- `--explode-cas`: one row per CAS number.
- `ifra-standards pdfs`: download every Standard PDF into a folder.
- `ifra-standards diff`: compare two saved lists and show what changed.
- `ifra-standards token`: print the current access token (for troubleshooting).
- `--save-raw` / `--from-raw`: save the raw page, or read a saved one, so a run
  can be repeated offline.
- A double-click Windows app (`IFRA-Standards.exe`) that saves the CSV to the
  Desktop, built and attached to the release automatically.
- Python API: `fetch_standards()`, `write()`, `diff_standards()`, and CAS
  helpers with check-digit validation.

[Unreleased]: https://github.com/maurwhal/ifra-standards/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/maurwhal/ifra-standards/releases/tag/v0.1.0
