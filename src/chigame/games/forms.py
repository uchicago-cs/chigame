from django import forms

from .models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = "__all__"
        labels = {
            "complexity": "Complexity (1-5 scale)",
            "expected_playtime": "Expected playtime (minutes)",
            "min_playtime": "Min playtime (minutes)",
            "max_playtime": "Max playtime (minutes)",
            "image": "External Image URL (optional)",
        }
        widgets = {
            "name": forms.TextInput,
            "image": forms.Textarea(attrs={"cols": 80, "rows": 1}),
        }
