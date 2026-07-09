from django import forms
from django.contrib.auth import get_user_model

from config.uploads import validate_image

from .models import Profile

User = get_user_model()


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=User._meta.get_field("username").validators,
    )

    class Meta:
        model = Profile
        fields = ["bio", "avatar", "role"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}
        field_order = ["username", "bio", "avatar", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].initial = self.instance.user.username

    def clean_username(self):
        name = self.cleaned_data["username"]
        taken = User.objects.exclude(pk=self.instance.user_id).filter(
            username__iexact=name
        )
        if taken.exists():
            raise forms.ValidationError("That username is already taken.")
        return name

    def clean_avatar(self):
        return validate_image(self.cleaned_data.get("avatar"))

    def save(self, commit=True):
        prof = super().save(commit)
        user = prof.user
        user.username = self.cleaned_data["username"]
        if commit:
            user.save(update_fields=["username"])
        return prof
