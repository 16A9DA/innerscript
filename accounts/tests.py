from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from accounts.adapter import MinimalSocialAccountAdapter


class MinimalSocialAdapterTests(TestCase):
    def _run(self, extra):
        account = SimpleNamespace(extra_data=extra)
        sociallogin = SimpleNamespace(account=account)
        adapter = MinimalSocialAccountAdapter()
        # Stub allauth's DB-touching parent; we only test the stripping logic.
        with patch(
            "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.save_user",
            lambda self, r, s, form=None: s,
        ):
            adapter.save_user(None, sociallogin)
        return account.extra_data

    def test_strips_everything_but_name_and_email(self):
        result = self._run({
            "email": "a@b.com",
            "name": "Ada L",
            "picture": "http://x/p.jpg",
            "locale": "en",
            "sub": "12345",
        })
        self.assertEqual(set(result), {"email", "name"})
        self.assertEqual(result["email"], "a@b.com")
        self.assertEqual(result["name"], "Ada L")

    def test_builds_name_from_given_family(self):
        result = self._run({"given_name": "Ada", "family_name": "Lovelace"})
        self.assertEqual(result["name"], "Ada Lovelace")
        self.assertEqual(result["email"], "")
