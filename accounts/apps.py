import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        if not (settings.WORKOS_API_KEY and settings.WORKOS_CLIENT_ID):
            logger.warning("WORKOS_API_KEY/WORKOS_CLIENT_ID missing: login will fail.")
