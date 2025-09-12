import logging
from .config import load_config, validate_config, get_slack_token, ConfigError
from .slack import SlackUpdater
from .scheduler import Scheduler

logger = logging.getLogger(__name__)

class SlackStatusUpdater:
    """
    The main application class that orchestrates the status updates.
    """
    def __init__(self):
        self.updater: SlackUpdater | None = None
        self.scheduler: Scheduler | None = None

    def _setup(self) -> bool:
        """
        Loads configuration and sets up the updater and scheduler.
        Returns True on success, False on failure.
        """
        try:
            config = load_config()
            validate_config(config)
        except ConfigError as e:
            logger.error(e)
            logger.error("Fix the configuration and try again")
            return False

        token = get_slack_token(config)
        if not token:
            logger.error("Slack token is not configured.")
            return False

        self.updater = SlackUpdater(token)
        intervals = config.get("intervals", [])
        self.scheduler = Scheduler(self.updater, intervals)
        return True

    def run(self) -> None:
        """
        Runs the Slack status updater application.
        """
        if not self._setup() or not self.updater or not self.scheduler:
            return

        try:
            # Set initial status
            current_job = self.scheduler.get_current_job()
            if current_job:
                self.updater.set_status(
                    presence=current_job.get("presence", "auto"),
                    text=current_job.get("status_text", ""),
                    emoji=current_job.get("status_emoji", ""),
                )
                logger.info("Initial status set based on current schedule")
            else:
                logger.info("No active schedule for current time/day - status not updated")

            # Schedule future updates
            self.scheduler.schedule_jobs()

            # Run the scheduler
            self.scheduler.run_forever()

        except (KeyboardInterrupt, SystemExit):
            logger.info("Interrupted, shutting down")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
