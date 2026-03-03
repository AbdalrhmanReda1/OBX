from __future__ import annotations

import time
from typing import Any, Callable, Dict, List


def _noop_target(n: int = 1000) -> int:
    total = 0
    for i in range(n):
        total += i
    return total


def _recursive_target(n: int = 15) -> int:
    if n <= 1:
        return n
    return _recursive_target(n - 1) + _recursive_target(n - 2)


def measure_overhead(func: Callable[..., Any], with_obx: bool, iterations: int = 5) -> float:
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return sum(times) / len(times)


def run_overhead_benchmark() -> Dict[str, Any]:
    baseline = measure_overhead(_noop_target, with_obx=False)

    import obx
    obx.enable(mode="silent")
    with_obx = measure_overhead(_noop_target, with_obx=True)
    obx.disable()

    overhead_pct = ((with_obx - baseline) / baseline) * 100 if baseline > 0 else 0.0

    return {
        "baseline_ms": baseline * 1000,
        "with_obx_ms": with_obx * 1000,
        "overhead_pct": overhead_pct,
        "within_target": overhead_pct < 5.0,
    }


def run_all() -> List[Dict[str, Any]]:
    results = []
    results.append({"benchmark": "overhead", **run_overhead_benchmark()})
    return results


if __name__ == "__main__":
    for result in run_all():
        print(result)
