from django import forms

class BGGSearchForm(forms.Form):
    bgg_search_term = forms.CharField(label='Search BoardGameGeek', max_length=100)
