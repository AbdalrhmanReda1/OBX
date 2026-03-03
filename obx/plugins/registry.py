from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from obx.core.events import EventBus, EventType, get_event_bus
from obx.core.types import OBXScores, SessionData


class OBXPlugin(ABC):
    name: str = "unnamed_plugin"
    version: str = "0.0.1"
    description: str = ""

    @abstractmethod
    def on_load(self, event_bus: EventBus) -> None:
        ...

    def on_session_start(self, session: SessionData) -> None:
        pass

    def on_session_end(self, session: SessionData, scores: OBXScores) -> None:
        pass

    def on_exception(self, **kwargs: Any) -> None:
        pass

    def on_score_updated(self, scores: OBXScores) -> None:
        pass


class WebhookPlugin(OBXPlugin):
    name = "webhook"
    version = "1.0.0"
    description = "Sends OBX events to a webhook URL"

    def __init__(self, url: str, on_critical_only: bool = True) -> None:
        self._url = url
        self._on_critical_only = on_critical_only

    def on_load(self, event_bus: EventBus) -> None:
        event_bus.subscribe(EventType.SESSION_END, self._handle_session_end)

    def _handle_session_end(self, **kwargs: Any) -> None:
        try:
            import json
            import urllib.request

            session: Optional[SessionData] = kwargs.get("session")
            if session is None:
                return

            payload = json.dumps({
                "event": "session_end",
                "issues": len(session.issues),
                "score": session.scores.index,
                "grade": session.scores.grade,
            }).encode("utf-8")

            req = urllib.request.Request(
                self._url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, OBXPlugin] = {}
        self._event_bus = get_event_bus()

    def register(self, plugin: OBXPlugin) -> None:
        plugin.on_load(self._event_bus)
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        if name in self._plugins:
            del self._plugins[name]

    def load_from_module(self, module_path: str) -> Optional[OBXPlugin]:
        try:
            module = importlib.import_module(module_path)
            plugin_class: Optional[Type[OBXPlugin]] = getattr(module, "Plugin", None)
            if plugin_class and issubclass(plugin_class, OBXPlugin):
                instance = plugin_class()
                self.register(instance)
                return instance
        except (ImportError, AttributeError):
            pass
        return None

    def get_all(self) -> List[OBXPlugin]:
        return list(self._plugins.values())

    def get(self, name: str) -> Optional[OBXPlugin]:
        return self._plugins.get(name)


_registry: PluginRegistry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    return _registry
