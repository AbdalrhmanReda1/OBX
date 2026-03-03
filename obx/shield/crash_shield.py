from __future__ import annotations

import sys
import threading
import traceback
from typing import Any, Callable, Dict, List, Optional, Type

from obx.core.context import get_context
from obx.core.events import EventType, get_event_bus
from obx.core.types import Issue, IssueCategory, OBXMode, Severity

_KNOWN_PATTERNS: Dict[str, tuple] = {
    "RecursionError": (
        Severity.CRITICAL,
        "Infinite recursion detected",
        "Add a base case or increase sys.setrecursionlimit() cautiously",
    ),
    "MemoryError": (
        Severity.CRITICAL,
        "Memory exhaustion detected",
        "Reduce data size, use generators, or stream processing",
    ),
    "AttributeError": (
        Severity.HIGH,
        "Attribute access on None or missing object",
        "Add None check or verify object initialization",
    ),
    "KeyError": (
        Severity.MEDIUM,
        "Dictionary key not found",
        "Use .get() with default or check key existence",
    ),
    "TypeError": (
        Severity.HIGH,
        "Type mismatch in operation",
        "Verify argument types and use type hints",
    ),
    "ValueError": (
        Severity.MEDIUM,
        "Invalid value passed to function",
        "Validate inputs before processing",
    ),
    "IndexError": (
        Severity.MEDIUM,
        "List index out of bounds",
        "Check list length before indexing",
    ),
    "FileNotFoundError": (
        Severity.HIGH,
        "File or directory does not exist",
        "Verify path and use pathlib.Path.exists()",
    ),
    "ConnectionError": (
        Severity.HIGH,
        "Network connection failed",
        "Implement retry logic with exponential backoff",
    ),
    "TimeoutError": (
        Severity.HIGH,
        "Operation timed out",
        "Increase timeout or implement async processing",
    ),
    "PermissionError": (
        Severity.HIGH,
        "Insufficient permissions",
        "Check file/resource permissions",
    ),
    "ZeroDivisionError": (
        Severity.HIGH,
        "Division by zero",
        "Add guard: if denominator != 0",
    ),
    "UnicodeDecodeError": (
        Severity.MEDIUM,
        "String encoding error",
        "Specify encoding explicitly: open(f, encoding='utf-8')",
    ),
    "RuntimeError": (
        Severity.HIGH,
        "Runtime failure",
        "Review execution context and dependencies",
    ),
}


class ExceptionAnalyzer:
    def analyze(self, exc: BaseException) -> Issue:
        exc_type = type(exc).__name__
        tb = traceback.extract_tb(exc.__traceback__)

        location = None
        if tb:
            frame = tb[-1]
            location = f"{frame.filename}:{frame.lineno} in {frame.name}"

        pattern = _KNOWN_PATTERNS.get(exc_type)
        if pattern:
            severity, title, suggestion = pattern
        else:
            severity = Severity.MEDIUM
            title = f"Unhandled {exc_type}"
            suggestion = "Review stack trace and add appropriate exception handling"

        return Issue(
            category=IssueCategory.STABILITY,
            severity=severity,
            title=title,
            description=f"{exc_type}: {exc}",
            location=location,
            suggestion=suggestion,
            metadata={
                "exc_type": exc_type,
                "exc_message": str(exc),
                "traceback": traceback.format_exc(),
            },
        )


class CrashShield:
    def __init__(self) -> None:
        self._analyzer = ExceptionAnalyzer()
        self._safe_mode = False
        self._original_excepthook: Optional[Callable] = None
        self._original_threading_excepthook: Optional[Callable] = None

    def install(self, safe_mode: bool = False) -> None:
        self._safe_mode = safe_mode
        self._original_excepthook = sys.excepthook
        sys.excepthook = self._global_excepthook

        try:
            self._original_threading_excepthook = threading.excepthook
            threading.excepthook = self._threading_excepthook
        except AttributeError:
            pass

    def uninstall(self) -> None:
        if self._original_excepthook:
            sys.excepthook = self._original_excepthook
        if self._original_threading_excepthook:
            try:
                threading.excepthook = self._original_threading_excepthook
            except AttributeError:
                pass

    def _global_excepthook(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_tb: Any,
    ) -> None:
        self._handle_exception(exc_value)
        mode = get_context().get_mode()
        if mode != OBXMode.SILENT and self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_tb)

    def _threading_excepthook(self, args: Any) -> None:
        if args.exc_value:
            self._handle_exception(args.exc_value)
        if self._original_threading_excepthook:
            self._original_threading_excepthook(args)

    def _handle_exception(self, exc: BaseException) -> None:
        issue = self._analyzer.analyze(exc)
        session = get_context().get_session()
        if session:
            session.issues.append(issue)
            if issue.category == IssueCategory.STABILITY and issue.severity in (
                Severity.HIGH,
                Severity.CRITICAL,
            ):
                for profile in session.profiles.values():
                    profile.exceptions_raised += 1

        get_event_bus().emit(EventType.EXCEPTION_CAUGHT, issue=issue, exc=exc)

    def intercept(self, exc: BaseException) -> Issue:
        issue = self._analyzer.analyze(exc)
        session = get_context().get_session()
        if session:
            session.issues.append(issue)
        get_event_bus().emit(EventType.EXCEPTION_CAUGHT, issue=issue, exc=exc)
        return issue

    def get_exception_summary(self) -> List[Dict[str, Any]]:
        session = get_context().get_session()
        if not session:
            return []
        return [
            {
                "category": i.category.value,
                "severity": i.severity.value,
                "title": i.title,
                "description": i.description,
                "location": i.location,
                "suggestion": i.suggestion,
            }
            for i in session.issues
            if i.category == IssueCategory.STABILITY
        ]


_shield: CrashShield = CrashShield()


def get_crash_shield() -> CrashShield:
    return _shield
