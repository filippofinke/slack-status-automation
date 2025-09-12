#!/usr/bin/env python3
"""
Basic tests for the new time-based scheduling functionality.
"""
import unittest
from datetime import datetime, time
from unittest.mock import Mock

from slack_status_updater.utils import parse_days, is_time_in_range, is_day_match
from slack_status_updater.scheduler import Scheduler


class TestUtils(unittest.TestCase):
    """Test utility functions for day and time parsing."""

    def test_parse_days_weekdays(self):
        """Test parsing 'weekdays' keyword."""
        result = parse_days("weekdays")
        self.assertEqual(result, [0, 1, 2, 3, 4])  # Monday to Friday

    def test_parse_days_weekends(self):
        """Test parsing 'weekends' keyword."""
        result = parse_days("weekends")
        self.assertEqual(result, [5, 6])  # Saturday and Sunday

    def test_parse_days_single_day(self):
        """Test parsing single day name."""
        result = parse_days("monday")
        self.assertEqual(result, [0])

    def test_parse_days_list(self):
        """Test parsing list of day names."""
        result = parse_days(["monday", "wednesday", "friday"])
        self.assertEqual(result, [0, 2, 4])

    def test_parse_days_invalid(self):
        """Test parsing invalid day specification."""
        with self.assertRaises(ValueError):
            parse_days("invalid")
        
        with self.assertRaises(ValueError):
            parse_days(["invalid_day"])

    def test_is_time_in_range_normal(self):
        """Test time range that doesn't cross midnight."""
        start = time(9, 0)
        end = time(17, 0)
        
        self.assertTrue(is_time_in_range(time(12, 0), start, end))
        self.assertTrue(is_time_in_range(time(9, 0), start, end))
        self.assertFalse(is_time_in_range(time(17, 0), start, end))
        self.assertFalse(is_time_in_range(time(8, 0), start, end))
        self.assertFalse(is_time_in_range(time(18, 0), start, end))

    def test_is_time_in_range_crosses_midnight(self):
        """Test time range that crosses midnight."""
        start = time(22, 0)
        end = time(6, 0)
        
        self.assertTrue(is_time_in_range(time(23, 0), start, end))
        self.assertTrue(is_time_in_range(time(5, 0), start, end))
        self.assertTrue(is_time_in_range(time(22, 0), start, end))
        self.assertFalse(is_time_in_range(time(6, 0), start, end))
        self.assertFalse(is_time_in_range(time(12, 0), start, end))

    def test_is_day_match(self):
        """Test day matching functionality."""
        weekdays = [0, 1, 2, 3, 4]
        weekends = [5, 6]
        
        self.assertTrue(is_day_match(0, weekdays))  # Monday
        self.assertTrue(is_day_match(4, weekdays))  # Friday
        self.assertFalse(is_day_match(5, weekdays))  # Saturday
        
        self.assertTrue(is_day_match(5, weekends))  # Saturday
        self.assertTrue(is_day_match(6, weekends))  # Sunday
        self.assertFalse(is_day_match(0, weekends))  # Monday


class TestScheduler(unittest.TestCase):
    """Test the enhanced scheduler functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_updater = Mock()
        
    def test_is_interval_active_no_constraints(self):
        """Test interval with no day/time constraints (always active)."""
        intervals = [{"time": "09:00", "status_text": "Working"}]
        scheduler = Scheduler(self.mock_updater, intervals)
        
        # Should be active on any day at any time
        test_time = datetime(2024, 1, 15, 12, 0)  # Monday
        self.assertTrue(scheduler._is_interval_active(intervals[0], test_time))
        
        test_time = datetime(2024, 1, 20, 12, 0)  # Saturday
        self.assertTrue(scheduler._is_interval_active(intervals[0], test_time))

    def test_is_interval_active_weekdays_only(self):
        """Test interval that should only be active on weekdays."""
        intervals = [{"time": "09:00", "days": "weekdays", "status_text": "Working"}]
        scheduler = Scheduler(self.mock_updater, intervals)
        
        # Should be active on Monday
        test_time = datetime(2024, 1, 15, 12, 0)  # Monday
        self.assertTrue(scheduler._is_interval_active(intervals[0], test_time))
        
        # Should not be active on Saturday
        test_time = datetime(2024, 1, 20, 12, 0)  # Saturday
        self.assertFalse(scheduler._is_interval_active(intervals[0], test_time))

    def test_is_interval_active_time_range(self):
        """Test interval with time range constraints."""
        intervals = [{
            "time": "09:00",
            "time_range": {"start": "09:00", "end": "17:00"},
            "status_text": "Working"
        }]
        scheduler = Scheduler(self.mock_updater, intervals)
        
        # Should be active within time range
        test_time = datetime(2024, 1, 15, 12, 0)
        self.assertTrue(scheduler._is_interval_active(intervals[0], test_time))
        
        # Should not be active outside time range
        test_time = datetime(2024, 1, 15, 18, 0)
        self.assertFalse(scheduler._is_interval_active(intervals[0], test_time))

    def test_is_interval_active_combined_constraints(self):
        """Test interval with both day and time range constraints."""
        intervals = [{
            "time": "09:00",
            "days": "weekdays",
            "time_range": {"start": "09:00", "end": "17:00"},
            "status_text": "Working"
        }]
        scheduler = Scheduler(self.mock_updater, intervals)
        
        # Should be active on weekday within time range
        test_time = datetime(2024, 1, 15, 12, 0)  # Monday, 12:00
        self.assertTrue(scheduler._is_interval_active(intervals[0], test_time))
        
        # Should not be active on weekday outside time range
        test_time = datetime(2024, 1, 15, 18, 0)  # Monday, 18:00
        self.assertFalse(scheduler._is_interval_active(intervals[0], test_time))
        
        # Should not be active on weekend even within time range
        test_time = datetime(2024, 1, 20, 12, 0)  # Saturday, 12:00
        self.assertFalse(scheduler._is_interval_active(intervals[0], test_time))

    def test_get_current_job_no_active_intervals(self):
        """Test get_current_job when no intervals are active."""
        intervals = [{
            "time": "09:00",
            "days": "weekdays",
            "status_text": "Working"
        }]
        scheduler = Scheduler(self.mock_updater, intervals)
        
        # Mock datetime.now to return a Saturday
        with unittest.mock.patch('slack_status_updater.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 20, 12, 0)  # Saturday
            result = scheduler.get_current_job()
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()