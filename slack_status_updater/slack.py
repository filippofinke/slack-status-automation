import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

class SlackUpdater:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def set_status(self, presence: str, text: str = "", emoji: str = "") -> None:
        """
        Set the Slack presence and optional custom status for the authenticated user.
        This function logs its actions and catches `SlackApiError` to avoid
        crashing the scheduler loop.
        """
        try:
            self.client.users_setPresence(presence=presence)
            logger.info("Presence set to %s", presence)

            if text or emoji:
                profile = {
                    "status_text": text,
                    "status_emoji": emoji,
                    "status_expiration": 0,
                }
                self.client.users_profile_set(profile=profile)
                logger.info("Custom status set to '%s' %s", text, emoji)

        except SlackApiError as e:
            err = e.response.get("error") if hasattr(e, "response") else str(e)
            logger.error("Slack API error: %s", err)
