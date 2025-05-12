from django import forms
from django.core.exceptions import ValidationError

from .models import Game


class MarkdownUploadForm(forms.Form):
    game = forms.ModelChoiceField(queryset=Game.objects.all())
    file = forms.FileField(label="Markdown File:")

    def __init__(self, *args, fixed_game=None, **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_game:
            self.fields["game"].initial = fixed_game
            self.fields["game"].disabled = True  # user can't change it

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.endswith(".md"):
            raise ValidationError("Only .md (Markdown) files are allowed.")
        return uploaded_file
