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


@override_settings(ADMIN_EMAILS={"admin@x.com"}, MEMBER_EMAILS={"member@x.com", "admin@x.com"})
class PermissionTests(TestCase):
    def test_is_admin_is_member(self):
        admin = User.objects.create_user("admin", "admin@x.com", "pw")
        member = User.objects.create_user("member", "member@x.com", "pw")
        regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.assertTrue(is_admin(admin))
        self.assertTrue(is_member(admin))
        self.assertFalse(is_admin(member))
        self.assertTrue(is_member(member))
        self.assertFalse(is_admin(regular))
        self.assertFalse(is_member(regular))


@override_settings(ADMIN_EMAILS={"admin@x.com"}, MEMBER_EMAILS={"member@x.com", "admin@x.com"})
class ToolkitUploadTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user("member", "member@x.com", "pw")
        self.regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.pdf = SimpleUploadedFile("guide.pdf", _one_page_pdf_bytes(), content_type="application/pdf")

    def _post(self):
        return self.client.post(reverse("pages:toolkit_upload"), {
            "title": "Coping Guide", "description": "x", "topic": "", "file": self.pdf,
        })

    def test_non_member_forbidden(self):
        self.client.force_login(self.regular)
        self.assertEqual(self._post().status_code, 403)

    def test_member_upload_pending_with_preview(self):
        self.client.force_login(self.member)
        self._post()
        toolkit = Toolkit.objects.get(title="Coping Guide")
        self.assertFalse(toolkit.is_approved)
        self.assertTrue(toolkit.preview_image)
        self.assertNotIn(toolkit, Toolkit.objects.filter(is_approved=True))


@override_settings(ADMIN_EMAILS={"admin@x.com"}, MEMBER_EMAILS={"admin@x.com"})
class ToolkitApproveTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.regular = User.objects.create_user("regular", "reg@x.com", "pw")
        self.toolkit = Toolkit.objects.create(title="Pending", description="x")

    def test_non_admin_forbidden(self):
        self.client.force_login(self.regular)
        resp = self.client.post(reverse("pages:toolkit_approve", args=[self.toolkit.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_admin_approve(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("pages:toolkit_approve", args=[self.toolkit.pk]))
        self.toolkit.refresh_from_db()
        self.assertTrue(self.toolkit.is_approved)
