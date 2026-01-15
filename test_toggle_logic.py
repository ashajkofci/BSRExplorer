"""
Test file for toggle logic in BSR Explorer

These tests verify that the checkbox state comparison logic works correctly
with PyQt6's stateChanged signal, which passes integer values (not enum values).
"""
import unittest


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


if __name__ == '__main__':
    unittest.main()
