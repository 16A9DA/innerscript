import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # Surface the active email backend on boot so a missing SENDGRID_API_KEY
        # (which silently falls back to the console backend) is obvious in logs.
        backend = settings.EMAIL_BACKEND
        logger.info("Email backend: %s", backend)
        if not settings.DEBUG and "console" in backend:
            logger.warning(
                "Console email backend in production: mail will NOT be "
                "delivered. Set SENDGRID_API_KEY."
            )
