from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from config.permissions import is_admin, is_member
from .models import Toolkit

User = get_user_model()


def _one_page_pdf_bytes():
    import fitz
    doc = fitz.open()
    doc.new_page()
    return doc.tobytes()


class PermissionTests(TestCase):
    def test_is_admin_is_member(self):
        admin = User.objects.create_user("admin", "admin@x.com", "pw")
        admin.profile.site_role = "admin"
        admin.profile.save(update_fields=["site_role"])
        member = User.objects.create_user("member", "member@x.com", "pw")
        member.profile.site_role = "member"
        member.profile.save(update_fields=["site_role"])
        regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.assertTrue(is_admin(admin))
        self.assertTrue(is_member(admin))
        self.assertFalse(is_admin(member))
        self.assertTrue(is_member(member))
        self.assertFalse(is_admin(regular))
        self.assertFalse(is_member(regular))

    @override_settings(SUPERADMIN_EMAILS={"boss@x.com"})
    def test_superadmin_email_override(self):
        boss = User.objects.create_user("boss", "boss@x.com", "pw")
        self.assertTrue(is_admin(boss))
        self.assertTrue(is_member(boss))


class ToolkitUploadTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user("member", "member@x.com", "pw")
        self.member.profile.role = "student"
        self.member.profile.site_role = "member"
        self.member.profile.save(update_fields=["role", "site_role"])
        self.regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.regular.profile.role = "student"
        self.regular.profile.save(update_fields=["role"])
        self.pdf = SimpleUploadedFile("guide.pdf", _one_page_pdf_bytes(), content_type="application/pdf")

    def _post(self):
        return self.client.post(reverse("pages:toolkit_upload"), {
            "title": "Coping Guide", "description": "x", "topic": "", "file": self.pdf,
        })

    def test_anonymous_forbidden(self):
        resp = self._post()
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Toolkit.objects.filter(title="Coping Guide").exists())

    def test_regular_user_upload_pending_with_preview(self):
        self.client.force_login(self.regular)
        self._post()
        toolkit = Toolkit.objects.get(title="Coping Guide")
        self.assertFalse(toolkit.is_approved)
        self.assertTrue(toolkit.preview_image)
        self.assertNotIn(toolkit, Toolkit.objects.filter(is_approved=True))

    def test_member_upload_pending_with_preview(self):
        self.client.force_login(self.member)
        self._post()
        toolkit = Toolkit.objects.get(title="Coping Guide")
        self.assertFalse(toolkit.is_approved)
        self.assertTrue(toolkit.preview_image)
        self.assertNotIn(toolkit, Toolkit.objects.filter(is_approved=True))


class ToolkitApproveTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.admin.profile.site_role = "admin"
        self.admin.profile.save(update_fields=["site_role"])
        self.member = User.objects.create_user("member", "member@x.com", "pw")
        self.member.profile.role = "student"
        self.member.profile.site_role = "member"
        self.member.profile.save(update_fields=["role", "site_role"])
        self.regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.regular.profile.role = "student"
        self.regular.profile.save(update_fields=["role"])
        self.toolkit = Toolkit.objects.create(title="Pending", description="x")

    def test_non_member_forbidden(self):
        self.client.force_login(self.regular)
        resp = self.client.post(reverse("pages:toolkit_approve", args=[self.toolkit.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_admin_approve(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("pages:toolkit_approve", args=[self.toolkit.pk]))
        self.toolkit.refresh_from_db()
        self.assertTrue(self.toolkit.is_approved)

    def test_member_approve(self):
        self.client.force_login(self.member)
        self.client.post(reverse("pages:toolkit_approve", args=[self.toolkit.pk]))
        self.toolkit.refresh_from_db()
        self.assertTrue(self.toolkit.is_approved)


class ToolkitDeleteTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user("member", "member@x.com", "pw")
        self.member.profile.role = "student"
        self.member.profile.site_role = "member"
        self.member.profile.save(update_fields=["role", "site_role"])
        self.regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.regular.profile.role = "student"
        self.regular.profile.save(update_fields=["role"])
        self.toolkit = Toolkit.objects.create(title="Guide", description="x")
        self.own_toolkit = Toolkit.objects.create(title="Mine", description="x", uploaded_by=self.regular)

    def test_non_member_forbidden(self):
        self.client.force_login(self.regular)
        resp = self.client.post(reverse("pages:toolkit_delete", args=[self.toolkit.pk]))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Toolkit.objects.filter(pk=self.toolkit.pk).exists())

    def test_owner_deletes(self):
        self.client.force_login(self.regular)
        resp = self.client.get(reverse("pages:toolkit_delete", args=[self.own_toolkit.pk]))
        self.assertEqual(resp.status_code, 200)
        self.client.post(reverse("pages:toolkit_delete", args=[self.own_toolkit.pk]))
        self.assertFalse(Toolkit.objects.filter(pk=self.own_toolkit.pk).exists())

    def test_member_delete(self):
        self.client.force_login(self.member)
        self.client.post(reverse("pages:toolkit_delete", args=[self.toolkit.pk]))
        self.assertFalse(Toolkit.objects.filter(pk=self.toolkit.pk).exists())
