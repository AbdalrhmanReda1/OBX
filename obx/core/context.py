from __future__ import annotations

import threading
import time
from typing import Optional

from obx.core.types import OBXMode, SessionData


class OBXContext:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._session: Optional[SessionData] = None
        self._mode: OBXMode = OBXMode.DEV
        self._active: bool = False

    def start_session(self, mode: OBXMode = OBXMode.DEV) -> SessionData:
        with self._lock:
            self._mode = mode
            self._session = SessionData(start_time=time.time(), mode=mode)
            self._active = True
        return self._session

    def end_session(self) -> Optional[SessionData]:
        with self._lock:
            if self._session:
                self._session.end_time = time.time()
            self._active = False
            return self._session

    def get_session(self) -> Optional[SessionData]:
        return self._session

    def is_active(self) -> bool:
        return self._active

    def get_mode(self) -> OBXMode:
        return self._mode

    def reset(self) -> None:
        with self._lock:
            self._session = None
            self._active = False


_global_context: OBXContext = OBXContext()


def get_context() -> OBXContext:
    return _global_context
