from django import template

from ..utils import ProfanityFilter

register = template.Library()
pf = ProfanityFilter()


@register.filter(name="profanity_filter")
def profanity_filter_tag(text):
    return pf.censor_message(text)
