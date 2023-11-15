import django_filters
from .models import Lobby

class LobbyFilter(django_filters.FilterSet):
    class Meta:
        model = Lobby
        fields = {
            'game' : ['icontains'],
        }

