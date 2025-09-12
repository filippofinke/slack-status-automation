import logging
import time
from typing import Any, Dict, List, Optional

import schedule

from .slack import SlackUpdater
from .utils import parse_time, parse_days, is_time_in_range, is_day_match
from datetime import datetime

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, updater: SlackUpdater, intervals: List[Dict[str, Any]]):
        self.updater = updater
        self.intervals = sorted(intervals, key=lambda j: parse_time(j["time"]))

    def _is_interval_active(self, interval: Dict[str, Any], current_time: datetime) -> bool:
        """Check if an interval should be active at the current time."""
        # Check day constraints
        if "days" in interval:
            allowed_days = parse_days(interval["days"])
            if not is_day_match(current_time.weekday(), allowed_days):
                return False
        
        # Check time range constraints
        if "time_range" in interval:
            time_range = interval["time_range"]
            start_time = parse_time(time_range["start"])
            end_time = parse_time(time_range["end"])
            if not is_time_in_range(current_time.time(), start_time, end_time):
                return False
        
        return True

    def get_current_job(self) -> Optional[Dict[str, Any]]:
        """Return the interval (job) that matches the current time."""
        now = datetime.now()
        
        if not self.intervals:
            raise ValueError("No intervals configured")

        # Filter intervals that are active for current day/time constraints
        active_intervals = [job for job in self.intervals if self._is_interval_active(job, now)]
        
        if not active_intervals:
            # If no intervals are active, return None to indicate no status should be set
            return None

        # Find the active interval that matches current time
        for i, job in enumerate(active_intervals):
            start_time = parse_time(job["time"])
            next_job = active_intervals[(i + 1) % len(active_intervals)]
            end_time = parse_time(next_job["time"])

            if start_time <= end_time:
                if start_time <= now.time() < end_time:
                    return job
            else:
                if now.time() >= start_time or now.time() < end_time:
                    return job
        
        return active_intervals[-1] if active_intervals else None

    def _schedule_interval_job(self, interval: Dict[str, Any]) -> None:
        """Schedule a specific interval job with day constraints."""
        job_time = interval["time"]
        
        def status_update_job():
            # Double-check if the job should run at execution time
            if self._is_interval_active(interval, datetime.now()):
                self.updater.set_status(
                    presence=interval.get("presence", "auto"),
                    text=interval.get("status_text", ""),
                    emoji=interval.get("status_emoji", ""),
                )
            else:
                logger.debug(f"Skipping job at {job_time} - not active for current day/time constraints")
        
        if "days" in interval:
            # Schedule for specific days
            allowed_days = parse_days(interval["days"])
            day_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            
            for day_num in allowed_days:
                day_name = day_map[day_num]
                getattr(schedule.every(), day_name).at(job_time).do(status_update_job)
                logger.info(
                    "Scheduled %s on %s at %s with '%s' %s",
                    interval.get("presence", "auto"),
                    day_name,
                    job_time,
                    interval.get("status_text", ""),
                    interval.get("status_emoji", ""),
                )
        else:
            # Schedule for every day (backwards compatibility)
            schedule.every().day.at(job_time).do(status_update_job)
            logger.info(
                "Scheduled %s at %s with '%s' %s",
                interval.get("presence", "auto"),
                job_time,
                interval.get("status_text", ""),
                interval.get("status_emoji", ""),
            )

    def schedule_jobs(self) -> None:
        """Schedule all status updates."""
        for interval in self.intervals:
            self._schedule_interval_job(interval)

    def run_forever(self) -> None:
        """Run the scheduler indefinitely."""
        logger.info("Scheduler running...")
        while True:
            schedule.run_pending()
            time.sleep(1)
