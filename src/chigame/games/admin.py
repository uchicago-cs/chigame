from django.apps import apps
from django.contrib import admin

from .models import Game, Lobby, Match, MatchProposal, Player


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "min_players", "max_players", "complexity", "year_published")
    list_filter = ("categories", "mechanics", "min_players", "max_players")
    search_fields = (
        "name__icontains",
        "description__icontains",
        "people__name__icontains",
        "publishers__name__icontains",
        "categories__name__icontains",
        "mechanics__name__icontains",
    )
    ordering = ("name",)


# for future admin page customizations
@admin.register(Lobby)
class LobbyAdmin(admin.ModelAdmin):
    pass


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(MatchProposal)
class MatchProposalAdmin(admin.ModelAdmin):
    pass


# Tournaments

models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
