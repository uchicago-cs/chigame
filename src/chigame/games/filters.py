import django_filters

from .models import Lobby


class LobbyFilter(django_filters.FilterSet):
    lobby_name = django_filters.CharFilter(field_name="name", lookup_expr="contains", label="Lobby Name")
    game_name = django_filters.CharFilter(field_name="game_id__name", lookup_expr="contains", label="Game Name")
    max_players = django_filters.NumberFilter(
        field_name="max_players", lookup_expr="lt", label="Maximum Number of Players less than or equal to"
    )

    class Meta:
        model = Lobby
        fields = ["lobby_name", "game_name", "max_players"]
