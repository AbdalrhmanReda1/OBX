from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TimelineEvent:
    timestamp: float
    event_type: str
    name: str
    module: str
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateSnapshot:
    timestamp: float
    label: str
    state: Dict[str, Any] = field(default_factory=dict)


class ExecutionRecorder:
    def __init__(self, max_events: int = 10_000) -> None:
        self._max_events = max_events
        self._timeline: List[TimelineEvent] = []
        self._snapshots: List[StateSnapshot] = []
        self._recording = False

    def start(self) -> None:
        self._recording = True
        self._timeline.clear()
        self._snapshots.clear()

    def stop(self) -> None:
        self._recording = False

    def record_event(
        self,
        event_type: str,
        name: str,
        module: str,
        duration: Optional[float] = None,
        **metadata: Any,
    ) -> None:
        if not self._recording:
            return
        if len(self._timeline) >= self._max_events:
            self._timeline = self._timeline[self._max_events // 2:]
        self._timeline.append(
            TimelineEvent(
                timestamp=time.perf_counter(),
                event_type=event_type,
                name=name,
                module=module,
                duration=duration,
                metadata=metadata,
            )
        )

    def snapshot(self, label: str, state: Dict[str, Any]) -> StateSnapshot:
        snap = StateSnapshot(
            timestamp=time.time(),
            label=label,
            state=dict(state),
        )
        self._snapshots.append(snap)
        return snap

    def compare_snapshots(self, label_a: str, label_b: str) -> Dict[str, Any]:
        snap_a = next((s for s in self._snapshots if s.label == label_a), None)
        snap_b = next((s for s in self._snapshots if s.label == label_b), None)

        if not snap_a or not snap_b:
            return {"error": "One or both snapshots not found"}

        all_keys = set(snap_a.state) | set(snap_b.state)
        changes: Dict[str, Any] = {}

        for key in all_keys:
            val_a = snap_a.state.get(key)
            val_b = snap_b.state.get(key)
            if val_a != val_b:
                changes[key] = {"before": val_a, "after": val_b}

        return {
            "snapshot_a": label_a,
            "snapshot_b": label_b,
            "changed_keys": list(changes.keys()),
            "changes": changes,
            "time_delta": snap_b.timestamp - snap_a.timestamp,
        }

    def get_timeline(self) -> List[TimelineEvent]:
        return list(self._timeline)

    def export_session(self) -> Dict[str, Any]:
        return {
            "timeline_events": len(self._timeline),
            "snapshots": len(self._snapshots),
            "timeline": [
                {
                    "timestamp": e.timestamp,
                    "type": e.event_type,
                    "function": f"{e.module}.{e.name}",
                    "duration_ms": round(e.duration * 1000, 3) if e.duration else None,
                }
                for e in self._timeline[:500]
            ],
        }

    def export_json(self) -> str:
        return json.dumps(self.export_session(), indent=2)


_recorder: ExecutionRecorder = ExecutionRecorder()


def get_recorder() -> ExecutionRecorder:
    return _recorder
