from django import template

from chigame.games.models import Game

register = template.Library()


@register.simple_tag
def get_games():
    game_list = Game.objects.all()
    return game_list
