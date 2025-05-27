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

    def clean(self):
        """
        Making sure that the user can't both completely opt out and appear
        anonymously with the form.
        """

        cleaned = super().clean()
        opt_out = cleaned.get("complete_opt_out")
        anon = cleaned.get("display_as_anonymous")
        if opt_out and anon:
            raise forms.ValidationError("You can't both completely opt out and appear anonymously.")
        return cleaned
