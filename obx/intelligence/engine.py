from __future__ import annotations

from typing import Any, Dict, List, Optional

from obx.core.context import get_context
from obx.core.types import Issue, IssueCategory, OBXMode, Severity

_NARRATIVES: Dict[str, str] = {
    "RecursionError": (
        "A recursive function entered an infinite loop. "
        "The call stack grew until Python's safety limit was hit."
    ),
    "MemoryError": (
        "The process consumed all available memory. "
        "This often points to unbounded data accumulation."
    ),
    "AttributeError": (
        "Code tried to access an attribute that doesn't exist. "
        "This usually means an object was None or not properly initialized."
    ),
    "TypeError": (
        "A function received an argument of the wrong type. "
        "Python's dynamic typing can mask these issues until runtime."
    ),
    "ConnectionError": (
        "A network operation failed. "
        "The remote host may be unreachable or the service is down."
    ),
}


class RootCauseAnalyzer:
    def analyze(self, issue: Issue) -> Optional[str]:
        exc_type = issue.metadata.get("exc_type", "")
        return _NARRATIVES.get(exc_type)

    def build_narrative(self, issues: List[Issue]) -> str:
        if not issues:
            return "No issues detected. Your application is running smoothly."

        critical = [i for i in issues if i.severity == Severity.CRITICAL]
        high = [i for i in issues if i.severity == Severity.HIGH]
        medium = [i for i in issues if i.severity == Severity.MEDIUM]

        parts: List[str] = []

        if critical:
            parts.append(
                f"CRITICAL: {len(critical)} critical issue(s) require immediate attention. "
                f"Top issue: {critical[0].title} — {critical[0].description}"
            )

        if high:
            parts.append(
                f"HIGH: {len(high)} high-severity issue(s) detected. "
                f"Most impactful: {high[0].title}"
            )

        if medium:
            parts.append(f"MEDIUM: {len(medium)} medium-severity issue(s) found.")

        total = len(issues)
        parts.append(
            f"Total issues: {total}. "
            f"Resolve critical and high issues before deploying to production."
        )

        return " ".join(parts)


class IntelligenceEngine:
    def __init__(self) -> None:
        self._rca = RootCauseAnalyzer()

    def generate_report(self) -> Dict[str, Any]:
        session = get_context().get_session()
        if not session:
            return {"status": "no_session"}

        issues = session.issues
        narrative = self._rca.build_narrative(issues)

        top_bottleneck: Optional[str] = None
        if session.profiles:
            top = max(session.profiles.values(), key=lambda p: p.total_time)
            top_bottleneck = f"{top.module}.{top.name} ({top.total_time * 1000:.1f}ms total)"

        memory_trend = "stable"
        if len(session.memory_snapshots) >= 2:
            delta = (
                session.memory_snapshots[-1].rss_mb - session.memory_snapshots[0].rss_mb
            )
            if delta > 20:
                memory_trend = f"growing (+{delta:.1f} MB)"
            elif delta < -20:
                memory_trend = f"shrinking ({delta:.1f} MB)"

        return {
            "narrative": narrative,
            "top_bottleneck": top_bottleneck,
            "memory_trend": memory_trend,
            "issue_breakdown": {
                "critical": sum(1 for i in issues if i.severity == Severity.CRITICAL),
                "high": sum(1 for i in issues if i.severity == Severity.HIGH),
                "medium": sum(1 for i in issues if i.severity == Severity.MEDIUM),
                "low": sum(1 for i in issues if i.severity == Severity.LOW),
            },
            "category_breakdown": {
                cat.value: sum(1 for i in issues if i.category == cat)
                for cat in IssueCategory
            },
            "top_suggestions": [
                {"title": i.title, "suggestion": i.suggestion}
                for i in sorted(issues, key=lambda x: x.severity.value)[:5]
                if i.suggestion
            ],
        }

    def filter_for_production(self, report: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(report)
        safe.pop("narrative", None)
        return safe


_engine: IntelligenceEngine = IntelligenceEngine()


def get_intelligence_engine() -> IntelligenceEngine:
    return _engine
