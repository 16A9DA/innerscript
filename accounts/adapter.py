from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


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
