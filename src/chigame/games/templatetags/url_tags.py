from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def updated_params(context, **kwargs):
    dict_ = context["request"].GET.copy()
    for k, v in kwargs.items():
        dict_[k] = v
    return dict_.urlencode()
