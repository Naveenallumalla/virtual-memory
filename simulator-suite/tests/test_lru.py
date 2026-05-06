"""
Unit tests for LRU page replacement algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from algorithms.lru import simulate


class TestLRU(unittest.TestCase):

    def test_classic_example(self):
        """Classic textbook example: ref=[1,2,3,4,1,2,5,1,2,3,4,5], frames=3 → 10 faults."""
        ref = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        result = simulate(ref, 3)
        # LRU classic result
        self.assertEqual(result["page_faults"], 10)
        self.assertEqual(result["page_hits"], 2)

    def test_all_same_page(self):
        """Repeating same page: 1 fault then all hits."""
        ref = [5, 5, 5, 5]
        result = simulate(ref, 2)
        self.assertEqual(result["page_faults"], 1)
        self.assertEqual(result["page_hits"], 3)

    def test_single_frame(self):
        """1 frame → every different page is a fault."""
        ref = [1, 2, 3, 1, 2]
        result = simulate(ref, 1)
        self.assertEqual(result["page_faults"], 5)

    def test_lru_eviction_order(self):
        """LRU should evict least recently used page."""
        # ref=[1,2,3,2,4], frames=3
        # [1],[1,2],[1,2,3] → hit 2 → [1,2,3] → 4: evict 1 (LRU)
        ref = [1, 2, 3, 2, 4]
        result = simulate(ref, 3)
        last_fault_step = [s for s in result["steps"] if s["fault"]][-1]
        self.assertEqual(last_fault_step["evicted"], 1)

    def test_hit_ratio_and_fault_rate_sum(self):
        """Hit ratio + fault rate should sum to 1."""
        ref = [0, 1, 2, 3, 0, 1, 4, 0, 1, 2, 3, 4]
        result = simulate(ref, 3)
        self.assertAlmostEqual(
            result["hit_ratio"] + result["fault_rate"], 1.0, places=4
        )

    def test_frames_larger_than_unique_pages(self):
        """More frames than unique pages → no evictions."""
        ref = [1, 2, 1, 2, 3, 3]
        result = simulate(ref, 10)
        self.assertEqual(result["page_faults"], 3)
        self.assertEqual(result["page_hits"], 3)

    def test_step_count(self):
        """Steps count must equal reference string length."""
        ref = [7, 0, 1, 2, 0, 3]
        result = simulate(ref, 3)
        self.assertEqual(len(result["steps"]), len(ref))

    def test_frame_snapshot_size(self):
        """Each step frame snapshot must have size == num_frames."""
        ref = [1, 2, 3, 4]
        result = simulate(ref, 3)
        for step in result["steps"]:
            self.assertEqual(len(step["frames"]), 3)

    def test_execution_time_nonnegative(self):
        result = simulate([1, 2, 3], 2)
        self.assertGreaterEqual(result["execution_time_ms"], 0)

    def test_page_hit_not_fault(self):
        """A hit step should have fault=False and evicted=None."""
        ref = [1, 2, 1]
        result = simulate(ref, 3)
        step = result["steps"][2]  # second access to page 1 → hit
        self.assertFalse(step["fault"])
        self.assertIsNone(step["evicted"])


if __name__ == "__main__":
    unittest.main()
