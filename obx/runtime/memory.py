from __future__ import annotations

import threading
import time
from typing import Optional

import psutil

from obx.core.context import get_context
from obx.core.events import EventType, get_event_bus
from obx.core.types import MemorySnapshot


class MemoryMonitor:
    def __init__(self, interval: float = 1.0) -> None:
        self._interval = interval
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._process = psutil.Process()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._sample_loop,
            daemon=True,
            name="obx-memory-monitor",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def sample_once(self) -> Optional[MemorySnapshot]:
        session = get_context().get_session()
        if session is None:
            return None

        try:
            mem = self._process.memory_info()
            pct = self._process.memory_percent()
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                rss_mb=mem.rss / 1_048_576,
                vms_mb=mem.vms / 1_048_576,
                percent=pct,
            )
            session.memory_snapshots.append(snapshot)
            get_event_bus().emit(EventType.MEMORY_SAMPLED, snapshot=snapshot)
            return snapshot
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def _sample_loop(self) -> None:
        while not self._stop_event.wait(timeout=self._interval):
            self.sample_once()

    def get_current_mb(self) -> float:
        try:
            return self._process.memory_info().rss / 1_048_576
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0


_monitor: MemoryMonitor = MemoryMonitor()


def get_memory_monitor() -> MemoryMonitor:
    return _monitor
