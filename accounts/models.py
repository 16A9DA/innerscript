from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from config.uploads import avatar_path


class Profile(models.Model):
    ROLE_CHOICES = [
        ("youth", "Youth"),
        ("educator", "Educator"),
        ("clinician", "Clinician"),
        ("supporter", "Supporter"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_path, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="youth")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @property
    def initial(self):
        return (self.user.username[:1] or "?").upper()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
