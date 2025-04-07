from django import template

register = template.Library()


def get_dict_val(dict, key):
    """Returns the value corresponding to a key in a dictionary"""
    return dict.get(key)


register.filter("get_dict_val", get_dict_val)
