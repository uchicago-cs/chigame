"""
This file contains the functions needed for the tournaments feature.
"""

import random

from .models import Lobby, Match, Tournament


def create_tournaments_brackets(tournament: Tournament) -> list[Match]:
    """
    Creates a list of brackets for the tournaments.

    Args:
        tournament: the tournament

    Returns:
        a list of matches
    """
    players = [player for player in tournament.players.all()]  # the players in the tournament
    brackets = []
    random.shuffle(players)  # shuffle the players
    # Create a list of brackets (match assignment) for the tournament
    for i in range(0, len(players), tournament.game.max_players):
        game = tournament.game
        lobby = Lobby.objects.create(
            match_status=Lobby.Lobbied,
            game=game,
            game_mod_status=Lobby.Default_game,
            created_by=players[i],  # the field is currently set to the first player in the list
            min_players=game.min_players,
            max_players=game.max_players,
            # time_constraint, # default: 300
            # lobby_created, # default: the field is set to the current time
        )
        players_in_match = players[i : i + tournament.game.max_players]  # the players in the match
        match = Match.objects.create(game=game, lobby=lobby, date_played=tournament.start_date)
        # date_played is set to the start date of the tournament for now
        match.players.set(players_in_match)
        match.save()
        brackets.append(match)

        tournament.matches.add(match)  # add the match to the tournament

    return brackets


def next_round_tournaments_brackets(tournament: Tournament) -> list[Match]:
    """
    Creates a list of brackets for the next round of the tournaments.

    Args:
        tournament: the tournament

    Returns:
        a list of matches
    """
    brackets = tournament.matches.all()  # the matches of the previous round
    players = []

    # get the winners of the previous round
    for bracket in brackets:
        for winner in bracket.winners.all():  # .all() because allow multiple winners
            players.append(winner)

    # check if the number of players is small enough to end the tournament
    if len(players) < tournament.game.min_players:
        end_tournament(tournament)
        return []  # the tournament is finished

    # clear the matches of the previous round
    tournament.matches.clear()

    # create the matches of the next round
    random.shuffle(players)
    next_round_brackets = []
    # Create a list of brackets (match assignment) for the tournament
    for i in range(0, len(brackets), tournament.game.max_players):
        game = tournament.game
        lobby = Lobby.objects.create(
            match_status=Lobby.Lobbied,
            game=game,
            game_mod_status=Lobby.Default_game,
            created_by=brackets[i].winners.all()[0],  # the field is currently set to the first player in the list
            min_players=game.min_players,
            max_players=game.max_players,
            # time_constraint, # default: 300
            # lobby_created, # default: the field is set to the current time
        )
        players_in_match = players[i : i + tournament.game.max_players]  # the players in the match
        match = Match.objects.create(game=game, lobby=lobby, date_played=tournament.start_date)
        match.players.set(players_in_match)
        match.save()
        next_round_brackets.append(match)

        tournament.matches.add(match)  # add the match to the tournament

    return next_round_brackets


def end_tournament(tournament: Tournament) -> None:
    """
    Ends the tournament.

    Args:
        tournament: the tournament

    Returns:
        None
    """
    winners = []
    for match in tournament.matches.all():  # the matches of the previous round
        for winner in match.winners.all():  # .all() because allow multiple winners
            winners.append(winner)

    tournament.winners.set(winners)  # set the winners of the tournament
    tournament.save()  # save the tournament to the database

    # Note: we don't delete the tournament because we want to keep it in the database
