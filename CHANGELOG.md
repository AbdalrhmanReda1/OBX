# Changelog

All notable changes to OBX are documented here.

## [1.0.0] — 2024

### Initial Release — Autonomous Runtime Intelligence for Python

**Core Systems**
- Runtime tracer with < 5% overhead
- Crash Shield with root-cause analysis for 15+ exception types
- Memory monitor with leak detection
- Performance analyzer with bottleneck detection and heatmap
- Logic Intelligence Engine via AST analysis
- Execution Recorder with state snapshots and diff
- OBX Health Scoring: Stability, Performance, Risk, Logic, and OBX Index

**CLI**
- `obx run` — execute scripts with full intelligence
- `obx analyze` — static logic analysis
- `obx score` — compute OBX Health Score
- `obx report` — generate JSON and Markdown reports
- `obx doctor` — environment diagnostics
- `obx benchmark` — measure script performance

**Integrations**
- GitHub Badge generator
- GitHub Actions compatible
- WebhookPlugin for external notifications
- Plugin API for custom extensions

**Quality**
- Full type hints (mypy strict compatible)
- Python 3.8–3.12 support
- Comprehensive test suite
- Zero external service dependencies
