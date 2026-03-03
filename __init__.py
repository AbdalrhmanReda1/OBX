from __future__ import annotations

import atexit
from typing import Any, Dict, Optional

from obx.config.config import OBXConfig, get_config, set_config
from obx.core.context import get_context
from obx.core.events import EventType, get_event_bus
from obx.core.types import OBXMode, OBXScores, SessionData
from obx.intelligence.engine import get_intelligence_engine
from obx.logic.engine import get_logic_engine
from obx.performance.analyzer import get_performance_analyzer
from obx.recorder.recorder import get_recorder
from obx.reporting.reporter import get_json_reporter, get_terminal_reporter
from obx.runtime.memory import get_memory_monitor
from obx.runtime.tracer import get_tracer
from obx.scoring.engine import get_scoring_engine
from obx.shield.crash_shield import get_crash_shield

__version__ = "1.0.0"
__author__ = "Abdalrhman Reda"


def enable(
    mode: str = "dev",
    safe_mode: bool = False,
    config: Optional[OBXConfig] = None,
    **kwargs: Any,
) -> None:
    if config is None:
        config = OBXConfig.from_env()
        config.mode = mode

    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    set_config(config)

    obx_mode = OBXMode(mode)
    context = get_context()
    context.start_session(mode=obx_mode)

    get_crash_shield().install(safe_mode=safe_mode)

    if config.enable_tracer:
        get_tracer().start()

    if config.enable_memory_monitor:
        monitor = get_memory_monitor()
        monitor._interval = config.memory_sample_interval
        monitor.start()

    if config.enable_recorder:
        recorder = get_recorder()
        recorder._max_events = config.max_timeline_events
        recorder.start()

    get_event_bus().subscribe(EventType.FUNCTION_EXIT, _on_function_exit)

    if obx_mode != OBXMode.SILENT:
        get_terminal_reporter().print_banner(obx_mode)

    atexit.register(_auto_report)


def _on_function_exit(**kwargs: Any) -> None:
    pass


def _auto_report() -> None:
    context = get_context()
    if not context.is_active():
        return

    config = get_config()
    mode = context.get_mode()

    _finalize()

    if mode != OBXMode.SILENT:
        session = context.get_session()
        if session:
            scores = session.scores
            reporter = get_terminal_reporter()
            reporter.print_scores(scores)
            reporter.print_issues(session.issues)

            intel = get_intelligence_engine().generate_report()
            narrative = intel.get("narrative", "")
            if narrative:
                reporter.print_narrative(narrative)

            if session.profiles:
                reporter.print_profile_top(session.profiles)


def _finalize() -> None:
    config = get_config()
    get_tracer().stop()
    get_memory_monitor().stop()
    get_recorder().stop()
    get_crash_shield().uninstall()

    session = get_context().end_session()
    if session is None:
        return

    logic_issues = []
    logic_score = 100.0

    scoring = get_scoring_engine()
    scores = scoring.compute_all_scores(logic_score=logic_score)

    session.issues.extend(get_performance_analyzer().detect_issues())

    get_event_bus().emit(EventType.SESSION_END, session=session, scores=scores)


def disable() -> None:
    _finalize()
    get_context().reset()


def report(output: str = "terminal") -> Any:
    context = get_context()
    session = context.get_session()

    if session is None:
        get_terminal_reporter().print_error("No active OBX session.")
        return None

    scoring = get_scoring_engine()
    scores = scoring.compute_all_scores()

    if output == "json":
        return get_json_reporter().generate(
            scores=scores,
            issues=session.issues,
            extra=get_intelligence_engine().generate_report(),
        )

    if output == "markdown":
        return scoring.to_markdown(scores)

    reporter = get_terminal_reporter()
    reporter.print_scores(scores)
    reporter.print_issues(session.issues)
    return scores


def score() -> OBXScores:
    session = get_context().get_session()
    issues = session.issues if session else []
    logic = get_logic_engine()
    logic_issues = []
    logic_score = logic.compute_logic_score(logic_issues)
    return get_scoring_engine().compute_all_scores(logic_score=logic_score)


def snapshot(label: str, state: Optional[Dict[str, Any]] = None) -> None:
    get_recorder().snapshot(label=label, state=state or {})


__all__ = [
    "__version__",
    "__author__",
    "enable",
    "disable",
    "report",
    "score",
    "snapshot",
    "OBXConfig",
]
