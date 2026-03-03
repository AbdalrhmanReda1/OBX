from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from obx.core.types import Issue, OBXMode, OBXScores, Severity

_console = Console()
_err_console = Console(stderr=True)


def _severity_color(severity: Severity) -> str:
    return {
        Severity.CRITICAL: "bold red",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "dim",
    }.get(severity, "white")


def _grade_color(grade: str) -> str:
    return {
        "EXCELLENT": "bold bright_green",
        "GOOD": "bold green",
        "FAIR": "bold yellow",
        "POOR": "bold red",
        "CRITICAL": "bold bright_red",
    }.get(grade, "white")


def _score_bar(score: float, width: int = 20) -> str:
    filled = int((score / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


class TerminalReporter:
    def __init__(self, console: Optional[Console] = None) -> None:
        self._console = console or _console

    def print_banner(self, mode: OBXMode) -> None:
        banner = Text()
        banner.append("⚡ OBX", style="bold bright_red")
        banner.append(" Runtime Intelligence", style="bold white")
        banner.append(f"  [{mode.value.upper()}]", style="dim cyan")
        self._console.print(Panel(banner, border_style="bright_red", padding=(0, 2)))

    def print_scores(self, scores: OBXScores) -> None:
        table = Table(
            show_header=True,
            header_style="bold white",
            border_style="bright_black",
            padding=(0, 1),
        )
        table.add_column("Component", style="cyan", width=18)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Visual", width=24)
        table.add_column("Status", width=12)

        components = [
            ("Stability", scores.stability),
            ("Performance", scores.performance),
            ("Logic", scores.logic),
            ("Risk (lower=better)", 100 - scores.risk),
        ]

        for name, value in components:
            color = "green" if value >= 75 else "yellow" if value >= 55 else "red"
            bar = _score_bar(value)
            table.add_row(
                name,
                f"[{color}]{value:.0f}[/]",
                f"[{color}]{bar}[/]",
                f"[{color}]{'OK' if value >= 75 else 'WARN' if value >= 55 else 'FAIL'}[/]",
            )

        self._console.print(table)

        grade_color = _grade_color(scores.grade)
        self._console.print(
            f"\n  [dim]OBX Index[/]  [{grade_color}]{scores.index} / 100  {scores.grade}[/]\n"
        )

    def print_issues(self, issues: List[Issue], max_show: int = 10) -> None:
        if not issues:
            self._console.print("  [bold green]✓ No issues detected[/]")
            return

        self._console.print(f"\n  [bold]Issues Detected: {len(issues)}[/]\n")

        for issue in issues[:max_show]:
            color = _severity_color(issue.severity)
            icon = {"critical": "💀", "high": "⚠", "medium": "●", "low": "○"}.get(
                issue.severity.value, "·"
            )
            self._console.print(f"  [{color}]{icon} [{issue.severity.value.upper()}][/]  {issue.title}")
            if issue.location:
                self._console.print(f"       [dim]@ {issue.location}[/]")
            if issue.suggestion:
                self._console.print(f"       [cyan]→ {issue.suggestion}[/]")
            self._console.print()

        if len(issues) > max_show:
            self._console.print(f"  [dim]... and {len(issues) - max_show} more[/]")

    def print_narrative(self, narrative: str) -> None:
        self._console.print(
            Panel(
                f"[italic]{narrative}[/italic]",
                title="[bold cyan]OBX Intelligence Report[/]",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    def print_profile_top(self, profiles: Dict[str, Any], top_n: int = 5) -> None:
        if not profiles:
            return

        self._console.print("\n  [bold]Top Functions by Time[/]\n")
        table = Table(
            show_header=True,
            header_style="bold white",
            border_style="bright_black",
            padding=(0, 1),
        )
        table.add_column("Function", style="cyan")
        table.add_column("Calls", justify="right", style="white")
        table.add_column("Total (ms)", justify="right", style="yellow")
        table.add_column("Avg (ms)", justify="right", style="dim")

        sorted_profiles = sorted(profiles.values(), key=lambda p: p.total_time, reverse=True)

        for profile in sorted_profiles[:top_n]:
            table.add_row(
                f"{profile.module}.{profile.name}",
                str(profile.call_count),
                f"{profile.total_time * 1000:.1f}",
                f"{profile.avg_time * 1000:.2f}",
            )

        self._console.print(table)

    def print_success(self, message: str) -> None:
        self._console.print(f"  [bold green]✓[/] {message}")

    def print_error(self, message: str) -> None:
        self._console.print(f"  [bold red]✗[/] {message}")

    def print_info(self, message: str) -> None:
        self._console.print(f"  [dim cyan]→[/] {message}")


class JSONReporter:
    def generate(
        self,
        scores: OBXScores,
        issues: List[Issue],
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        data: Dict[str, Any] = {
            "obx_version": "1.0.0",
            "timestamp": time.time(),
            "scores": {
                "index": scores.index,
                "grade": scores.grade,
                "stability": scores.stability,
                "performance": scores.performance,
                "risk": scores.risk,
                "logic": scores.logic,
            },
            "issues": [
                {
                    "category": i.category.value,
                    "severity": i.severity.value,
                    "title": i.title,
                    "description": i.description,
                    "location": i.location,
                    "suggestion": i.suggestion,
                }
                for i in issues
            ],
            "summary": {
                "total_issues": len(issues),
                "critical": sum(1 for i in issues if i.severity == Severity.CRITICAL),
                "high": sum(1 for i in issues if i.severity == Severity.HIGH),
                "medium": sum(1 for i in issues if i.severity == Severity.MEDIUM),
                "low": sum(1 for i in issues if i.severity == Severity.LOW),
            },
        }
        if extra:
            data.update(extra)
        return json.dumps(data, indent=2)


_terminal_reporter = TerminalReporter()
_json_reporter = JSONReporter()


def get_terminal_reporter() -> TerminalReporter:
    return _terminal_reporter


def get_json_reporter() -> JSONReporter:
    return _json_reporter
