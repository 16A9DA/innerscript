from django import forms

from config.uploads import validate_image

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "role"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def clean_avatar(self):
        return validate_image(self.cleaned_data.get("avatar"))
