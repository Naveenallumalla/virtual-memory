"""
Optimal (Bélády's Algorithm) Page Replacement.

Replaces the page that will not be used for the longest period in the future.
This is a theoretical best-case algorithm (requires future knowledge).
"""

import time
from typing import List, Dict, Any, Optional


def _find_optimal_victim(frames: List[Optional[int]], future: List[int]) -> int:
    """
    Find the index of the frame to evict.
    Evict the page whose next use is farthest in the future
    (or never used again).
    """
    farthest = -1
    victim_idx = 0

    for i, page in enumerate(frames):
        if page is None:
            continue
        try:
            next_use = future.index(page)
        except ValueError:
            # Page never used again → perfect candidate to evict
            return i

        if next_use > farthest:
            farthest = next_use
            victim_idx = i

    return victim_idx


def simulate(reference_string: List[int], num_frames: int) -> Dict[str, Any]:
    """
    Run Optimal page replacement simulation.

    Args:
        reference_string: List of page numbers to reference.
        num_frames: Number of available memory frames.

    Returns:
        dict with steps, page_faults, page_hits, hit_ratio, fault_rate, execution_time_ms
    """
    start_time = time.perf_counter()

    frames: List[Optional[int]] = [None] * num_frames
    frame_set: set = set()

    steps: List[Dict[str, Any]] = []
    page_faults = 0
    page_hits = 0

    for i, page in enumerate(reference_string):
        fault = False
        evicted: Optional[int] = None

        if page in frame_set:
            # Page Hit
            page_hits += 1
        else:
            # Page Fault
            fault = True
            page_faults += 1
            future = reference_string[i + 1:]  # remaining references

            if None in frames:
                # Free frame available
                free_idx = frames.index(None)
                frames[free_idx] = page
            else:
                # Evict optimal victim
                victim_idx = _find_optimal_victim(frames, future)
                evicted = frames[victim_idx]
                frame_set.discard(evicted)
                frames[victim_idx] = page

            frame_set.add(page)

        steps.append({
            "page": page,
            "frames": list(frames),
            "fault": fault,
            "evicted": evicted,
            "page_hits": page_hits,
            "page_faults": page_faults,
        })

    total = page_faults + page_hits
    hit_ratio = round(page_hits / total, 4) if total > 0 else 0.0
    fault_rate = round(page_faults / total, 4) if total > 0 else 0.0
    execution_time_ms = round((time.perf_counter() - start_time) * 1000, 4)

    return {
        "algorithm": "optimal",
        "algorithm_name": "Optimal",
        "steps": steps,
        "page_faults": page_faults,
        "page_hits": page_hits,
        "hit_ratio": hit_ratio,
        "fault_rate": fault_rate,
        "execution_time_ms": execution_time_ms,
        "total_references": total,
    }
