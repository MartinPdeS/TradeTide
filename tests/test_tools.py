"""
Comprehensive test suite for TradeTide.tools module.

This module tests utility functions and data structures including:
- Percentage conversion utilities
- Time string parsing
- LinkedList data structure implementation
- Edge cases and error handling

Tests follow pytest best practices with fixtures, parametrized tests,
and comprehensive coverage of normal and edge cases.
"""

import pytest
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from TradeTide.tools import percent_to_float, parse_time_string_to_delta, LinkedList, Node


# ------------------------------------------------------------------------------
# Test Fixtures
# ------------------------------------------------------------------------------

@pytest.fixture
def sample_linked_list():
    """
    Fixture providing a sample LinkedList with test data.

    Returns
    -------
    LinkedList
        LinkedList instance with items [1, 2, 3, 'test', 4.5]
    """
    ll = LinkedList()
    test_data = [1, 2, 3, 'test', 4.5]
    for item in test_data:
        ll.append(item)
    return ll


@pytest.fixture
def empty_linked_list():
    """
    Fixture providing an empty LinkedList instance.

    Returns
    -------
    LinkedList
        Empty LinkedList instance
    """
    return LinkedList()


# ------------------------------------------------------------------------------
# Test Cases for percent_to_float
# ------------------------------------------------------------------------------

class TestPercentToFloat:
    """Test suite for the percent_to_float function."""

    @pytest.mark.parametrize("input_value,expected", [
        ("50%", 0.5),
        ("100%", 1.0),
        ("0%", 0.0),
        ("25.5%", 0.255),
        ("150%", 1.5),
        ("0.1%", 0.001),
        ("99.99%", 0.9999),
        ("1%", 0.01),
    ])
    def test_percent_string_conversion(self, input_value, expected):
        """
        Test conversion of percentage strings to float values.

        Parameters
        ----------
        input_value : str
            Input percentage string
        expected : float
            Expected decimal output
        """
        result = percent_to_float(input_value)
        assert result == pytest.approx(expected, rel=1e-9), f"Failed for input: {input_value}"

    @pytest.mark.parametrize("input_value, expected", [
        ("10%", 0.1),
        ("25%", 0.25),
        ("0%", 0.0),
        ("100.5%", 1.005),
        ("50%", 0.5),
    ])
    def test_pip_conversion(self, input_value, expected):
        """
        Test conversion of pip strings to float values.

        Parameters
        ----------
        input_value : str
            Input pip string
        expected : float
            Expected float output
        """
        result = percent_to_float(input_value)
        assert result == pytest.approx(expected, rel=1e-9), f"Failed for input: {input_value}"

    @pytest.mark.parametrize("input_value,expected", [
        ("42", 42.0),
        ("0", 0.0),
        ("3.14", 3.14),
        ("-10", -10.0),
        ("1000", 1000.0),
    ])
    def test_numeric_string_conversion(self, input_value, expected):
        """
        Test conversion of numeric strings without percentage signs.

        Parameters
        ----------
        input_value : str
            Input numeric string
        expected : float
            Expected float output
        """
        result = percent_to_float(input_value)
        assert result == pytest.approx(expected, rel=1e-9), f"Failed for input: {input_value}"

    @pytest.mark.parametrize("input_value,expected", [
        ("50,5%", 0.505),  # European decimal notation
        ("25,25%", 0.2525),
        ("100,0%", 1.0),
    ])
    def test_european_decimal_notation(self, input_value, expected):
        """
        Test handling of European decimal notation (comma as decimal separator).

        Parameters
        ----------
        input_value : str
            Input percentage string with comma decimal separator
        expected : float
            Expected decimal output
        """
        result = percent_to_float(input_value)
        assert result == pytest.approx(expected, rel=1e-9), f"Failed for input: {input_value}"

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very small percentage
        assert percent_to_float("0.001%") == pytest.approx(0.00001, rel=1e-9)

        # Large percentage
        assert percent_to_float("1000%") == pytest.approx(10.0, rel=1e-9)

        # Zero
        assert percent_to_float("0%") == 0

        # Negative numbers
        assert percent_to_float("-5%") == pytest.approx(-0.05, rel=1e-9)


# ------------------------------------------------------------------------------
# Test Cases for parse_time_string_to_delta
# ------------------------------------------------------------------------------

class TestParseTimeStringToDelta:
    """Test suite for the parse_time_string_to_delta function."""

    @pytest.mark.parametrize("input_string,expected_type,expected_value", [
        ("1 day", timedelta, timedelta(days=1)),
        ("5 days", timedelta, timedelta(days=5)),
        ("2 weeks", timedelta, timedelta(weeks=2)),
        ("3 hours", timedelta, timedelta(hours=3)),
        ("30 minutes", timedelta, timedelta(minutes=30)),
        ("45 seconds", timedelta, timedelta(seconds=45)),
        ("1 week", timedelta, timedelta(weeks=1)),
        ("1 hour", timedelta, timedelta(hours=1)),
        ("1 minute", timedelta, timedelta(minutes=1)),
        ("1 second", timedelta, timedelta(seconds=1)),
    ])
    def test_timedelta_units(self, input_string, expected_type, expected_value):
        """
        Test parsing of time strings that result in timedelta objects.

        Parameters
        ----------
        input_string : str
            Input time string
        expected_type : type
            Expected return type
        expected_value : timedelta
            Expected timedelta value
        """
        result = parse_time_string_to_delta(input_string)
        assert isinstance(result, expected_type), f"Wrong type for {input_string}"
        assert result == expected_value, f"Wrong value for {input_string}"

    @pytest.mark.parametrize("input_string, expected_months, expected_years", [
        ("1 month", 1, 0),
        ("6 months", 6, 0),
        ("12 months", 0, 1),
        ("1 year", 0, 1),
        ("2 years", 0, 2),
        ("5 years", 0, 5),
    ])
    def test_relative_delta_units(self, input_string, expected_months, expected_years):
        """
        Test parsing of time strings that result in relativedelta objects.

        Parameters
        ----------
        input_string : str
            Input time string
        expected_months : int
            Expected months value
        expected_years : int
            Expected years value
        """
        result = parse_time_string_to_delta(input_string)
        assert isinstance(result, relativedelta), f"Wrong type for {input_string}"
        assert result.months == expected_months, f"Wrong months for {input_string}, observed: {result.months}"
        assert result.years == expected_years, f"Wrong years for {input_string}, observed: {result.years}"

    @pytest.mark.parametrize("input_string", [
        "10days",    # No space
        "5 Days",    # Capital letters
        "3 HOURS",   # All caps
        "2 Weeks",   # Mixed case
        "1 MONTH",
        "7 Minutes",
    ])
    def test_case_insensitive_parsing(self, input_string):
        """
        Test that parsing is case-insensitive and handles various formats.

        Parameters
        ----------
        input_string : str
            Input time string with various cases
        """
        result = parse_time_string_to_delta(input_string)
        assert result is not None, f"Should parse {input_string}"

    @pytest.mark.parametrize("invalid_string", [
        "invalid format",
        "5 invalid_unit",
        "not_a_number days",
        "",
        "5",
        "days 5",
        "5 eons",
        "negative_5 days",
    ])
    def test_invalid_format_raises_error(self, invalid_string):
        """
        Test that invalid time strings raise ValueError.

        Parameters
        ----------
        invalid_string : str
            Invalid time string that should raise an error
        """
        with pytest.raises(ValueError):
            parse_time_string_to_delta(invalid_string)

    def test_large_values(self):
        """Test parsing of large time values."""
        result = parse_time_string_to_delta("365 days")
        assert result == timedelta(days=365)

        result = parse_time_string_to_delta("100 years")
        assert isinstance(result, relativedelta)
        assert result.years == 100

    def test_boundary_values(self):
        """Test parsing of boundary values."""
        # Minimum values
        result = parse_time_string_to_delta("1 second")
        assert result == timedelta(seconds=1)

        # Large values that should still work
        result = parse_time_string_to_delta("999999 hours")
        assert result == timedelta(hours=999999)


# ------------------------------------------------------------------------------
# Test Cases for Node class
# ------------------------------------------------------------------------------

class TestNode:
    """Test suite for the Node class."""

    def test_node_creation(self):
        """Test basic node creation."""
        node = Node("test_data")
        assert node.data == "test_data"
        assert node.next is None

    def test_node_with_none_data(self):
        """Test node creation with None data."""
        node = Node(None)
        assert node.data is None
        assert node.next is None

    def test_node_without_data(self):
        """Test node creation without data parameter."""
        node = Node()
        assert node.data is None
        assert node.next is None

    @pytest.mark.parametrize("data", [
        1, "string", [1, 2, 3], {"key": "value"}, 3.14, True, False
    ])
    def test_node_with_various_data_types(self, data):
        """
        Test node creation with various data types.

        Parameters
        ----------
        data : any
            Data to store in the node
        """
        node = Node(data)
        assert node.data == data
        assert node.next is None


# ------------------------------------------------------------------------------
# Test Cases for LinkedList class
# ------------------------------------------------------------------------------

class TestLinkedList:
    """Test suite for the LinkedList class."""

    def test_empty_list_creation(self, empty_linked_list):
        """Test creation of empty linked list."""
        ll = empty_linked_list
        assert ll.head is None
        assert ll.current is None

    def test_append_single_item(self, empty_linked_list):
        """Test appending a single item to empty list."""
        ll = empty_linked_list
        ll.append("first_item")
        assert ll.head is not None
        assert ll.head.data == "first_item"
        assert ll.head.next is None

    def test_append_multiple_items(self, empty_linked_list):
        """Test appending multiple items."""
        ll = empty_linked_list
        items = ["first", "second", "third"]

        for item in items:
            ll.append(item)

        # Verify order by traversing
        current = ll.head
        for expected_item in items:
            assert current is not None, f"Missing node for {expected_item}"
            assert current.data == expected_item
            current = current.next

        assert current is None, "List should end after last item"

    def test_iteration_empty_list(self, empty_linked_list):
        """Test iteration over empty list."""
        ll = empty_linked_list
        items = list(ll)
        assert items == []

    def test_iteration_populated_list(self, sample_linked_list):
        """Test iteration over populated list."""
        ll = sample_linked_list
        items = list(ll)
        expected_items = [1, 2, 3, 'test', 4.5]
        assert items == expected_items

    def test_multiple_iterations(self, sample_linked_list):
        """Test that multiple iterations work correctly."""
        ll = sample_linked_list
        expected_items = [1, 2, 3, 'test', 4.5]

        # First iteration
        items1 = list(ll)
        assert items1 == expected_items

        # Second iteration should work the same
        items2 = list(ll)
        assert items2 == expected_items

    def test_delete_head_node(self, sample_linked_list):
        """Test deletion of head node."""
        ll = sample_linked_list
        ll.delete(1)  # Delete first item

        items = list(ll)
        expected_items = [2, 3, 'test', 4.5]
        assert items == expected_items

    def test_delete_middle_node(self, sample_linked_list):
        """Test deletion of middle node."""
        ll = sample_linked_list
        ll.delete(3)  # Delete middle item

        items = list(ll)
        expected_items = [1, 2, 'test', 4.5]
        assert items == expected_items

    def test_delete_tail_node(self, sample_linked_list):
        """Test deletion of tail node."""
        ll = sample_linked_list
        ll.delete(4.5)  # Delete last item

        items = list(ll)
        expected_items = [1, 2, 3, 'test']
        assert items == expected_items

    def test_delete_nonexistent_node(self, sample_linked_list):
        """Test deletion of non-existent node."""
        ll = sample_linked_list
        original_items = list(ll)

        ll.delete("nonexistent")  # Should not crash

        items_after_delete = list(ll)
        assert items_after_delete == original_items  # Should be unchanged

    def test_delete_from_empty_list(self, empty_linked_list):
        """Test deletion from empty list."""
        ll = empty_linked_list
        ll.delete("anything")  # Should not crash
        assert ll.head is None

    def test_delete_all_nodes(self, sample_linked_list):
        """Test deleting all nodes one by one."""
        ll = sample_linked_list
        items_to_delete = [1, 2, 3, 'test', 4.5]

        for item in items_to_delete:
            ll.delete(item)

        assert ll.head is None
        assert list(ll) == []

    @pytest.mark.parametrize("data_types", [
        [1, 2, 3, 4, 5],  # Integers
        ["a", "b", "c"],  # Strings
        [1.1, 2.2, 3.3],  # Floats
        [True, False, True],  # Booleans
        [None, None, None],  # None values
        [[1, 2], [3, 4]],  # Lists
        [{"a": 1}, {"b": 2}],  # Dictionaries
    ])
    def test_various_data_types(self, data_types):
        """
        Test LinkedList with various data types.

        Parameters
        ----------
        data_types : list
            List of items of various types to test
        """
        ll = LinkedList()
        for item in data_types:
            ll.append(item)

        result = list(ll)
        assert result == data_types

    def test_print_list_method(self, sample_linked_list, capsys):
        """Test the print_list method (captures stdout)."""
        ll = sample_linked_list
        ll.print_list()

        captured = capsys.readouterr()
        expected_lines = ["1", "2", "3", "test", "4.5"]
        actual_lines = [line.strip() for line in captured.out.strip().split('\n') if line.strip()]

        assert actual_lines == expected_lines

    def test_print_empty_list(self, empty_linked_list, capsys):
        """Test print_list on empty list."""
        ll = empty_linked_list
        ll.print_list()

        captured = capsys.readouterr()
        assert captured.out.strip() == ""

    def test_memory_efficiency(self):
        """Test that deleted nodes are properly dereferenced."""
        ll = LinkedList()

        # Add many items
        for i in range(1000):
            ll.append(i)

        # Delete every other item
        for i in range(0, 1000, 2):
            ll.delete(i)

        # Verify remaining items
        remaining = list(ll)
        expected = list(range(1, 1000, 2))
        assert remaining == expected

    def test_iteration_during_modification(self):
        """Test behavior when modifying list during iteration."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)

        # Start iteration
        iterator = iter(ll)
        first_item = next(iterator)
        assert first_item == 1

        # Modify list during iteration
        ll.delete(2)

        # Continue iteration (behavior may vary, but should not crash)
        try:
            remaining_items = list(iterator)
            # The exact behavior here depends on implementation
            # but it should not raise an exception
        except StopIteration:
            pass  # This is acceptable behavior


# ------------------------------------------------------------------------------
# Performance and Memory Tests
# ------------------------------------------------------------------------------

class TestPerformanceAndMemory:
    """Performance and memory-related tests for tools module."""

    def test_percent_to_float_performance(self):
        """Test performance of percent_to_float with many conversions."""
        import time

        test_values = ["50%", "25.5%", "100%", "0.1%"] * 1000

        start_time = time.time()
        results = [percent_to_float(val) for val in test_values]
        end_time = time.time()

        # Should complete in reasonable time (less than 1 second for 4000 conversions)
        assert end_time - start_time < 1.0
        assert len(results) == len(test_values)

    def test_large_linked_list_performance(self):
        """Test LinkedList performance with large dataset."""
        import time

        ll = LinkedList()

        # Test append performance
        start_time = time.time()
        for i in range(10000):
            ll.append(i)
        append_time = time.time() - start_time

        # Test iteration performance
        start_time = time.time()
        items = list(ll)
        iteration_time = time.time() - start_time

        # Performance should be reasonable
        assert append_time < 5.0  # Less than 5 seconds for 10000 appends
        assert iteration_time < 1.0  # Less than 1 second for iteration
        assert len(items) == 10000

    def test_time_parsing_performance(self):
        """Test performance of time string parsing."""
        import time

        test_strings = ["1 day", "5 hours", "30 minutes", "2 weeks"] * 1000

        start_time = time.time()
        results = [parse_time_string_to_delta(s) for s in test_strings]
        end_time = time.time()

        # Should complete in reasonable time
        assert end_time - start_time < 2.0
        assert len(results) == len(test_strings)

# ===============================
# Test Execution
# ===============================

if __name__ == "__main__":
    """
    Execute test suite when run directly.

    Runs all tests with error warnings enabled to catch potential
    issues during development. Provides detailed output for debugging.

    Examples
    --------
    >>> python test_signal.py

    Notes
    -----
    Use pytest directly for more control over test execution
    """
    pytest.main([
        "-v",           # Verbose output
        "-W", "error",  # Treat warnings as errors
        "--tb=short",   # Short traceback format
        __file__
    ])
