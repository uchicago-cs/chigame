from django import forms

from .models import Game, Lobby


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


class LobbyForm(forms.ModelForm):
    class Meta:
        model = Lobby
        fields = ['name', 'game', 'game_mod_status', 'min_players', 'max_players', 'time_constraint', 'lobby_created']
        widgets = {
            "name": forms.TextInput
        }