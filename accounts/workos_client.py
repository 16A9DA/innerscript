from django.conf import settings
from workos import WorkOSClient

workos_client = WorkOSClient(
    api_key=settings.WORKOS_API_KEY, client_id=settings.WORKOS_CLIENT_ID
)
