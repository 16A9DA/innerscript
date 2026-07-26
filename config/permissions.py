"""WorkOS-metadata-driven site roles, separate from Django is_staff/is_superuser."""

from django.conf import settings


def _is_superadmin_email(user):
    return user.is_authenticated and user.email.lower() in settings.SUPERADMIN_EMAILS


def is_admin(user):
    return _is_superadmin_email(user) or (
        user.is_authenticated and user.profile.site_role == "admin"
    )


def is_member(user):
    return _is_superadmin_email(user) or (
        user.is_authenticated and user.profile.site_role in ("admin", "member")
    )
