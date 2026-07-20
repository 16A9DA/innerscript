from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from config.uploads import avatar_path


class Profile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("young_adult", "Young Adult"),
        ("parent", "Parent"),
        ("caregiver", "Caregiver"),
        ("educator", "Educator"),
        ("mental_health_professional", "Mental Health Professional"),
        ("healthcare_professional", "Healthcare Professional"),
        ("researcher", "Researcher"),
        ("advocate", "Advocate"),
        ("other", "Other"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_path, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, blank=True)
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
