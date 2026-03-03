from __future__ import annotations

import sys
import threading
import time
from typing import Any, Dict, Optional, Set

from obx.core.context import get_context
from obx.core.events import EventType, get_event_bus
from obx.core.types import FunctionProfile


class RuntimeTracer:
    def __init__(self) -> None:
        self._active = False
        self._lock = threading.Lock()
        self._excluded_modules: Set[str] = {
            "obx",
            "threading",
            "importlib",
            "_bootstrap",
            "abc",
            "typing",
            "enum",
            "dataclasses",
            "collections",
            "rich",
            "click",
            "psutil",
            "pip",
            "pkg_resources",
            "setuptools",
            "codecs",
            "io",
            "re",
            "json",
            "pathlib",
            "functools",
            "weakref",
            "gc",
            "inspect",
            "ast",
        }
        self._call_stack: Dict[int, list] = {}

    def start(self) -> None:
        with self._lock:
            if self._active:
                return
            self._active = True
        sys.settrace(self._trace_dispatch)
        threading.settrace(self._trace_dispatch)

    def stop(self) -> None:
        with self._lock:
            if not self._active:
                return
            self._active = False
        sys.settrace(None)
        threading.settrace(None)

    def _trace_dispatch(self, frame: Any, event: str, arg: Any) -> Optional[Any]:
        if not self._active:
            return None

        module = frame.f_globals.get("__name__", "") or ""
        root = module.split(".")[0]

        if root in self._excluded_modules:
            return None

        if event == "call":
            return self._on_call(frame, module)
        if event == "return":
            self._on_return(frame, module, arg)
        if event == "exception":
            self._on_exception(frame, module, arg)

        return self._trace_dispatch

    def _on_call(self, frame: Any, module: str) -> Any:
        tid = threading.get_ident()
        if tid not in self._call_stack:
            self._call_stack[tid] = []

        name = frame.f_code.co_name
        self._call_stack[tid].append((name, module, time.perf_counter()))

        get_event_bus().emit(
            EventType.FUNCTION_ENTER,
            name=name,
            module=module,
            lineno=frame.f_lineno,
        )
        return self._trace_dispatch

    def _on_return(self, frame: Any, module: str, return_value: Any) -> None:
        tid = threading.get_ident()
        stack = self._call_stack.get(tid)
        if not stack:
            return

        name = frame.f_code.co_name
        for i in range(len(stack) - 1, -1, -1):
            if stack[i][0] == name and stack[i][1] == module:
                _, _, start_time = stack.pop(i)
                elapsed = time.perf_counter() - start_time
                self._record_profile(name, module, elapsed)
                get_event_bus().emit(
                    EventType.FUNCTION_EXIT,
                    name=name,
                    module=module,
                    duration=elapsed,
                )
                break

    def _on_exception(self, frame: Any, module: str, arg: Any) -> None:
        exc_type, exc_value, _ = arg
        get_event_bus().emit(
            EventType.EXCEPTION_CAUGHT,
            exc_type=exc_type,
            exc_value=exc_value,
            module=module,
            lineno=frame.f_lineno,
            name=frame.f_code.co_name,
        )

    def _record_profile(self, name: str, module: str, elapsed: float) -> None:
        session = get_context().get_session()
        if session is None:
            return

        key = f"{module}.{name}"
        if key not in session.profiles:
            session.profiles[key] = FunctionProfile(name=name, module=module)

        profile = session.profiles[key]
        profile.call_count += 1
        profile.total_time += elapsed
        profile.min_time = min(profile.min_time, elapsed)
        profile.max_time = max(profile.max_time, elapsed)

    def add_excluded_module(self, module: str) -> None:
        with self._lock:
            self._excluded_modules.add(module)


_tracer: RuntimeTracer = RuntimeTracer()


def get_tracer() -> RuntimeTracer:
    return _tracer
