import django_filters

from chigame.games.models import Game


class GameFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    min_players = django_filters.NumberFilter(lookup_expr="exact")
    max_players = django_filters.NumberFilter(lookup_expr="exact")

    class Meta:
        model = Game
        fields = ["name", "min_players", "max_players"]
