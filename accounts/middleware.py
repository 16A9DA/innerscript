from django.shortcuts import redirect
from django.urls import reverse

from config.permissions import is_admin

EXEMPT_URL_NAMES = ["account_login", "account_signup", "account_logout", "workos_callback"]


class ProfileCompletionMiddleware:
    """Mandatory-role enforcement now that WorkOS owns the signup UI.

    Redirects any authenticated user with a blank Profile.role to
    profile_edit until they set one, mirroring the old allauth
    signup-form requirement.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._exempt_paths = None

    @property
    def exempt_paths(self):
        if self._exempt_paths is None:
            self._exempt_paths = {reverse(name) for name in EXEMPT_URL_NAMES} | {
                reverse("accounts:profile_edit")
            }
        return self._exempt_paths

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_staff
            and not is_admin(request.user)
            and not request.path.startswith("/admin/")
            and not request.path.startswith("/static/")
            and not request.path.startswith("/media/")
            and not request.user.profile.role
            and request.path not in self.exempt_paths
        ):
            return redirect("accounts:profile_edit")
        return self.get_response(request)
