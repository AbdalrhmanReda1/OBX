from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class OBXMode(str, Enum):
    DEV = "dev"
    PROD = "prod"
    SILENT = "silent"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(str, Enum):
    PERFORMANCE = "performance"
    STABILITY = "stability"
    LOGIC = "logic"
    SECURITY = "security"
    MEMORY = "memory"


@dataclass
class Issue:
    category: IssueCategory
    severity: Severity
    title: str
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FunctionProfile:
    name: str
    module: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    exceptions_raised: int = 0

    @property
    def avg_time(self) -> float:
        if self.call_count == 0:
            return 0.0
        return self.total_time / self.call_count


@dataclass
class MemorySnapshot:
    timestamp: float
    rss_mb: float
    vms_mb: float
    percent: float


@dataclass
class OBXScores:
    stability: float = 0.0
    performance: float = 0.0
    risk: float = 0.0
    logic: float = 0.0

    @property
    def index(self) -> float:
        return round(
            self.stability * 0.30
            + self.performance * 0.25
            + (100.0 - self.risk) * 0.25
            + self.logic * 0.20,
            2,
        )

    @property
    def grade(self) -> str:
        idx = self.index
        if idx >= 90:
            return "EXCELLENT"
        if idx >= 75:
            return "GOOD"
        if idx >= 55:
            return "FAIR"
        if idx >= 35:
            return "POOR"
        return "CRITICAL"


@dataclass
class SessionData:
    start_time: float
    end_time: Optional[float] = None
    mode: OBXMode = OBXMode.DEV
    issues: List[Issue] = field(default_factory=list)
    profiles: Dict[str, FunctionProfile] = field(default_factory=dict)
    memory_snapshots: List[MemorySnapshot] = field(default_factory=list)
    scores: OBXScores = field(default_factory=OBXScores)
    metadata: Dict[str, Any] = field(default_factory=dict)
