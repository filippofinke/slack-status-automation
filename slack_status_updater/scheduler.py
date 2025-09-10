import logging
import time
from typing import Any, Dict, List

import schedule

from .slack import SlackUpdater
from .utils import parse_time
from datetime import datetime

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, updater: SlackUpdater, intervals: List[Dict[str, Any]]):
        self.updater = updater
        self.intervals = sorted(intervals, key=lambda j: parse_time(j["time"]))

    def get_current_job(self) -> Dict[str, Any]:
        """Return the interval (job) that matches the current time."""
        now = datetime.now().time()

        if not self.intervals:
            raise ValueError("No intervals configured")

        for i, job in enumerate(self.intervals):
            start_time = parse_time(job["time"])
            next_job = self.intervals[(i + 1) % len(self.intervals)]
            end_time = parse_time(next_job["time"])

            if start_time <= end_time:
                if start_time <= now < end_time:
                    return job
            else:
                if now >= start_time or now < end_time:
                    return job
        return self.intervals[-1]

    def schedule_jobs(self) -> None:
        """Schedule all status updates."""
        for job in self.intervals:
            schedule.every().day.at(job["time"]).do(
                self.updater.set_status,
                presence=job.get("presence", "auto"),
                text=job.get("status_text", ""),
                emoji=job.get("status_emoji", ""),
            )
            logger.info(
                "Scheduled %s at %s with '%s' %s",
                job.get("presence"),
                job["time"],
                job.get("status_text", ""),
                job.get("status_emoji", ""),
            )

    def run_forever(self) -> None:
        """Run the scheduler indefinitely."""
        logger.info("Scheduler running...")
        while True:
            schedule.run_pending()
            time.sleep(1)
