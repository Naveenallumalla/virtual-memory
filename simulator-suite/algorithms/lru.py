"""
LRU (Least Recently Used) Page Replacement Algorithm.

Replaces the page that has not been referenced for the longest time.
Uses an ordered dict to efficiently track usage recency.
"""

import time
from collections import OrderedDict
from typing import List, Dict, Any, Optional


def simulate(reference_string: List[int], num_frames: int) -> Dict[str, Any]:
    """
    Run LRU page replacement simulation.

    Args:
        reference_string: List of page numbers to reference.
        num_frames: Number of available memory frames.

    Returns:
        dict with steps, page_faults, page_hits, hit_ratio, fault_rate, execution_time_ms
    """
    start_time = time.perf_counter()

    frames: List[Optional[int]] = [None] * num_frames
    # OrderedDict: key = page, value = True (used as an ordered set)
    lru_order: OrderedDict = OrderedDict()

    steps: List[Dict[str, Any]] = []
    page_faults = 0
    page_hits = 0

    for page in reference_string:
        fault = False
        evicted: Optional[int] = None

        if page in lru_order:
            # Page Hit – move to most recently used (end)
            page_hits += 1
            lru_order.move_to_end(page)
        else:
            # Page Fault
            fault = True
            page_faults += 1

            if len(lru_order) < num_frames:
                # Free frame available
                free_idx = frames.index(None)
                frames[free_idx] = page
            else:
                # Evict least recently used (front of OrderedDict)
                evicted, _ = lru_order.popitem(last=False)
                replace_idx = frames.index(evicted)
                frames[replace_idx] = page

            lru_order[page] = True

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
        "algorithm": "lru",
        "algorithm_name": "LRU",
        "steps": steps,
        "page_faults": page_faults,
        "page_hits": page_hits,
        "hit_ratio": hit_ratio,
        "fault_rate": fault_rate,
        "execution_time_ms": execution_time_ms,
        "total_references": total,
    }
