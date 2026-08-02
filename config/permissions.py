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


def can_delete_post(user, post):
    return is_admin(user) or post.author == user


def can_delete_comment(user, comment):
    return is_admin(user) or comment.author == user


def can_delete_toolkit(user, toolkit):
    return is_member(user) or toolkit.uploaded_by == user
