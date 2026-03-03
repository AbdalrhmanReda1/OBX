<div align="center">

```
 ██████╗ ██████╗ ██╗  ██╗
██╔═══██╗██╔══██╗╚██╗██╔╝
██║   ██║██████╔╝ ╚███╔╝ 
██║   ██║██╔══██╗ ██╔██╗ 
╚██████╔╝██████╔╝██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
```

# OBX

### Autonomous Runtime Intelligence for Python

The first local-first engine that transforms any Python application into a  
**self-monitoring · self-diagnosing · self-scoring system** — in one line.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/github/license/AbdalrhmanReda1/OBX?color=green)](LICENSE)
[![OBX Score](https://img.shields.io/badge/OBX%20Score-92%2F100-brightgreen)]()

**Stop monitoring. Start understanding.**

</div>

---

## Why OBX Exists

Modern debugging is reactive.

Something crashes.  
You open logs.  
You inspect stack traces.  
You guess.

OBX changes that.

Instead of only showing *what* happened, OBX analyzes behavior, detects instability patterns, and produces **actionable intelligence** about *why* it happened — and what to fix.

---

## What Makes OBX Different?

| Category | Question Answered |
|-----------|-------------------|
| Monitoring Tools | What happened? |
| Profilers | Where is it slow? |
| Tracing Systems | How did the request flow? |
| **OBX** | **Why is this happening — and what should I do?** |

OBX creates a new DevTools category:

> **Autonomous Runtime Intelligence**

---

## One Line to Activate

```python
from obx import enable
enable()
```

No dashboards.  
No agents.  
No config files.  
No cloud required.

---

## Core Capabilities

### Runtime Intelligence Engine
- Function call tracing
- Execution flow awareness
- Exception interception
- Behavioral fingerprinting
- Lightweight runtime sampling

### Crash Shield
Intercepts every exception and generates structured diagnostics:

```
[CRITICAL] Infinite recursion detected
  @ user_service.py:45
  Suggestion: Add a base case or refactor recursive logic

[HIGH] Memory growth anomaly detected
  @ db/session.py:112
  Suggestion: Ensure sessions are properly closed
```

### OBX Health Score

Every execution produces a composite intelligence score:

```
Stability     94
Performance   88
Logic         91
Risk           8

OBX Index     92.1 / 100
```

Add a badge to your README:

```markdown
![OBX Score](https://img.shields.io/badge/OBX%20Score-92%2F100-brightgreen)
```

---

### Logic Intelligence Engine
Static analysis that detects:
- Unreachable code
- Always-true / always-false conditions
- Deep nesting patterns
- Identity comparison misuse
- High complexity functions

---

### Performance Intelligence
- Function heatmap
- Bottleneck detection
- Repeated-call anomaly detection
- Memory growth monitoring
- Optimization suggestions

---

### Execution Snapshots

```python
from obx import snapshot

snapshot("before", {"users": count_users()})
run_migration()
snapshot("after", {"users": count_users()})
```

---

### Modes

```python
enable(mode="dev")      # Full intelligence output
enable(mode="prod")     # Minimal overhead
enable(mode="silent")   # Internal tracking only
```

---

## CLI

```bash
obx run app.py
obx analyze ./src
obx score ./src
obx report --json
obx report --markdown --output report.md
obx doctor
obx benchmark app.py --iterations 5
```

---

## Architecture

```
obx/
├── core/
├── runtime/
├── intelligence/
├── performance/
├── logic/
├── shield/
├── recorder/
├── scoring/
├── plugins/
├── reporting/
├── cli/
├── config/
└── benchmarks/
```

### Design Principles

- Local-first intelligence
- Actionable insights over raw metrics
- Minimal runtime overhead
- Clean modular architecture
- Fully typed codebase
- Python 3.8+ compatible

---

## Performance

| Mode | Estimated CPU Overhead |
|------|-----------------------|
| dev  | < 3% |
| prod | < 1% |
| silent | < 0.5% |

Benchmark locally:

```bash
python -m obx.benchmarks.overhead
```

---

## Privacy & Security

- No external data transmission
- No telemetry
- No analytics
- Automatic sensitive-key redaction in production mode

Your code never leaves your machine.

---

## Installation

```bash
pip install obx-dev
```

Requirements: Python 3.8+

---

## Roadmap

- v1.1 — Adaptive sampling tracer
- v1.2 — Advanced anomaly detection
- v1.3 — GitHub Action intelligence mode
- v2.0 — Optional cloud intelligence layer

---

## Contributing

```bash
git clone https://github.com/AbdalrhmanReda1/OBX
cd OBX
pip install -e .
pytest tests/
```

---

## Author

**Abdalrhman Reda**

GitHub: https://github.com/AbdalrhmanReda1  
Telegram: https://t.me/o7_4l  

---

## License

MIT License

---

<div align="center">

**OBX — Autonomous Runtime Intelligence for Python**

Built for developers who want answers — not dashboards.

</div>
