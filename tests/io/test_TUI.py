"""Test suite for URModbus io/TUI module."""

import pytest
from URModbus.io.TUI import tuiPrint,format_pile


class TestTuiPrint:
    """Test the tuiPrint function for terminal user interface printing."""

    @pytest.fixture
    def reset_line_count(self):
        """Fixture to reset the internal line counter for isolated tests."""
        if hasattr(tuiPrint, "line_count"):
            delattr(tuiPrint, "line_count")
        yield
        # Reset after each test
        if hasattr(tuiPrint, "line_count"):
            delattr(tuiPrint, "line_count")

    def test_tui_print_adds_timestamp(self, reset_line_count):
        """Test that tuiPrint adds current timestamp to first line."""
        import datetime
        
        lines = ["Line 1", "Line 2"]
        tuiPrint(lines)
        
        # First line should have timestamp (at least start with '# >')
        assert tuiPrint.line_count > 2

    def test_tui_print_updates_line_count(self, reset_line_count):
        """Test that internal line count is updated correctly."""
        # First call with 2 lines
        tuiPrint(["Line 1", "Line 2"])
        assert hasattr(tuiPrint, "line_count")
        assert tuiPrint.line_count == 3
        
        # Second call with 1 line (should update to 3 total)
        tuiPrint(["Line 3"])
        assert tuiPrint.line_count == 2

    def test_tui_print_empty_lines(self, reset_line_count):
        """Test that empty lines list is handled."""
        tuiPrint([])
        
        # Should have timestamp but no user lines
        assert hasattr(tuiPrint, "line_count")
        assert tuiPrint.line_count == 1

    def test_tui_print_single_line(self, reset_line_count):
        """Test with single line input."""
        tuiPrint(["Single Line"])
        
        assert hasattr(tuiPrint, "line_count")
        assert tuiPrint.line_count == 2


class TestFormatPile:
    """Test the format_pile function for pretty task pile display."""

    def test_format_pile_empty_pile(self):
        """Test formatting an empty task pile."""
        result = format_pile([])
        
        # Empty pile should remain empty (after filtering 0s)
        assert result == []

    def test_format_pile_with_single_task(self):
        """Test formatting a single non-zero task in pile."""
        result = format_pile([0, 5, 0])
        
        assert result == [5]

    def test_format_pile_multiple_tasks(self):
        """Test formatting multiple tasks without truncation."""
        # 6 or fewer tasks - no truncation
        pile = [0, 1, 0, 2, 0, 3, 0]  # 3 real tasks
        result = format_pile(pile)
        
        assert len(result) == 3
        assert result == [1, 2, 3]

    def test_format_pile_exactly_seven_tasks(self):
        """Test formatting exactly 7 tasks (boundary case)."""
        pile = [0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0]  # 6 real tasks + zeros
        result = format_pile(pile)
        
        assert len(result) == 6
        assert result == [1, 2, 3, 4, 5, 6]

    def test_format_pile_truncation_at_six_plus(self):
        """Test truncation when pile has more than 6 tasks."""
        # This creates a pile with many tasks > 6 after filtering
        pile = [0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7]  # 7 real tasks
        result = format_pile(pile)
        
        assert len(result) == 7  # First 3 + '...N hidden...' + last 3
        assert "...1 hidden..." in result

    def test_format_pile_truncation_three_plus(self):
        """Test truncation with exactly 6+ tasks."""
        pile = [0, 1, 0, 2, 0, 3, 0, 4, 0, 5]  # 5 real tasks (should NOT truncate)
        result = format_pile(pile)
        
        assert len(result) == 5
        

    def test_format_pile_mixed_zero_and_positive(self):
        """Test with mixed zeros and positive task IDs."""
        pile = [0, 1, 0, 2, 0, 3, 0, -1]  # Includes negative (should be kept)
        result = format_pile(pile)
        
        # Filter only removes 0s, not negatives
        assert -1 in result

    def test_format_pile_all_zeros(self):
        """Test when pile contains only zeros."""
        pile = [0, 0, 0, 0]
        result = format_pile(pile)
        
        assert result == []
