"""
Template tags allow us to embed more complex python code into templates
https://docs.djangoproject.com/en/4.2/howto/custom-template-tags/

Simple tags are used for generating a single value rather than an html template fragment
https://docs.djangoproject.com/en/4.2/howto/custom-template-tags/#simple-tags

To use a tag in a template:
1) First add {% load url_tags %} after extending previous templates
2) For a given simple tag <my_tag> use {% <my_tag> <param1> <param2> ... %} in the template
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def updated_params(context, **kwargs):
    """
    Returns an updated url given the current url and provided parameters to add or update.
    https://blog.ovalerio.net/archives/1512
    """
    dict_ = context["request"].GET.copy()
    for k, v in kwargs.items():
        dict_[k] = v
    return dict_.urlencode()
