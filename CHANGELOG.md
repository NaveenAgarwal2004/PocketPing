# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-23

### Added
- **Undo Support**: Added a 30-second bounded `/undo` command to easily remove mistaken logs.
- **Rich Success Messages**: When an expense is logged, the bot now replies with your running daily total and transaction count instantly.
- **Smart Analytics**: `/today` now sorts your categories recursively by amount (most expensive at top) and displays percentage distribution.
- **CI Pipeline**: Fully integrated GitHub Actions CI pipeline that executes 97 automated tests on PR and Push.

### Changed
- **Architecture**: Separated presentation logic from Telegram interactions into an isolated `analytics.py` module.
- **Documentation**: Overhauled `README.md` to production quality with architectural diagram, feature sets, and deployment guidelines.
- **Code Quality**: Enforced strict `ruff` formatting and type hints across the entire repository.

### Removed
- Extraneous memory-leak loops: The duplicate caches actively clean themselves every 10 seconds, scaling beautifully on tiny containers.

## [1.0.0] - 2026-06-22

### Added
- Native Google Sheets backing structure.
- Render Free Tier polling setup via Flask daemon.
- Duplicate message detection within 5-second boundaries.
- Native parser matching descriptions, amounts, currencies, and account sources unconditionally of order.
