from django import forms
from .models import *

class MatchInitForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['game', 'lobby', 'winners', 'players']

