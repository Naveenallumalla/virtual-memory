"""
Unit tests for Optimal page replacement algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from algorithms.optimal import simulate


class TestOptimal(unittest.TestCase):

    def test_classic_example(self):
        """Classic example: ref=[1,2,3,4,1,2,5,1,2,3,4,5], frames=3 → 7 faults."""
        ref = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        result = simulate(ref, 3)
        self.assertEqual(result["page_faults"], 7)
        self.assertEqual(result["page_hits"], 5)

    def test_all_same_page(self):
        """Repeating same page: 1 fault then all hits."""
        ref = [3, 3, 3, 3]
        result = simulate(ref, 2)
        self.assertEqual(result["page_faults"], 1)
        self.assertEqual(result["page_hits"], 3)

    def test_single_frame(self):
        """1 frame: every different page is a fault."""
        ref = [1, 2, 3]
        result = simulate(ref, 1)
        self.assertEqual(result["page_faults"], 3)

    def test_optimal_beats_or_ties_fifo(self):
        """Optimal must have page_faults <= FIFO page_faults."""
        from algorithms.fifo import simulate as fifo_sim
        ref = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        opt = simulate(ref, 3)
        fifo = fifo_sim(ref, 3)
        self.assertLessEqual(opt["page_faults"], fifo["page_faults"])

    def test_optimal_beats_or_ties_lru(self):
        """Optimal must have page_faults <= LRU page_faults."""
        from algorithms.lru import simulate as lru_sim
        ref = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        opt = simulate(ref, 3)
        lru = lru_sim(ref, 3)
        self.assertLessEqual(opt["page_faults"], lru["page_faults"])

    def test_no_eviction_needed(self):
        """Enough frames for all unique pages → only initial faults."""
        ref = [1, 2, 3, 1, 2, 3]
        result = simulate(ref, 5)
        self.assertEqual(result["page_faults"], 3)
        self.assertEqual(result["page_hits"], 3)

    def test_hit_fault_sum(self):
        """Hits + faults must equal total references."""
        ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3]
        result = simulate(ref, 4)
        self.assertEqual(
            result["page_hits"] + result["page_faults"], len(ref)
        )

    def test_step_count(self):
        """Steps count must equal reference string length."""
        ref = [1, 2, 3, 4, 5]
        result = simulate(ref, 3)
        self.assertEqual(len(result["steps"]), len(ref))

    def test_frame_snapshot_size(self):
        """Each step frame snapshot must have size == num_frames."""
        ref = [1, 2, 3, 4]
        result = simulate(ref, 3)
        for step in result["steps"]:
            self.assertEqual(len(step["frames"]), 3)

    def test_execution_time_nonnegative(self):
        result = simulate([1, 2, 3, 4], 2)
        self.assertGreaterEqual(result["execution_time_ms"], 0)

    def test_never_used_again_evicted_first(self):
        """Optimal should evict a page that is never used again over one used soon."""
        # ref=[1,2,3,4], frames=3
        # After [1,2,3], page 4 arrives. Of {1,2,3}: none appear in []. All are never used again.
        # The victim should be one of them.
        ref = [1, 2, 3, 4]
        result = simulate(ref, 3)
        last_step = result["steps"][-1]
        self.assertTrue(last_step["fault"])
        self.assertIsNotNone(last_step["evicted"])


if __name__ == "__main__":
    unittest.main()
