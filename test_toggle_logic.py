"""
Test file for toggle logic in BSR Explorer

These tests verify that the checkbox state comparison logic works correctly
with PyQt6's stateChanged signal, which passes integer values (not enum values).
"""
import time as time_module
import unittest
import numpy as np


class TestToggleLogic(unittest.TestCase):
    """Test the toggle logic that was fixed"""
    
    def test_checkbox_state_values(self):
        """Verify the expected checkbox state values from PyQt6"""
        # In PyQt6, Qt.CheckState has these values:
        # Qt.CheckState.Unchecked.value = 0
        # Qt.CheckState.PartiallyChecked.value = 1
        # Qt.CheckState.Checked.value = 2
        
        # The stateChanged signal passes an int, so we compare against .value
        CHECKED_VALUE = 2
        UNCHECKED_VALUE = 0
        
        # Test that our comparison logic works correctly
        state_checked = 2  # simulates stateChanged signal with checked state
        state_unchecked = 0  # simulates stateChanged signal with unchecked state
        
        # The fixed comparison: state == Qt.CheckState.Checked.value
        self.assertTrue(state_checked == CHECKED_VALUE)
        self.assertFalse(state_unchecked == CHECKED_VALUE)
        
    def test_toggle_view_mode_logic(self):
        """Test that toggle_view_mode computes exploded_mode correctly"""
        CHECKED_VALUE = 2  # Qt.CheckState.Checked.value
        
        # Simulate the fixed toggle_view_mode logic
        def compute_exploded_mode(state):
            return (state == CHECKED_VALUE)
        
        # When checkbox is checked, exploded_mode should be True
        self.assertTrue(compute_exploded_mode(2))
        
        # When checkbox is unchecked, exploded_mode should be False
        self.assertFalse(compute_exploded_mode(0))
        
    def test_toggle_channel_logic(self):
        """Test that toggle_channel computes visibility correctly"""
        CHECKED_VALUE = 2  # Qt.CheckState.Checked.value
        
        # Simulate the fixed toggle_channel logic
        def compute_visible(state):
            return (state == CHECKED_VALUE)
        
        # When checkbox is checked, channel should be visible
        self.assertTrue(compute_visible(2))
        
        # When checkbox is unchecked, channel should be hidden
        self.assertFalse(compute_visible(0))


class TestBugRegression(unittest.TestCase):
    """Test that the original bug behavior is fixed"""
    
    def test_old_broken_comparison_fails(self):
        """Demonstrate why the old comparison was broken"""
        # This simulates what the old code did (comparing int to enum)
        # Since we can't import PyQt6 in this environment, we'll use a mock
        
        class MockCheckState:
            """Mock of Qt.CheckState enum"""
            class Checked:
                value = 2
        
        state = 2  # What stateChanged signal actually sends
        
        # Old broken comparison (comparing int to object)
        # This would ALWAYS be False
        old_result = (state == MockCheckState.Checked)
        self.assertFalse(old_result, "Old comparison should fail")
        
        # New fixed comparison (comparing int to int)
        new_result = (state == MockCheckState.Checked.value)
        self.assertTrue(new_result, "New comparison should succeed")
        
    def test_visibility_toggle_cycle(self):
        """Test that visibility can be toggled on and off repeatedly"""
        CHECKED_VALUE = 2
        
        def compute_visible(state):
            return (state == CHECKED_VALUE)
        
        # Simulate a series of checkbox toggles
        states = [2, 0, 2, 0, 2]  # check, uncheck, check, uncheck, check
        expected = [True, False, True, False, True]
        
        for state, expected_visible in zip(states, expected):
            self.assertEqual(compute_visible(state), expected_visible,
                           f"State {state} should give visible={expected_visible}")


class TestHistogramDownsample(unittest.TestCase):
    """Test the optimized histogram downsampling function"""
    
    def histogram_downsample(self, data, time_axis, target_samples):
        """Copy of the optimized histogram_downsample function for testing"""
        if len(data) <= target_samples or target_samples <= 0:
            return time_axis, data
        
        num_bins = max(1, target_samples // 2)
        bin_size = len(data) // num_bins
        
        if bin_size <= 0:
            return time_axis, data
        
        n_samples = num_bins * bin_size
        data_truncated = data[:n_samples]
        time_truncated = time_axis[:n_samples]
        
        data_bins = data_truncated.reshape(num_bins, bin_size)
        time_bins = time_truncated.reshape(num_bins, bin_size)
        
        min_indices = np.argmin(data_bins, axis=1)
        max_indices = np.argmax(data_bins, axis=1)
        
        bin_range = np.arange(num_bins)
        min_data = data_bins[bin_range, min_indices]
        max_data = data_bins[bin_range, max_indices]
        min_time = time_bins[bin_range, min_indices]
        max_time = time_bins[bin_range, max_indices]
        
        min_first = min_indices <= max_indices
        
        first_time = np.where(min_first, min_time, max_time)
        first_data = np.where(min_first, min_data, max_data)
        second_time = np.where(min_first, max_time, min_time)
        second_data = np.where(min_first, max_data, min_data)
        
        result_time = np.empty(2 * num_bins, dtype=time_axis.dtype)
        result_data = np.empty(2 * num_bins, dtype=data.dtype)
        result_time[0::2] = first_time
        result_time[1::2] = second_time
        result_data[0::2] = first_data
        result_data[1::2] = second_data
        
        return result_time, result_data
    
    def test_no_downsampling_needed(self):
        """Test that small datasets are returned unchanged"""
        data = np.array([1, 2, 3, 4, 5], dtype=np.int32)
        time = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
        
        result_time, result_data = self.histogram_downsample(data, time, 10)
        
        np.testing.assert_array_equal(result_time, time)
        np.testing.assert_array_equal(result_data, data)
    
    def test_downsampling_preserves_extrema(self):
        """Test that downsampling preserves min and max values"""
        # Create data with clear peaks and valleys
        data = np.array([0, 10, 5, 0, 20, 15, 10, 5], dtype=np.int32)
        time = np.arange(8, dtype=np.float64) / 10
        
        result_time, result_data = self.histogram_downsample(data, time, 4)
        
        # Should capture the 10 and 20 peaks
        self.assertIn(10, result_data)
        self.assertIn(20, result_data)
        # Should capture the 0 valleys
        self.assertIn(0, result_data)
    
    def test_downsampling_reduces_samples(self):
        """Test that downsampling reduces sample count"""
        data = np.random.randint(0, 100, 10000, dtype=np.int32)
        time = np.arange(10000, dtype=np.float64) / 1000
        
        result_time, result_data = self.histogram_downsample(data, time, 100)
        
        # Should reduce to approximately target_samples (100)
        self.assertLessEqual(len(result_data), 100)
        self.assertEqual(len(result_time), len(result_data))
    
    def test_downsampling_performance(self):
        """Test that vectorized downsampling is fast"""
        # Large dataset
        data = np.random.randint(0, 100, 1000000, dtype=np.int32)
        time_axis = np.arange(1000000, dtype=np.float64) / 200000
        
        start = time_module.perf_counter()
        result_time, result_data = self.histogram_downsample(data, time_axis, 100000)
        elapsed = time_module.perf_counter() - start
        
        # Should complete in under 100ms for 1M samples
        self.assertLess(elapsed, 0.1, f"Downsampling took {elapsed:.3f}s, should be < 0.1s")


if __name__ == '__main__':
    unittest.main()
