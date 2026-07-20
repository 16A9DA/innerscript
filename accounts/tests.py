from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.adapter import MinimalSocialAccountAdapter

User = get_user_model()


@override_settings(ADMIN_EMAILS={"admin@x.com"}, MEMBER_EMAILS={"admin@x.com"})
class AdminUserDeleteTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.target = User.objects.create_user("target", "target@x.com", "pw")

    def test_non_admin_forbidden(self):
        self.client.force_login(self.target)
        resp = self.client.post(reverse("accounts:admin_user_delete", args=["admin"]))
        self.assertEqual(resp.status_code, 403)

    def test_admin_deletes_other(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("accounts:admin_user_delete", args=["target"]))
        self.assertFalse(User.objects.filter(username="target").exists())

    def test_admin_cannot_self_delete(self):
        self.client.force_login(self.admin)
        resp = self.client.post(reverse("accounts:admin_user_delete", args=["admin"]))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(User.objects.filter(username="admin").exists())


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


class SignupRoleTests(TestCase):
    def _post(self, role=""):
        return self.client.post(reverse("account_signup"), {
            "email": "new@x.com",
            "username": "newperson",
            "role": role,
            "password1": "a-strong-pw-123",
            "password2": "a-strong-pw-123",
        })

    def test_role_required(self):
        resp = self._post(role="")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="newperson").exists())

    def test_role_saved_on_signup(self):
        self._post(role="researcher")
        user = User.objects.get(username="newperson")
        self.assertEqual(user.profile.role, "researcher")


@override_settings(ACCOUNT_RATE_LIMITS=False)  # isolate axes; allauth has its own separate limiter
class LoginRateLimitTests(TestCase):
    def setUp(self):
        User.objects.create_user("victim", "victim@x.com", "correct-pw")

    def test_locked_out_after_repeated_failures(self):
        for _ in range(5):
            self.client.post(reverse("account_login"), {"login": "victim@x.com", "password": "wrong"})
        resp = self.client.post(reverse("account_login"), {"login": "victim@x.com", "password": "correct-pw"})
        self.assertContains(resp, "Account locked", status_code=429)
