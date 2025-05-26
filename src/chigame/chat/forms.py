from django import forms

from .models import LiveChat


class LiveChatForm(forms.ModelForm):
    class Meta:
        model = LiveChat
        fields = ["name", "description", "public"]
