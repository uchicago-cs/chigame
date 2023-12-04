from django import forms
from machina.apps.forum.models import Forum


class ForumForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Forum
        fields = ["name", "description", "image", "type"]
        labels = {"image": "Upload forum image"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
