from django import template

from chigame.games.models import Game, Player

# in order to crete new tags, a module-level instance of a template.Library
# object must be created that custom tags will be registered to. More information
# about creating custom tags here https://docs.djangoproject.com/en/4.2/howto/custom-template-tags/
register = template.Library()


# create a new tag called get_games that returns all Game objects
@register.simple_tag
def get_games():
    game_list = Game.objects.all()
    return game_list


# filter to get the Player object for a given user and match
@register.filter
def get_player_for_match(user, match):
    """
    Returns the Player object for a given user and match.
    This is used to check if a player has won a match.
    """
    try:
        return Player.objects.get(user=user, match=match)
    except Player.DoesNotExist:
        return None
