from django import forms

from config.uploads import validate_image

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["category", "title", "body", "image", "is_public"]

    def clean_image(self):
        return validate_image(self.cleaned_data.get("image"))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Share an insight..."})}
