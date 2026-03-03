from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
err_console = Console(stderr=True)

LOGO = """
 ██████╗ ██████╗ ██╗  ██╗
██╔═══██╗██╔══██╗╚██╗██╔╝
██║   ██║██████╔╝ ╚███╔╝ 
██║   ██║██╔══██╗ ██╔██╗ 
╚██████╔╝██████╔╝██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝"""


def _print_logo() -> None:
    console.print(f"[bold bright_red]{LOGO}[/]")
    console.print(
        "  [bold white]Autonomous Runtime Intelligence[/]  [dim]v1.0.0[/]\n"
        "  [dim]by Abdalrhman Reda · github.com/AbdalrhmanReda1[/]\n"
    )


@click.group()
@click.version_option(version="1.0.0", prog_name="obx")
def cli() -> None:
    pass


@cli.command()
@click.argument("script", type=click.Path(exists=True))
@click.option("--mode", "-m", default="dev", type=click.Choice(["dev", "prod", "silent"]))
@click.option("--safe", is_flag=True, help="Enable safe mode (prevent crashes)")
@click.option("--report", "-r", is_flag=True, help="Show full report after run")
@click.option("--json", "output_json", is_flag=True, help="Output report as JSON")
def run(script: str, mode: str, safe: bool, report: bool, output_json: bool) -> None:
    """Run a Python script with OBX intelligence enabled."""
    _print_logo()
    console.print(f"  [cyan]→[/] Running [bold]{script}[/] in [bold]{mode}[/] mode\n")

    script_path = Path(script).resolve()
    sys.path.insert(0, str(script_path.parent))

    os.environ["OBX_MODE"] = mode

    import importlib.util

    spec = importlib.util.spec_from_file_location("__obx_target__", script_path)
    if spec is None or spec.loader is None:
        err_console.print(f"[red]Cannot load script: {script}[/]")
        sys.exit(1)

    import obx

    obx.enable(mode=mode, safe_mode=safe)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except SystemExit:
        pass
    except Exception as exc:
        from obx.shield.crash_shield import get_crash_shield
        get_crash_shield().intercept(exc)
    finally:
        if output_json:
            output = obx.report(output="json")
            console.print(output)
        elif report:
            obx.report()


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--min-score", default=0, type=int, help="Fail if score below threshold")
def analyze(path: str, output_json: bool, min_score: int) -> None:
    """Analyze a Python file or project directory."""
    _print_logo()
    console.print(f"  [cyan]→[/] Analyzing: [bold]{path}[/]\n")

    from obx.logic.engine import get_logic_engine
    from obx.scoring.engine import get_scoring_engine

    engine = get_logic_engine()
    target = Path(path)

    if target.is_file():
        issues = engine.analyze_file(str(target))
    else:
        issues = engine.analyze_directory(str(target))

    logic_score = engine.compute_logic_score(issues)

    if output_json:
        result = {
            "path": path,
            "logic_score": logic_score,
            "total_issues": len(issues),
            "issues": [i.to_dict() for i in issues],
        }
        console.print(json.dumps(result, indent=2))
        return

    if not issues:
        console.print("  [bold green]✓ No logic issues detected[/]\n")
    else:
        table = Table(
            show_header=True,
            header_style="bold white",
            border_style="bright_black",
        )
        table.add_column("File", style="dim", max_width=40)
        table.add_column("Line", justify="right", width=6)
        table.add_column("Severity", width=10)
        table.add_column("Issue")
        table.add_column("Suggestion", style="cyan", max_width=40)

        severity_colors = {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "dim",
        }

        for issue in sorted(issues, key=lambda x: x.severity):
            color = severity_colors.get(issue.severity, "white")
            table.add_row(
                Path(issue.file).name,
                str(issue.lineno),
                f"[{color}]{issue.severity.upper()}[/]",
                issue.title,
                issue.suggestion,
            )

        console.print(table)

    console.print(f"\n  [bold]Logic Score: {logic_score:.0f} / 100[/]\n")

    if min_score and logic_score < min_score:
        console.print(f"  [red]✗ Score {logic_score:.0f} below threshold {min_score}[/]")
        sys.exit(1)


@cli.command()
def doctor() -> None:
    """Run OBX health diagnostics on the current environment."""
    _print_logo()
    console.print("  [bold]Running Environment Diagnostics...[/]\n")

    checks = []

    import sys as _sys
    py_ver = _sys.version_info
    checks.append((
        "Python version",
        f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}",
        py_ver >= (3, 8),
    ))

    try:
        import psutil
        checks.append(("psutil", psutil.__version__, True))
    except ImportError:
        checks.append(("psutil", "NOT INSTALLED", False))

    try:
        import rich
        rich_ver = getattr(rich, "__version__", getattr(rich, "version", "available"))
        checks.append(("rich", rich_ver, True))
    except ImportError:
        checks.append(("rich", "NOT INSTALLED", False))

    try:
        import click
        checks.append(("click", click.__version__, True))
    except ImportError:
        checks.append(("click", "NOT INSTALLED", False))

    try:
        import psutil as _psutil
        mem = _psutil.virtual_memory()
        checks.append(("Available Memory", f"{mem.available // 1_048_576} MB", True))
        cpu = _psutil.cpu_count()
        checks.append(("CPU cores", str(cpu), True))
    except Exception:
        pass

    table = Table(
        show_header=True,
        header_style="bold white",
        border_style="bright_black",
    )
    table.add_column("Check", style="cyan")
    table.add_column("Value")
    table.add_column("Status", justify="center")

    all_ok = True
    for name, value, ok in checks:
        status = "[green]✓[/]" if ok else "[red]✗[/]"
        table.add_row(name, value, status)
        if not ok:
            all_ok = False

    console.print(table)

    if all_ok:
        console.print("\n  [bold green]✓ Environment is ready for OBX[/]\n")
    else:
        console.print("\n  [bold yellow]⚠ Some dependencies are missing. Run: pip install obx[/]\n")


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--json", "output_json", is_flag=True)
def score(path: str, output_json: bool) -> None:
    """Compute and display the OBX Health Score for a project."""
    _print_logo()

    from obx.logic.engine import get_logic_engine
    from obx.scoring.engine import get_scoring_engine
    from obx.core.types import OBXScores

    engine = get_logic_engine()
    target = Path(path)

    if target.is_file():
        issues = engine.analyze_file(str(target))
    else:
        issues = engine.analyze_directory(str(target))

    logic_score = engine.compute_logic_score(issues)

    scores = OBXScores(
        stability=100.0,
        performance=100.0,
        risk=0.0,
        logic=logic_score,
    )

    if output_json:
        console.print(get_scoring_engine().to_json(scores))
        return

    from obx.reporting.reporter import get_terminal_reporter
    get_terminal_reporter().print_scores(scores)

    badge = get_scoring_engine().badge_url(scores)
    console.print(f"\n  [dim]Badge URL:[/] {badge}\n")
    console.print(
        f"  [dim]README badge:[/] [cyan]![OBX Score]({badge})[/]\n"
    )


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--json", "output_json", is_flag=True)
@click.option("--markdown", "output_md", is_flag=True)
@click.option("--output", "-o", type=click.Path(), default=None)
def report(path: str, output_json: bool, output_md: bool, output_o: Optional[str] = None) -> None:
    """Generate a full OBX intelligence report."""
    _print_logo()

    from obx.logic.engine import get_logic_engine
    from obx.scoring.engine import get_scoring_engine
    from obx.core.types import OBXScores
    from obx.reporting.reporter import get_json_reporter, get_terminal_reporter

    engine = get_logic_engine()
    target = Path(path)

    if target.is_file():
        logic_issues = engine.analyze_file(str(target))
    else:
        logic_issues = engine.analyze_directory(str(target))

    logic_score = engine.compute_logic_score(logic_issues)
    scores = OBXScores(stability=100.0, performance=100.0, risk=0.0, logic=logic_score)

    from obx.core.types import Issue, IssueCategory, Severity
    issues = [
        Issue(
            category=IssueCategory.LOGIC,
            severity=Severity(i.severity),
            title=i.title,
            description=i.description,
            location=f"{i.file}:{i.lineno}",
            suggestion=i.suggestion,
        )
        for i in logic_issues
    ]

    if output_md:
        result = get_scoring_engine().to_markdown(scores)
    elif output_json:
        result = get_json_reporter().generate(scores=scores, issues=issues)
    else:
        get_terminal_reporter().print_scores(scores)
        get_terminal_reporter().print_issues(issues)
        return

    if output_o:
        Path(output_o).write_text(result, encoding="utf-8")
        console.print(f"  [green]✓ Report saved to {output_o}[/]")
    else:
        console.print(result)


@cli.command()
@click.argument("script", type=click.Path(exists=True))
@click.option("--iterations", "-n", default=3, type=int)
def benchmark(script: str, iterations: int) -> None:
    """Benchmark a Python script and show performance metrics."""
    _print_logo()
    console.print(f"  [cyan]→[/] Benchmarking [bold]{script}[/] × {iterations}\n")

    import importlib.util
    import statistics

    script_path = Path(script).resolve()
    sys.path.insert(0, str(script_path.parent))

    times = []

    for i in range(1, iterations + 1):
        spec = importlib.util.spec_from_file_location(f"__bench_{i}__", script_path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)

        start = time.perf_counter()
        try:
            spec.loader.exec_module(module)
        except (SystemExit, Exception):
            pass
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        console.print(f"  Run {i}: [yellow]{elapsed * 1000:.2f}ms[/]")

    if len(times) >= 2:
        console.print(f"\n  [bold]Results:[/]")
        console.print(f"  Min:    [green]{min(times) * 1000:.2f}ms[/]")
        console.print(f"  Max:    [yellow]{max(times) * 1000:.2f}ms[/]")
        console.print(f"  Mean:   [cyan]{statistics.mean(times) * 1000:.2f}ms[/]")
        console.print(f"  Stdev:  [dim]{statistics.stdev(times) * 1000:.2f}ms[/]\n")


if __name__ == "__main__":
    cli()
