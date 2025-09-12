import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def main() -> None:
    """Main function to run the Slack status updater."""
    from slack_status_updater.app import SlackStatusUpdater
    app = SlackStatusUpdater()
    app.run()

if __name__ == "__main__":
    # parse CLI option for calendar interval before importing app so the calendar module default can be set
    parser = argparse.ArgumentParser(description="Run Slack status updater")
    parser.add_argument(
        "--calendar-interval",
        choices=["30", "60"],
        default="30",
        help="Calendar resolution in minutes (30 or 60). Default: 30",
    )
    args = parser.parse_args()

    # set the default in the calendar module so callers that don't pass interval_minutes pick it up
    import importlib
    try:
        calendar_mod = importlib.import_module("slack_status_updater.calendar")
        calendar_mod.DEFAULT_INTERVAL = int(args.calendar_interval)
    except Exception:
        # if calendar module isn't importable for some reason, ignore and continue
        pass

    main()