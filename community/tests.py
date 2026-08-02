from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Post

User = get_user_model()


class PostDeleteTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.admin.profile.site_role = "admin"
        self.admin.profile.save(update_fields=["site_role"])
        self.author = User.objects.create_user("author", "author@x.com", "pw")
        self.author.profile.role = "student"
        self.author.profile.save(update_fields=["role"])
        self.stranger = User.objects.create_user("stranger", "stranger@x.com", "pw")
        self.stranger.profile.role = "student"
        self.stranger.profile.save(update_fields=["role"])
        self.post = Post.objects.create(author=self.author, title="X", body="x")

    def test_stranger_forbidden(self):
        self.client.force_login(self.stranger)
        resp = self.client.post(reverse("community:post_delete", args=[self.post.slug]))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_owner_deletes(self):
        self.client.force_login(self.author)
        resp = self.client.get(reverse("community:post_delete", args=[self.post.slug]))
        self.assertEqual(resp.status_code, 200)
        self.client.post(reverse("community:post_delete", args=[self.post.slug]))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_admin_deletes(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("community:post_delete", args=[self.post.slug]))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class CommentDeleteTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", "admin@x.com", "pw")
        self.admin.profile.site_role = "admin"
        self.admin.profile.save(update_fields=["site_role"])
        self.author = User.objects.create_user("author", "author@x.com", "pw")
        self.author.profile.role = "student"
        self.author.profile.save(update_fields=["role"])
        self.stranger = User.objects.create_user("stranger", "stranger@x.com", "pw")
        self.stranger.profile.role = "student"
        self.stranger.profile.save(update_fields=["role"])
        self.post = Post.objects.create(author=self.author, title="X", body="x")
        self.comment = Comment.objects.create(post=self.post, author=self.author, body="hi")

    def test_stranger_forbidden(self):
        self.client.force_login(self.stranger)
        resp = self.client.post(reverse("community:comment_delete", args=[self.comment.pk]))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_owner_deletes(self):
        self.client.force_login(self.author)
        resp = self.client.get(reverse("community:comment_delete", args=[self.comment.pk]))
        self.assertEqual(resp.status_code, 200)
        self.client.post(reverse("community:comment_delete", args=[self.comment.pk]))
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_admin_deletes(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("community:comment_delete", args=[self.comment.pk]))
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


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
