from django.conf import settings
from django.db import models

from config.uploads import toolkit_pdf_path, toolkit_preview_path, validate_pdf


class Toolkit(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField()
    link = models.URLField(blank=True)
    file = models.FileField(upload_to=toolkit_pdf_path, blank=True, validators=[validate_pdf])
    preview_image = models.ImageField(upload_to=toolkit_preview_path, blank=True, editable=False)
    topic = models.CharField(max_length=80, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="toolkits"
    )
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        needs_preview = self.file and not self.preview_image
        super().save(*args, **kwargs)
        if needs_preview:
            self._generate_preview()

    def _generate_preview(self):
        import fitz
        from django.core.files.base import ContentFile

        self.file.open("rb")
        try:
            doc = fitz.open(stream=self.file.read(), filetype="pdf")
            page = doc.load_page(0)
            png_bytes = page.get_pixmap().tobytes("png")
        finally:
            self.file.close()
        self.preview_image.save(f"{self.pk}.png", ContentFile(png_bytes), save=True)
