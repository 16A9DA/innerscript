"""Email-list based site roles, separate from Django is_staff/is_superuser."""

from django.conf import settings


def is_admin(user):
    return user.is_authenticated and user.email.lower() in settings.ADMIN_EMAILS


def is_member(user):
    return user.is_authenticated and user.email.lower() in settings.MEMBER_EMAILS
