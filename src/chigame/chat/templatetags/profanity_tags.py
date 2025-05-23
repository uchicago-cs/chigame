from django import template

from ..utils import ProfanityFilter

register = template.Library()


@register.filter(name="profanity_filter")
def profanity_filter_tag(text):
    return ProfanityFilter().censor(text)
