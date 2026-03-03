from __future__ import annotations

import json
from typing import Any, Dict, List

from obx.core.context import get_context
from obx.core.events import EventType, get_event_bus
from obx.core.types import Issue, IssueCategory, OBXScores, Severity
from obx.performance.analyzer import get_performance_analyzer


class ScoringEngine:
    def compute_stability_score(self, issues: List[Issue]) -> float:
        score = 100.0
        stability_issues = [i for i in issues if i.category == IssueCategory.STABILITY]

        for issue in stability_issues:
            if issue.severity == Severity.CRITICAL:
                score -= 25
            elif issue.severity == Severity.HIGH:
                score -= 15
            elif issue.severity == Severity.MEDIUM:
                score -= 7
            else:
                score -= 2

        session = get_context().get_session()
        if session:
            total_exceptions = sum(p.exceptions_raised for p in session.profiles.values())
            score -= min(total_exceptions * 3, 20)

        return max(round(score, 2), 0.0)

    def compute_risk_score(self, issues: List[Issue]) -> float:
        score = 0.0
        risk_categories = {IssueCategory.SECURITY, IssueCategory.MEMORY}

        for issue in issues:
            if issue.category in risk_categories:
                if issue.severity == Severity.CRITICAL:
                    score += 30
                elif issue.severity == Severity.HIGH:
                    score += 15
                elif issue.severity == Severity.MEDIUM:
                    score += 7
                else:
                    score += 2

        return min(round(score, 2), 100.0)

    def compute_all_scores(self, logic_score: float = 100.0) -> OBXScores:
        session = get_context().get_session()
        issues: List[Issue] = session.issues if session else []

        stability = self.compute_stability_score(issues)
        performance = get_performance_analyzer().compute_performance_score()
        risk = self.compute_risk_score(issues)

        scores = OBXScores(
            stability=stability,
            performance=performance,
            risk=risk,
            logic=logic_score,
        )

        if session:
            session.scores = scores

        get_event_bus().emit(EventType.SCORE_UPDATED, scores=scores)
        return scores

    def to_json(self, scores: OBXScores) -> str:
        data: Dict[str, Any] = {
            "obx_index": scores.index,
            "grade": scores.grade,
            "components": {
                "stability": scores.stability,
                "performance": scores.performance,
                "risk": scores.risk,
                "logic": scores.logic,
            },
        }
        return json.dumps(data, indent=2)

    def to_markdown(self, scores: OBXScores) -> str:
        grade_emoji = {
            "EXCELLENT": "🏆",
            "GOOD": "✅",
            "FAIR": "⚠️",
            "POOR": "🔴",
            "CRITICAL": "💀",
        }
        emoji = grade_emoji.get(scores.grade, "")
        lines = [
            "## OBX Health Score Report",
            "",
            f"### Overall: {scores.index} / 100 {emoji} {scores.grade}",
            "",
            "| Component | Score |",
            "|-----------|-------|",
            f"| Stability | {scores.stability} |",
            f"| Performance | {scores.performance} |",
            f"| Risk | {scores.risk} (lower is better) |",
            f"| Logic | {scores.logic} |",
            "",
            f"**OBX Index**: `{scores.index}`",
        ]
        return "\n".join(lines)

    def badge_url(self, scores: OBXScores, project: str = "project") -> str:
        color = "brightgreen"
        if scores.index < 55:
            color = "red"
        elif scores.index < 75:
            color = "yellow"
        elif scores.index < 90:
            color = "green"

        label = "OBX+Score"
        value = f"{scores.index}%2F100"
        return f"https://img.shields.io/badge/{label}-{value}-{color}"


_engine: ScoringEngine = ScoringEngine()


def get_scoring_engine() -> ScoringEngine:
    return _engine
