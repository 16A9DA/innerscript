from django import forms

from .models import Toolkit


class ToolkitForm(forms.ModelForm):
    class Meta:
        model = Toolkit
        fields = ["title", "description", "topic", "file"]
