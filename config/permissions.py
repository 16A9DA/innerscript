"""WorkOS-metadata-driven site roles, separate from Django is_staff/is_superuser."""


def is_admin(user):
    return user.is_authenticated and user.profile.site_role == "admin"


def is_member(user):
    return user.is_authenticated and user.profile.site_role in ("admin", "member")
