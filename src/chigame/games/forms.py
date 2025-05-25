from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import Game, Lobby, Review


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


class IFGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "description", "image", "categories", "suggested_age", "rules", "year_published"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set fields automatically
        instance.min_players = 1  # typically IF is single-player
        instance.max_players = 1
        # Add any other field defaults
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class LobbyForm(forms.ModelForm):
    class Meta:
        model = Lobby
        fields = ["name", "game", "game_mod_status", "min_players", "max_players", "time_constraint"]
        widgets = {"name": forms.TextInput}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["title", "review", "rating", "is_public"]

    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Title (optional)"}), required=False)
    review = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Your review"}), required=False)
    rating = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "Rating (1-5)"}),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        required=False,
    )
    is_public = forms.BooleanField(initial=True, required=False)

    def clean(self):
        cleaned_data = super().clean()
        review = cleaned_data.get("review")
        rating = cleaned_data.get("rating")

        if not review and rating is None:
            raise forms.ValidationError("At least one of 'review' or 'rating' must be provided.")
