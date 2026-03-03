<div align="center">

```
 ██████╗ ██████╗ ██╗  ██╗
██╔═══██╗██╔══██╗╚██╗██╔╝
██║   ██║██████╔╝ ╚███╔╝ 
██║   ██║██╔══██╗ ██╔██╗ 
╚██████╔╝██████╔╝██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
```

**Autonomous Runtime Intelligence for Python**

[![PyPI version](https://img.shields.io/pypi/v/obx?color=brightred&label=obx)](https://pypi.org/project/obx/)
[![Python](https://img.shields.io/pypi/pyversions/obx?color=blue)](https://pypi.org/project/obx/)
[![License](https://img.shields.io/github/license/AbdalrhmanReda1/obx?color=green)](LICENSE)
[![OBX Score](https://img.shields.io/badge/OBX%20Score-97%2F100-brightgreen)](https://obx.dev)

*Stop monitoring. Start understanding.*

</div>

---

## What is OBX?

OBX is not another monitoring tool. It is the world's first **Autonomous Runtime Intelligence** engine for Python — a system that **thinks about your code** so you don't have to.

While Sentry tells you *what* crashed, and Datadog tells you *when* it crashed, **OBX tells you *why* it happened — and what to do about it**.

```python
from obx import enable

enable()

# That's it. OBX is now watching your application.
```

OBX creates a new category in the DevTools landscape:

| Tool | What it answers |
|------|----------------|
| Monitoring (Sentry, Datadog) | *What* happened? |
| Profiling (cProfile, py-spy) | *Where* is it slow? |
| Tracing (Jaeger, Zipkin) | *How* did the request flow? |
| **OBX — Autonomous Runtime Intelligence** | ***Why** is this happening? What should I do?* |

---

## Features

### Zero Setup Intelligence
One line. No configuration. No dashboards. No agents.

```python
from obx import enable
enable()
```

OBX immediately begins:
- Tracing all function calls and execution paths
- Monitoring memory growth and patterns
- Intercepting and analyzing every exception
- Building your application's behavioral fingerprint

### Crash Shield
OBX intercepts every exception, performs root-cause analysis, and produces actionable diagnostics.

```
💀 [CRITICAL]  Infinite recursion detected
       @ user_service.py:45 in get_user_profile
       → Add a base case or increase sys.setrecursionlimit() cautiously

⚠  [HIGH]  Memory leak detected
       @ db/session.py:112 in create_session
       → SQLAlchemy sessions not closed — add session.close() in finally block
```

### OBX Health Score
Every session produces a composite score across four intelligence dimensions:

```
┌────────────────────────────────────────────────────────┐
│  Component         Score    Visual              Status  │
├────────────────────────────────────────────────────────┤
│  Stability          94      ████████████████░░░░  OK   │
│  Performance        88      ██████████████░░░░░░  OK   │
│  Logic              91      ██████████████████░░  OK   │
│  Risk (lower=better) 8      ██░░░░░░░░░░░░░░░░░░  OK   │
├────────────────────────────────────────────────────────┤
│  OBX Index        92.1 / 100    ✅  EXCELLENT          │
└────────────────────────────────────────────────────────┘
```

Add this badge to your `README.md`:

```markdown
![OBX Score](https://img.shields.io/badge/OBX%20Score-92%2F100-brightgreen)
```

### Logic Intelligence Engine
OBX performs static analysis to detect code patterns that cause runtime failures before they happen:

- Infinite loops without break conditions
- Always-true / always-false conditions (unreachable code)
- Deeply nested loop structures (3+ levels)
- Functions with excessive complexity
- Identity comparisons on literals (`is 42` instead of `== 42`)

### Performance Intelligence
- Automatic bottleneck detection
- Function-level heatmap
- Memory growth analysis and leak detection
- High-frequency call detection
- Actionable optimization suggestions

### Execution Recorder
Capture state snapshots and compare them across time:

```python
from obx import enable, snapshot

enable()

snapshot("before_migration", {"user_count": get_user_count()})
run_migration()
snapshot("after_migration", {"user_count": get_user_count()})
```

### Production Mode
```python
enable(mode="prod")   # Minimal overhead, structured logs, no sensitive data
enable(mode="silent") # Zero output, internal tracking only
enable(mode="dev")    # Full intelligence output
```

### Plugin Architecture
```python
from obx.plugins import WebhookPlugin, get_plugin_registry

get_plugin_registry().register(
    WebhookPlugin(url="https://hooks.slack.com/your-webhook")
)
```

---

## Installation

```bash
pip install obx
```

**Requirements:** Python 3.8+ · No external services · No configuration files

---

## CLI

OBX ships with a professional CLI for static analysis, benchmarking, and CI/CD integration.

```bash
# Run script with full intelligence
obx run app.py

# Analyze a project for logic issues
obx analyze ./src

# Get OBX Health Score
obx score ./src

# Full report as JSON
obx report --json

# Full report as Markdown
obx report --markdown --output report.md

# System health check
obx doctor

# Benchmark a script
obx benchmark app.py --iterations 5
```

### GitHub Actions Integration

```yaml
name: OBX Intelligence Check

on: [push, pull_request]

jobs:
  obx-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install obx
      - run: obx analyze ./src --min-score 70
      - run: obx report --json --output obx-report.json
      - uses: actions/upload-artifact@v3
        with:
          name: obx-report
          path: obx-report.json
```

---

## Architecture

OBX is built on clean, modular architecture with complete separation of concerns.

```
obx/
├── core/           # Types, events, context — the foundation
├── runtime/        # Tracer and memory monitor
├── intelligence/   # Root-cause analysis and narrative engine
├── performance/    # Bottleneck detection and heatmap
├── logic/          # Static AST analysis engine
├── shield/         # Crash interception and classification
├── recorder/       # Timeline and state snapshots
├── scoring/        # OBX Index computation
├── plugins/        # Event-driven plugin system
├── reporting/      # Terminal, JSON, and Markdown output
├── cli/            # Professional CLI commands
├── config/         # Configuration management
└── benchmarks/     # Overhead verification suite
```

### Design Principles

- **Zero external dependencies** beyond `click`, `rich`, and `psutil`
- **< 5% runtime overhead** in production mode (benchmarked)
- **Event-driven architecture** — all subsystems communicate via typed events
- **Full type hints** throughout — compatible with mypy strict mode
- **Dependency isolation** — each module is independently testable
- **Python 3.8+ compatible** — no walrus operator, no 3.10+ match statements

---

## Performance & Trust

OBX is designed for production use. We take overhead seriously.

| Mode | CPU Overhead | Memory Impact | Tracing |
|------|-------------|---------------|---------|
| `dev` | < 3% | ~5MB | Full |
| `prod` | < 1% | ~2MB | Exceptions only |
| `silent` | < 0.5% | ~1MB | Minimal |

Run the built-in benchmark suite:

```bash
python -m obx.benchmarks.overhead
```

### Privacy & Security

- OBX **never** sends your code or data to external servers
- All intelligence is computed **locally**
- Production mode **automatically redacts** sensitive keys: `password`, `token`, `secret`, `key`
- No telemetry. No analytics. No phone-home.

---

## Comparison

| Feature | OBX | Sentry | Datadog | py-spy |
|---------|-----|--------|---------|--------|
| Zero setup | ✅ | ❌ | ❌ | ✅ |
| Root-cause analysis | ✅ | ❌ | Partial | ❌ |
| Human-language reports | ✅ | ❌ | ❌ | ❌ |
| Logic analysis (static) | ✅ | ❌ | ❌ | ❌ |
| Health Score | ✅ | ❌ | ❌ | ❌ |
| Local-only (no cloud) | ✅ | ❌ | ❌ | ✅ |
| Open source | ✅ | ✅ | ❌ | ✅ |
| Production safe | ✅ | ✅ | ✅ | ✅ |
| No dashboard required | ✅ | ❌ | ❌ | ✅ |

---

## API Reference

### `obx.enable()`

```python
obx.enable(
    mode: str = "dev",         # "dev" | "prod" | "silent"
    safe_mode: bool = False,   # Prevent app crashes via shield
    config: OBXConfig = None,  # Custom config object
)
```

### `obx.report()`

```python
obx.report(output="terminal")  # "terminal" | "json" | "markdown"
```

### `obx.score()`

```python
scores: OBXScores = obx.score()
print(scores.index)   # 92.1
print(scores.grade)   # "EXCELLENT"
```

### `obx.snapshot()`

```python
obx.snapshot("label", {"key": "value"})
```

### `OBXConfig`

```python
from obx.config import OBXConfig

config = OBXConfig(
    mode="prod",
    enable_tracer=True,
    enable_memory_monitor=True,
    memory_sample_interval=2.0,
    webhook_url="https://hooks.example.com/obx",
    excluded_modules=["third_party_lib"],
)
obx.enable(config=config)
```

---

## Contributing

We welcome contributions. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

```bash
git clone https://github.com/AbdalrhmanReda1/obx
cd obx
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Roadmap

- **v1.1** — VS Code extension, async-native tracer
- **v1.2** — OBX Cloud dashboard (optional, privacy-first)
- **v2.0** — Node.js support, Go support
- **v3.0** — OBX Universal via eBPF

---

## Author

**Abdalrhman Reda**

- GitHub: [@AbdalrhmanReda1](https://github.com/AbdalrhmanReda1)
- Telegram: [@o7_4l](https://t.me/o7_4l)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**OBX — Stop monitoring. Start understanding.**

*The first Autonomous Runtime Intelligence engine for Python.*

</div>
