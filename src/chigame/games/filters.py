import django_filters
from .models import Lobby

class LobbyFilter(django_filters.FilterSet):
    game_name = django_filters.CharFilter(field_name='game_id__name', lookup_expr='contains', label='Game Name')

    class Meta:
        model = Lobby
        fields = ['game_name']
