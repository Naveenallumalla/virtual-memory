"""
Unit tests for FIFO page replacement algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from algorithms.fifo import simulate


class TestFIFO(unittest.TestCase):

    def test_classic_example(self):
        """Classic textbook example: ref=[1,2,3,4,1,2,5,1,2,3,4,5], frames=3 → 9 faults."""
        ref = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        result = simulate(ref, 3)
        self.assertEqual(result["page_faults"], 9)
        self.assertEqual(result["page_hits"], 3)

    def test_all_hits_after_warmup(self):
        """All same page: should have 1 fault then all hits."""
        ref = [1, 1, 1, 1, 1]
        result = simulate(ref, 3)
        self.assertEqual(result["page_faults"], 1)
        self.assertEqual(result["page_hits"], 4)

    def test_single_frame(self):
        """With 1 frame, every new unique page is a fault."""
        ref = [1, 2, 3, 4]
        result = simulate(ref, 1)
        self.assertEqual(result["page_faults"], 4)

    def test_frames_larger_than_unique_pages(self):
        """If frames >= unique pages, faults = unique page count (no evictions)."""
        ref = [1, 2, 3, 1, 2, 3]
        result = simulate(ref, 10)
        self.assertEqual(result["page_faults"], 3)
        self.assertEqual(result["page_hits"], 3)

    def test_hit_ratio(self):
        """Hit ratio should equal page_hits / total."""
        ref = [1, 2, 1, 2, 1]
        result = simulate(ref, 2)
        expected_ratio = round(result["page_hits"] / len(ref), 4)
        self.assertAlmostEqual(result["hit_ratio"], expected_ratio, places=4)

    def test_fault_rate(self):
        """Fault rate + hit ratio should equal ~1.0."""
        ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3]
        result = simulate(ref, 4)
        self.assertAlmostEqual(
            result["hit_ratio"] + result["fault_rate"], 1.0, places=4
        )

    def test_step_count(self):
        """Number of steps should equal length of reference string."""
        ref = [1, 2, 3, 4, 5]
        result = simulate(ref, 3)
        self.assertEqual(len(result["steps"]), 5)

    def test_frame_snapshot_length(self):
        """Each step's frames list should have length == num_frames."""
        ref = [1, 2, 3]
        result = simulate(ref, 3)
        for step in result["steps"]:
            self.assertEqual(len(step["frames"]), 3)

    def test_execution_time_positive(self):
        """Execution time must be a non-negative number."""
        result = simulate([1, 2, 3], 2)
        self.assertGreaterEqual(result["execution_time_ms"], 0)

    def test_eviction_tracking(self):
        """Evicted page in step should be recorded correctly."""
        # With 2 frames: [1], [1,2] → evict 1 → [3,2]
        ref = [1, 2, 3]
        result = simulate(ref, 2)
        third_step = result["steps"][2]
        self.assertTrue(third_step["fault"])
        self.assertEqual(third_step["evicted"], 1)


if __name__ == "__main__":
    unittest.main()
