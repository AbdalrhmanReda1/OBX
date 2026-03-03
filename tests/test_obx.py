from __future__ import annotations

import pytest

from obx.core.types import (
    FunctionProfile,
    Issue,
    IssueCategory,
    OBXMode,
    OBXScores,
    Severity,
    SessionData,
)
from obx.core.events import EventBus, EventType
from obx.core.context import OBXContext


class TestOBXScores:
    def test_index_calculation(self):
        scores = OBXScores(
            stability=100.0,
            performance=100.0,
            risk=0.0,
            logic=100.0,
        )
        assert scores.index == 100.0

    def test_index_weights(self):
        scores = OBXScores(
            stability=80.0,
            performance=60.0,
            risk=20.0,
            logic=70.0,
        )
        expected = 80 * 0.30 + 60 * 0.25 + (100 - 20) * 0.25 + 70 * 0.20
        assert abs(scores.index - expected) < 0.01

    def test_grade_excellent(self):
        scores = OBXScores(stability=100, performance=100, risk=0, logic=100)
        assert scores.grade == "EXCELLENT"

    def test_grade_critical(self):
        scores = OBXScores(stability=0, performance=0, risk=100, logic=0)
        assert scores.grade == "CRITICAL"

    def test_grade_good(self):
        scores = OBXScores(stability=85, performance=85, risk=5, logic=85)
        assert scores.grade in ("GOOD", "EXCELLENT")


class TestFunctionProfile:
    def test_avg_time_empty(self):
        profile = FunctionProfile(name="test", module="mod")
        assert profile.avg_time == 0.0

    def test_avg_time(self):
        profile = FunctionProfile(name="test", module="mod")
        profile.call_count = 4
        profile.total_time = 2.0
        assert profile.avg_time == 0.5


class TestEventBus:
    def test_subscribe_emit(self):
        bus = EventBus()
        received = []
        bus.subscribe(EventType.SESSION_START, lambda **kw: received.append(kw))
        bus.emit(EventType.SESSION_START, name="test")
        assert len(received) == 1
        assert received[0]["name"] == "test"

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        handler = lambda **kw: received.append(kw)
        bus.subscribe(EventType.SESSION_START, handler)
        bus.unsubscribe(EventType.SESSION_START, handler)
        bus.emit(EventType.SESSION_START, name="test")
        assert len(received) == 0

    def test_error_in_handler_does_not_propagate(self):
        bus = EventBus()
        def bad_handler(**kw):
            raise ValueError("test error")
        bus.subscribe(EventType.SESSION_START, bad_handler)
        bus.emit(EventType.SESSION_START)

    def test_clear(self):
        bus = EventBus()
        received = []
        bus.subscribe(EventType.SESSION_START, lambda **kw: received.append(1))
        bus.clear()
        bus.emit(EventType.SESSION_START)
        assert len(received) == 0


class TestOBXContext:
    def test_start_session(self):
        ctx = OBXContext()
        session = ctx.start_session(mode=OBXMode.DEV)
        assert session is not None
        assert ctx.is_active()
        assert ctx.get_mode() == OBXMode.DEV

    def test_end_session(self):
        ctx = OBXContext()
        ctx.start_session()
        session = ctx.end_session()
        assert session is not None
        assert not ctx.is_active()

    def test_reset(self):
        ctx = OBXContext()
        ctx.start_session()
        ctx.reset()
        assert not ctx.is_active()
        assert ctx.get_session() is None


class TestScoringEngine:
    def test_stability_score_no_issues(self):
        from obx.scoring.engine import ScoringEngine
        engine = ScoringEngine()
        assert engine.compute_stability_score([]) == 100.0

    def test_stability_score_critical_issue(self):
        from obx.scoring.engine import ScoringEngine
        engine = ScoringEngine()
        issues = [
            Issue(
                category=IssueCategory.STABILITY,
                severity=Severity.CRITICAL,
                title="Test",
                description="desc",
            )
        ]
        score = engine.compute_stability_score(issues)
        assert score < 100.0
        assert score >= 0.0

    def test_risk_score_no_issues(self):
        from obx.scoring.engine import ScoringEngine
        engine = ScoringEngine()
        assert engine.compute_risk_score([]) == 0.0

    def test_to_json(self):
        import json
        from obx.scoring.engine import ScoringEngine
        engine = ScoringEngine()
        scores = OBXScores(stability=90, performance=80, risk=5, logic=85)
        result = json.loads(engine.to_json(scores))
        assert "obx_index" in result
        assert "grade" in result
        assert "components" in result

    def test_to_markdown(self):
        from obx.scoring.engine import ScoringEngine
        engine = ScoringEngine()
        scores = OBXScores(stability=90, performance=80, risk=5, logic=85)
        md = engine.to_markdown(scores)
        assert "OBX Health Score" in md
        assert "Stability" in md


class TestLogicEngine:
    def test_analyze_clean_file(self, tmp_path):
        from obx.logic.engine import get_logic_engine
        f = tmp_path / "clean.py"
        f.write_text("def add(a, b):\n    return a + b\n")
        issues = get_logic_engine().analyze_file(str(f))
        assert isinstance(issues, list)

    def test_detect_infinite_loop(self, tmp_path):
        from obx.logic.engine import get_logic_engine
        f = tmp_path / "bad.py"
        f.write_text("def run():\n    while True:\n        x = 1\n")
        issues = get_logic_engine().analyze_file(str(f))
        assert any("infinite" in i.title.lower() for i in issues)

    def test_detect_always_true_condition(self, tmp_path):
        from obx.logic.engine import get_logic_engine
        f = tmp_path / "cond.py"
        f.write_text("def run():\n    if True:\n        pass\n")
        issues = get_logic_engine().analyze_file(str(f))
        assert any("true" in i.title.lower() for i in issues)

    def test_logic_score_perfect(self):
        from obx.logic.engine import get_logic_engine
        score = get_logic_engine().compute_logic_score([])
        assert score == 100.0

    def test_logic_score_with_issues(self, tmp_path):
        from obx.logic.engine import get_logic_engine, LogicIssue
        issues = [LogicIssue("f.py", 1, "t", "d", "critical", "fix")]
        score = get_logic_engine().compute_logic_score(issues)
        assert score < 100.0


class TestCrashShield:
    def test_analyze_known_exception(self):
        from obx.shield.crash_shield import ExceptionAnalyzer
        analyzer = ExceptionAnalyzer()
        exc = ZeroDivisionError("division by zero")
        try:
            raise exc
        except ZeroDivisionError as e:
            issue = analyzer.analyze(e)
        assert issue.severity == Severity.HIGH
        assert "zero" in issue.title.lower()

    def test_analyze_unknown_exception(self):
        from obx.shield.crash_shield import ExceptionAnalyzer
        analyzer = ExceptionAnalyzer()
        exc = Exception("custom error")
        try:
            raise exc
        except Exception as e:
            issue = analyzer.analyze(e)
        assert issue is not None


class TestExecutionRecorder:
    def test_record_and_export(self):
        from obx.recorder.recorder import ExecutionRecorder
        rec = ExecutionRecorder()
        rec.start()
        rec.record_event("function.exit", "my_func", "my_module", duration=0.01)
        exported = rec.export_session()
        assert exported["timeline_events"] == 1
        rec.stop()

    def test_snapshot_compare(self):
        from obx.recorder.recorder import ExecutionRecorder
        rec = ExecutionRecorder()
        rec.start()
        rec.snapshot("before", {"count": 0, "name": "test"})
        rec.snapshot("after", {"count": 5, "name": "test"})
        diff = rec.compare_snapshots("before", "after")
        assert "count" in diff["changed_keys"]
        assert "name" not in diff["changed_keys"]
        rec.stop()


class TestMemoryMonitor:
    def test_sample_once(self):
        from obx.runtime.memory import MemoryMonitor
        from obx.core.context import OBXContext
        from obx.core.types import OBXMode

        ctx = OBXContext()
        from obx.core import get_context
        import obx.runtime.memory as mem_module

        monitor = MemoryMonitor(interval=10.0)
        result = monitor.get_current_mb()
        assert result >= 0.0

    def test_get_current_mb(self):
        from obx.runtime.memory import MemoryMonitor
        monitor = MemoryMonitor()
        mb = monitor.get_current_mb()
        assert mb > 0.0


class TestIntelligenceEngine:
    def test_build_narrative_no_issues(self):
        from obx.intelligence.engine import RootCauseAnalyzer
        rca = RootCauseAnalyzer()
        narrative = rca.build_narrative([])
        assert "no issues" in narrative.lower()

    def test_build_narrative_with_critical(self):
        from obx.intelligence.engine import RootCauseAnalyzer
        rca = RootCauseAnalyzer()
        issues = [
            Issue(
                category=IssueCategory.STABILITY,
                severity=Severity.CRITICAL,
                title="Test critical",
                description="desc",
            )
        ]
        narrative = rca.build_narrative(issues)
        assert "CRITICAL" in narrative
