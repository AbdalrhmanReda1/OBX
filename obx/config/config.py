from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class OBXConfig:
    mode: str = "dev"
    enable_tracer: bool = True
    enable_shield: bool = True
    enable_memory_monitor: bool = True
    enable_recorder: bool = True
    memory_sample_interval: float = 1.0
    max_timeline_events: int = 10_000
    webhook_url: Optional[str] = None
    excluded_modules: List[str] = field(default_factory=list)
    sensitive_keys: List[str] = field(
        default_factory=lambda: ["password", "secret", "token", "key", "auth"]
    )

    @classmethod
    def from_env(cls) -> "OBXConfig":
        cfg = cls()
        if mode := os.getenv("OBX_MODE"):
            cfg.mode = mode
        if url := os.getenv("OBX_WEBHOOK_URL"):
            cfg.webhook_url = url
        if interval := os.getenv("OBX_MEMORY_INTERVAL"):
            try:
                cfg.memory_sample_interval = float(interval)
            except ValueError:
                pass
        return cfg

    @classmethod
    def from_file(cls, path: str) -> "OBXConfig":
        p = Path(path)
        if not p.exists():
            return cls()
        try:
            data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
            cfg = cls()
            for key, value in data.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)
            return cfg
        except (json.JSONDecodeError, OSError):
            return cls()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "enable_tracer": self.enable_tracer,
            "enable_shield": self.enable_shield,
            "enable_memory_monitor": self.enable_memory_monitor,
            "enable_recorder": self.enable_recorder,
            "memory_sample_interval": self.memory_sample_interval,
            "max_timeline_events": self.max_timeline_events,
        }


_config: OBXConfig = OBXConfig()


def get_config() -> OBXConfig:
    return _config


def set_config(config: OBXConfig) -> None:
    global _config
    _config = config
