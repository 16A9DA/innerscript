from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AdminUserDeleteTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.admin.profile.site_role = "admin"
        self.admin.profile.save(update_fields=["site_role"])
        self.target = User.objects.create_user("target", "target@x.com", "pw")
        self.target.profile.role = "student"
        self.target.profile.save(update_fields=["role"])

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


class WorkOSLoginTests(TestCase):
    def test_login_redirects_to_authkit(self):
        with patch(
            "accounts.views.workos_client.user_management.get_authorization_url",
            return_value="https://auth.workos.com/sso/authorize?x=1",
        ) as mocked:
            resp = self.client.get(reverse("account_login"))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "https://auth.workos.com/sso/authorize?x=1")
        self.assertEqual(mocked.call_args.kwargs["screen_hint"], "sign-in")

    def _wos_user(self, **overrides):
        defaults = dict(
            id="user_01", email="new@x.com", first_name="Ada",
            last_name="L", email_verified=True, metadata={},
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_callback_creates_new_user_and_prompts_for_role(self):
        auth_response = SimpleNamespace(user=self._wos_user())
        with patch(
            "accounts.views.workos_client.user_management.authenticate_with_code",
            return_value=auth_response,
        ):
            resp = self.client.get(reverse("workos_callback"), {"code": "abc"})
        user = User.objects.get(email="new@x.com")
        self.assertEqual(user.profile.workos_user_id, "user_01")
        self.assertRedirects(resp, reverse("accounts:profile_edit"))

    def test_callback_links_existing_verified_email(self):
        existing = User.objects.create_user("ada", "ada@x.com", "pw")
        existing.profile.role = "student"
        existing.profile.save(update_fields=["role"])
        auth_response = SimpleNamespace(
            user=self._wos_user(id="user_02", email="ada@x.com")
        )
        with patch(
            "accounts.views.workos_client.user_management.authenticate_with_code",
            return_value=auth_response,
        ):
            resp = self.client.get(reverse("workos_callback"), {"code": "abc"})
        existing.profile.refresh_from_db()
        self.assertEqual(existing.profile.workos_user_id, "user_02")
        self.assertEqual(User.objects.filter(email__iexact="ada@x.com").count(), 1)
        self.assertRedirects(resp, "/")

    def test_callback_rejects_unverified_email_linkage(self):
        User.objects.create_user("ada", "ada@x.com", "pw")
        auth_response = SimpleNamespace(
            user=self._wos_user(id="user_03", email="ada@x.com", email_verified=False)
        )
        with patch(
            "accounts.views.workos_client.user_management.authenticate_with_code",
            return_value=auth_response,
        ):
            self.client.get(reverse("workos_callback"), {"code": "abc"})
        self.assertEqual(User.objects.filter(email__iexact="ada@x.com").count(), 2)

    def test_callback_syncs_site_role_from_metadata(self):
        auth_response = SimpleNamespace(
            user=self._wos_user(metadata={"site_role": "admin"})
        )
        with patch(
            "accounts.views.workos_client.user_management.authenticate_with_code",
            return_value=auth_response,
        ):
            self.client.get(reverse("workos_callback"), {"code": "abc"})
        user = User.objects.get(email="new@x.com")
        self.assertEqual(user.profile.site_role, "admin")

    def test_account_delete_calls_workos_delete_user(self):
        user = User.objects.create_user("bob", "bob@x.com", "pw")
        user.profile.workos_user_id = "user_04"
        user.profile.role = "student"
        user.profile.save(update_fields=["workos_user_id", "role"])
        self.client.force_login(user)
        with patch(
            "accounts.views.workos_client.user_management.delete_user"
        ) as mocked_delete:
            self.client.post(reverse("accounts:account_delete"))
        mocked_delete.assert_called_once_with("user_04")
        self.assertFalse(User.objects.filter(username="bob").exists())


class ProfileCompletionMiddlewareTests(TestCase):
    def test_roleless_user_redirected_to_profile_edit(self):
        user = User.objects.create_user("noro", "noro@x.com", "pw")
        self.client.force_login(user)
        resp = self.client.get(reverse("pages:home"))
        self.assertRedirects(resp, reverse("accounts:profile_edit"))

    def test_user_with_role_not_redirected(self):
        user = User.objects.create_user("hasrole", "hasrole@x.com", "pw")
        user.profile.role = "student"
        user.profile.save(update_fields=["role"])
        self.client.force_login(user)
        resp = self.client.get(reverse("pages:home"))
        self.assertEqual(resp.status_code, 200)
