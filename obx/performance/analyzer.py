from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from obx.core.context import get_context
from obx.core.types import FunctionProfile, Issue, IssueCategory, Severity

_SLOW_THRESHOLD_MS = 100.0
_VERY_SLOW_THRESHOLD_MS = 500.0
_HIGH_CALL_COUNT = 1000
_MEMORY_GROWTH_THRESHOLD_MB = 50.0


class PerformanceAnalyzer:
    def get_bottlenecks(self, top_n: int = 10) -> List[FunctionProfile]:
        session = get_context().get_session()
        if not session:
            return []
        profiles = list(session.profiles.values())
        return sorted(profiles, key=lambda p: p.total_time, reverse=True)[:top_n]

    def get_heatmap(self) -> Dict[str, float]:
        session = get_context().get_session()
        if not session:
            return {}
        total = sum(p.total_time for p in session.profiles.values()) or 1.0
        return {
            key: round((profile.total_time / total) * 100, 2)
            for key, profile in sorted(
                session.profiles.items(),
                key=lambda x: x[1].total_time,
                reverse=True,
            )
        }

    def detect_issues(self) -> List[Issue]:
        session = get_context().get_session()
        if not session:
            return []

        issues: List[Issue] = []

        for key, profile in session.profiles.items():
            avg_ms = profile.avg_time * 1000

            if avg_ms > _VERY_SLOW_THRESHOLD_MS:
                issues.append(
                    Issue(
                        category=IssueCategory.PERFORMANCE,
                        severity=Severity.HIGH,
                        title="Very slow function detected",
                        description=f"{key} averages {avg_ms:.1f}ms per call",
                        location=key,
                        suggestion="Consider caching, async execution, or algorithmic optimization",
                        metadata={"avg_ms": avg_ms, "call_count": profile.call_count},
                    )
                )
            elif avg_ms > _SLOW_THRESHOLD_MS:
                issues.append(
                    Issue(
                        category=IssueCategory.PERFORMANCE,
                        severity=Severity.MEDIUM,
                        title="Slow function detected",
                        description=f"{key} averages {avg_ms:.1f}ms per call",
                        location=key,
                        suggestion="Profile this function and consider optimization",
                        metadata={"avg_ms": avg_ms, "call_count": profile.call_count},
                    )
                )

            if profile.call_count > _HIGH_CALL_COUNT:
                issues.append(
                    Issue(
                        category=IssueCategory.PERFORMANCE,
                        severity=Severity.MEDIUM,
                        title="High-frequency function call",
                        description=f"{key} was called {profile.call_count} times",
                        location=key,
                        suggestion="Consider memoization or batching calls",
                        metadata={"call_count": profile.call_count},
                    )
                )

        issues.extend(self._detect_memory_issues())
        return issues

    def _detect_memory_issues(self) -> List[Issue]:
        session = get_context().get_session()
        if not session or len(session.memory_snapshots) < 2:
            return []

        issues: List[Issue] = []
        first = session.memory_snapshots[0].rss_mb
        last = session.memory_snapshots[-1].rss_mb
        growth = last - first

        if growth > _MEMORY_GROWTH_THRESHOLD_MB:
            issues.append(
                Issue(
                    category=IssueCategory.MEMORY,
                    severity=Severity.HIGH,
                    title="Significant memory growth detected",
                    description=f"Memory grew by {growth:.1f} MB during session",
                    suggestion="Check for memory leaks: unclosed resources, growing caches, circular references",
                    metadata={"growth_mb": growth, "initial_mb": first, "final_mb": last},
                )
            )

        peak = max(s.rss_mb for s in session.memory_snapshots)
        if peak > 500.0:
            issues.append(
                Issue(
                    category=IssueCategory.MEMORY,
                    severity=Severity.MEDIUM,
                    title="High peak memory usage",
                    description=f"Peak memory usage reached {peak:.1f} MB",
                    suggestion="Consider streaming large datasets or reducing in-memory state",
                    metadata={"peak_mb": peak},
                )
            )

        return issues

    def compute_performance_score(self) -> float:
        session = get_context().get_session()
        if not session:
            return 100.0

        score = 100.0
        profiles = list(session.profiles.values())

        if not profiles:
            return score

        slow_functions = sum(1 for p in profiles if p.avg_time * 1000 > _SLOW_THRESHOLD_MS)
        score -= min(slow_functions * 5, 30)

        very_slow = sum(1 for p in profiles if p.avg_time * 1000 > _VERY_SLOW_THRESHOLD_MS)
        score -= min(very_slow * 10, 30)

        hot_functions = sum(1 for p in profiles if p.call_count > _HIGH_CALL_COUNT)
        score -= min(hot_functions * 3, 15)

        if len(session.memory_snapshots) >= 2:
            growth = (
                session.memory_snapshots[-1].rss_mb - session.memory_snapshots[0].rss_mb
            )
            if growth > _MEMORY_GROWTH_THRESHOLD_MB:
                score -= min(growth / 10, 25)

        return max(round(score, 2), 0.0)

    def get_suggestions(self) -> List[Tuple[str, str]]:
        issues = self.detect_issues()
        return [(i.title, i.suggestion or "") for i in issues if i.suggestion]


_analyzer: PerformanceAnalyzer = PerformanceAnalyzer()


def get_performance_analyzer() -> PerformanceAnalyzer:
    return _analyzer
