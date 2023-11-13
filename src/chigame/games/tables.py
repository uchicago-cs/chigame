import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from .models import Lobby


class LobbyTable(tables.Table):
    match_status = tables.Column(verbose_name="Match Status")
    game_mod_status = tables.Column(verbose_name="Game Modifications")
    created_by = tables.Column(verbose_name="Created By")
    lobby_created = tables.Column(verbose_name="Creation Time")

    def render_name(self, value, record):
        url = reverse("lobby-details", args=[record.pk])
        return format_html('<a href="{}">{}</a>', url, value)

    class Meta:
        model = Lobby
        template_name = "django_tables2/bootstrap.html"
        fields = ("name", "game", "match_status", "game_mod_status", "created_by")
