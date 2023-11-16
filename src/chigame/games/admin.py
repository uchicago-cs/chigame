from django.contrib import admin

from .models import Game, Lobby, Match, MatchProposal, Player


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "min_players", "max_players")
    search_fields = ("name__startswith",)


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
