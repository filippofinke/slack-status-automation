import logging
from slack_status_updater.app import SlackStatusUpdater

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def main() -> None:
    """Main function to run the Slack status updater."""
    app = SlackStatusUpdater()
    app.run()

if __name__ == "__main__":
    main()