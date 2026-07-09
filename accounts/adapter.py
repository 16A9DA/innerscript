import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


class LoggingAccountAdapter(DefaultAccountAdapter):
    """Never let a mail-server failure become a 500.

    Signup verification and password reset send mail synchronously; if SMTP
    is down or rejects auth, allauth would bubble the exception into a 500
    (blank error page). We log the real cause and continue so the user sees
    the normal flow instead of a crash.
    """

    def send_mail(self, template_prefix, email, context):
        try:
            super().send_mail(template_prefix, email, context)
        except Exception:
            logger.exception("Email send failed for %s (%s)", email, template_prefix)


class MinimalSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Data minimization: keep only the user's name and email.

    Google returns a large profile payload (picture, locale, sub, etc.).
    We refuse to persist any of it beyond name + email. Enforced here so the
    database never holds more than the privacy policy promises.
    """

    def save_user(self, request, sociallogin, form=None):
        raw = sociallogin.account.extra_data or {}
        name = raw.get("name") or " ".join(
            filter(None, [raw.get("given_name"), raw.get("family_name")])
        )
        sociallogin.account.extra_data = {
            "email": raw.get("email", ""),
            "name": name,
        }
        return super().save_user(request, sociallogin, form)
