"""
FIFO (First In First Out) Page Replacement Algorithm.

Replaces the page that was loaded into memory first.
Uses a queue structure to track insertion order.
"""

import time
from collections import deque
from typing import List, Dict, Any, Optional


def simulate(reference_string: List[int], num_frames: int) -> Dict[str, Any]:
    """
    Run FIFO page replacement simulation.

    Args:
        reference_string: List of page numbers to reference.
        num_frames: Number of available memory frames.

    Returns:
        dict with steps, page_faults, page_hits, hit_ratio, fault_rate, execution_time_ms
    """
    start_time = time.perf_counter()

    frames: List[Optional[int]] = [None] * num_frames
    queue: deque = deque()  # tracks insertion order
    frame_set: set = set()

    steps: List[Dict[str, Any]] = []
    page_faults = 0
    page_hits = 0

    for page in reference_string:
        fault = False
        evicted: Optional[int] = None

        if page in frame_set:
            # Page Hit
            page_hits += 1
        else:
            # Page Fault
            fault = True
            page_faults += 1

            if len(queue) < num_frames:
                # There is still a free frame
                free_idx = frames.index(None)
                frames[free_idx] = page
            else:
                # Evict the oldest page (FIFO)
                evicted = queue.popleft()
                frame_set.remove(evicted)
                replace_idx = frames.index(evicted)
                frames[replace_idx] = page

            queue.append(page)
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
        "algorithm": "fifo",
        "algorithm_name": "FIFO",
        "steps": steps,
        "page_faults": page_faults,
        "page_hits": page_hits,
        "hit_ratio": hit_ratio,
        "fault_rate": fault_rate,
        "execution_time_ms": execution_time_ms,
        "total_references": total,
    }
