from django.db import models


class Toolkit(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField()
    link = models.URLField(blank=True)
    file = models.FileField(upload_to="toolkits/", blank=True)
    topic = models.CharField(max_length=80, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title
