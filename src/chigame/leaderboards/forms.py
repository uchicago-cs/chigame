from django import forms

from .models import LeaderboardPrivacySetting


class LeaderboardPrivacySettingForm(forms.ModelForm):
    class Meta:
        model = LeaderboardPrivacySetting
        fields = [
            "complete_opt_out",
            "display_as_anonymous",
        ]
        widgets = {
            "complete_opt_out": forms.CheckboxInput(),
            "display_as_anonymous": forms.CheckboxInput(),
        }
        labels = {
            "complete_opt_out": "Opt out of this leaderboard entirely",
            "display_as_anonymous": "Show my scores anonymously",
        }
        help_texts = {
            "complete_opt_out": "If checked, your scores will not appear on this leaderboard",
            "display_as_anonymous": "If checked, your scores will be visible but your username will be hidden",
        }
