from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Post

User = get_user_model()


@override_settings(ADMIN_EMAILS={"admin@x.com"}, MEMBER_EMAILS={"admin@x.com"})
class PostDeleteTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.author = User.objects.create_user("author", "author@x.com", "pw")
        self.post = Post.objects.create(author=self.author, title="X", body="x")

    def test_non_admin_forbidden(self):
        self.client.force_login(self.author)
        resp = self.client.post(reverse("community:post_delete", args=[self.post.slug]))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_admin_deletes(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("community:post_delete", args=[self.post.slug]))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class FeedAudienceFilterTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staffer", "staff@x.com", "pw", is_staff=True)
        self.pro = User.objects.create_user("pro", "pro@x.com", "pw")
        self.pro.profile.role = "healthcare_professional"
        self.pro.profile.save(update_fields=["role"])
        self.regular = User.objects.create_user("regular", "reg@x.com", "pw")
        Post.objects.create(author=self.staff, title="Team post", body="x")
        Post.objects.create(author=self.pro, title="Pro post", body="x")
        Post.objects.create(author=self.regular, title="Regular post", body="x")

    def test_team_filter(self):
        resp = self.client.get(reverse("community:feed"), {"audience": "team"})
        titles = {p.title for p in resp.context["posts"]} | ({resp.context["featured"].title} if resp.context["featured"] else set())
        self.assertEqual(titles, {"Team post"})

    def test_professional_filter(self):
        resp = self.client.get(reverse("community:feed"), {"audience": "professional"})
        titles = {p.title for p in resp.context["posts"]} | ({resp.context["featured"].title} if resp.context["featured"] else set())
        self.assertEqual(titles, {"Pro post"})

    def test_no_filter_shows_everyone(self):
        resp = self.client.get(reverse("community:feed"))
        titles = {p.title for p in resp.context["posts"]} | ({resp.context["featured"].title} if resp.context["featured"] else set())
        self.assertEqual(titles, {"Team post", "Pro post", "Regular post"})
