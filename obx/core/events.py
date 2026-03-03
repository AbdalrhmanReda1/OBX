from __future__ import annotations

import threading
from enum import Enum
from typing import Any, Callable, Dict, List


class EventType(str, Enum):
    FUNCTION_ENTER = "function.enter"
    FUNCTION_EXIT = "function.exit"
    EXCEPTION_CAUGHT = "exception.caught"
    ISSUE_DETECTED = "issue.detected"
    SCORE_UPDATED = "score.updated"
    SESSION_START = "session.start"
    SESSION_END = "session.end"
    MEMORY_SAMPLED = "memory.sampled"


class EventBus:
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event: EventType, handler: Callable[..., Any]) -> None:
        with self._lock:
            key = event.value
            if key not in self._listeners:
                self._listeners[key] = []
            self._listeners[key].append(handler)

    def unsubscribe(self, event: EventType, handler: Callable[..., Any]) -> None:
        with self._lock:
            key = event.value
            if key in self._listeners:
                self._listeners[key] = [h for h in self._listeners[key] if h != handler]

    def emit(self, event: EventType, **kwargs: Any) -> None:
        with self._lock:
            handlers = list(self._listeners.get(event.value, []))
        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception:
                pass

    def clear(self) -> None:
        with self._lock:
            self._listeners.clear()


_global_bus: EventBus = EventBus()


def get_event_bus() -> EventBus:
    return _global_bus
