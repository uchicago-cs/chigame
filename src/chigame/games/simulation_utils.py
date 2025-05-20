"""
Utility functions for simulating tournament progression.

This module provides functionality to simulate tournament progression for both
single and double elimination formats without modifying the existing Tournament model.
The simulation is for visualization purposes only and does not affect the actual
tournament data in the DB.
"""

import random

from django.contrib.auth import get_user_model

from .models import Match, Tournament

User = get_user_model()


class TournamentSimulator:
    """
    A class to simulate tournament progression for both single and double elimination formats.
    """

    def __init__(self, tournament: Tournament):
        """
        Initialize the tournament simulator with a tournament instance.

        Args:
            tournament: The tournament to simulate
        """
        self.tournament = tournament
        self.simulated_matches = {}
        self.simulated_winners = {}
        self.simulated_losers = {}
        self.simulated_next_round = {}
        self.simulated_final_match = None
        self.current_round = 0
        self.is_double_elimination = False  # single elimination by default

    def set_tournament_type(self, is_double_elimination: bool) -> None:
        """
        Set the tournament type.

        Args:
            is_double_elimination: Whether the tournament is double elimination
        """
        self.is_double_elimination = is_double_elimination

    def initialize_simulation(self) -> None:
        """
        Initialize the simulation by setting up the first round matches.
        """
        self.current_round = 1
        self.simulated_matches = {}
        self.simulated_winners = {}
        self.simulated_losers = {}
        self.simulated_next_round = {}
        self.simulated_final_match = None

        # get all matches from the tournament
        matches = self.tournament.matches.all()

        # store initial matches
        for match in matches:
            # Convert match ID to string for consistent key handling
            match_id_str = str(match.id)
            self.simulated_matches[match_id_str] = {
                "match": match,
                "players": list(match.players.all()),
                "winner": None,
                "loser": None,
                "round": 1,
                "bracket": "winners",  # all initial matches are in winners bracket
            }

    def simulate_match_outcome(self, match_id: int) -> tuple[User | None, User | None]:
        """
        Simulate the outcome of a match by randomly selecting a winner.

        Args:
            match_id: The ID of the match to simulate

        Returns:
            A tuple containing the winner and loser User objects
        """
        # Convert match_id to string if it's not already
        match_id_str = str(match_id)

        # Check if the match exists in either string or integer form
        if match_id_str in self.simulated_matches:
            match_data = self.simulated_matches[match_id_str]
        elif match_id in self.simulated_matches:
            match_data = self.simulated_matches[match_id]
        else:
            print(f"Match ID {match_id} not found in simulated matches")
            return None, None

        players = match_data["players"]

        if len(players) < 2:
            print(f"Not enough players in match {match_id}: {players}")
            return None, None

        # randomly select a winner
        winner_index = random.randint(0, len(players) - 1)
        winner = players[winner_index]

        loser = players[1 - winner_index] if len(players) == 2 else None

        # Update the match data with the winner and loser
        match_data["winner"] = winner
        match_data["loser"] = loser

        return winner, loser

    def create_next_round_matches(self) -> dict:
        """
        Create matches for the next round based on the winners of the current round.

        Returns:
            A dictionary of new matches for the next round
        """
        next_round = self.current_round + 1
        winners_bracket_matches = {}
        losers_bracket_matches = {}

        # get all matches from the current round
        current_matches = {
            m_id: m
            for m_id, m in self.simulated_matches.items()
            if m["round"] == self.current_round and m["bracket"] == "winners"
        }

        # pair winners for the next round
        winners = [m["winner"] for m in current_matches.values() if m["winner"]]

        # if there's only one winner, we have found our winner!!
        if len(winners) <= 1:
            return {}

        # create matches for the next round in the winners bracket
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                match_id = f"sim_w_{next_round}_{i // 2}"
                winners_bracket_matches[match_id] = {
                    "match": None,
                    "players": [winners[i], winners[i + 1]],
                    "winner": None,
                    "loser": None,
                    "round": next_round,
                    "bracket": "winners",
                }

        # if this is a double elimination tournament, create matches in the losers bracket
        if self.is_double_elimination:
            current_losers = [m["loser"] for m in current_matches.values() if m["loser"]]

            previous_losers_matches = {
                m_id: m
                for m_id, m in self.simulated_matches.items()
                if m["round"] < self.current_round and m["bracket"] == "losers"
            }
            previous_losers_winners = [m["winner"] for m in previous_losers_matches.values() if m["winner"]]

            losers_bracket_players = current_losers + previous_losers_winners

            # create matches for the next round in the losers bracket
            for i in range(0, len(losers_bracket_players), 2):
                if i + 1 < len(losers_bracket_players):
                    match_id = f"sim_l_{next_round}_{i // 2}"
                    losers_bracket_matches[match_id] = {
                        "match": None,
                        "players": [losers_bracket_players[i], losers_bracket_players[i + 1]],
                        "winner": None,
                        "loser": None,
                        "round": next_round,
                        "bracket": "losers",
                    }

        next_round_matches = {**winners_bracket_matches, **losers_bracket_matches}

        self.simulated_next_round = next_round_matches
        self.current_round = next_round

        self.simulated_matches.update(next_round_matches)

        return next_round_matches

    def create_final_match(self) -> dict:
        """
        Create the final match for a double elimination tournament between the winners
        bracket champion and the losers bracket champion.

        Returns:
            A dictionary containing the final match data
        """
        if not self.is_double_elimination:
            return None

        # get the winners bracket champion
        winners_bracket_matches = {m_id: m for m_id, m in self.simulated_matches.items() if m["bracket"] == "winners"}
        winners_bracket_champion = None

        for match in sorted(winners_bracket_matches.values(), key=lambda m: m["round"], reverse=True):
            if match["winner"]:
                winners_bracket_champion = match["winner"]
                break

        # get the losers bracket champion
        losers_bracket_matches = {m_id: m for m_id, m in self.simulated_matches.items() if m["bracket"] == "losers"}
        losers_bracket_champion = None

        for match in sorted(losers_bracket_matches.values(), key=lambda m: m["round"], reverse=True):
            if match["winner"]:
                losers_bracket_champion = match["winner"]
                break

        if not winners_bracket_champion or not losers_bracket_champion:
            return None

        # create the final match
        final_round = self.current_round + 1
        final_match_id = f"sim_final_{final_round}"

        final_match = {
            "match": None,
            "players": [winners_bracket_champion, losers_bracket_champion],
            "winner": None,
            "loser": None,
            "round": final_round,
            "bracket": "final",
        }

        self.simulated_final_match = final_match
        self.simulated_matches[final_match_id] = final_match

        return final_match

    def get_tournament_winner(self) -> User | None:
        """
        Get the winner of the tournament based on the simulation.

        Returns:
            The User object of the tournament winner, or None if the tournament is not complete
        """
        if self.is_double_elimination and self.simulated_final_match:
            return self.simulated_final_match["winner"]

        # for single elimination, get the winner of the last round
        last_round = max([m["round"] for m in self.simulated_matches.values()])
        last_round_matches = [m for m in self.simulated_matches.values() if m["round"] == last_round]

        if len(last_round_matches) == 1 and last_round_matches[0]["winner"]:
            return last_round_matches[0]["winner"]

        return None

    def get_bracket_data(self) -> dict:
        """
        Get the data needed to render the tournament bracket.

        Returns:
            A dictionary containing the bracket data
        """
        rounds = {}

        for match_id, match_data in self.simulated_matches.items():
            round_num = match_data["round"]
            bracket = match_data["bracket"]

            if round_num not in rounds:
                rounds[round_num] = {"winners": [], "losers": [], "final": []}

            rounds[round_num][bracket].append(
                {
                    "id": match_id,
                    "players": [{"id": p.id, "name": p.username} for p in match_data["players"]],
                    "winner": match_data["winner"].id if match_data["winner"] else None,
                    "loser": match_data["loser"].id if match_data["loser"] else None,
                }
            )

        return {
            "rounds": rounds,
            "current_round": self.current_round,
            "is_double_elimination": self.is_double_elimination,
            "tournament_winner": self.get_tournament_winner().id if self.get_tournament_winner() else None,
        }


def simulate_single_match(match_id: int) -> tuple[User | None, User | None]:
    """
    Simulate the outcome of a single match by randomly selecting a winner.

    Args:
        match_id: The ID of the match to simulate

    Returns:
        A tuple containing the winner and loser User objects
    """
    try:
        match = Match.objects.get(id=match_id)
        players = list(match.players.all())

        if len(players) < 2:
            return None, None

        # randomly select a winner
        winner_index = random.randint(0, len(players) - 1)
        winner = players[winner_index]

        loser = players[1 - winner_index] if len(players) == 2 else None

        return winner, loser
    except Match.DoesNotExist:
        return None, None


def run_complete_tournament_simulation(tournament: Tournament, is_double_elimination: bool = False) -> dict:
    """
    Run a complete simulation of a tournament from start to finish.

    Args:
        tournament: The tournament to simulate
        is_double_elimination: Whether the tournament is double elimination

    Returns:
        A dictionary containing the final bracket data
    """
    simulator = TournamentSimulator(tournament)
    simulator.set_tournament_type(is_double_elimination)
    simulator.initialize_simulation()

    # simulate all matches in the first round
    for match_id in simulator.simulated_matches:
        simulator.simulate_match_outcome(match_id)

    # create and simulate subsequent rounds until we have a winner
    while True:
        next_round_matches = simulator.create_next_round_matches()

        if not next_round_matches:
            break

        for match_id in next_round_matches:
            simulator.simulate_match_outcome(match_id)

    # for double elimination, create and simulate the final match
    if is_double_elimination:
        final_match = simulator.create_final_match()
        if final_match:
            simulator.simulate_match_outcome(
                list(final_match.keys())[0] if isinstance(final_match, dict) else "sim_final"
            )

    return simulator.get_bracket_data()


class RoundRobinSimulator:
    """
    A simple simulator for Round Robin tournaments where each player plays every other player exactly once.
    No concept of rounds; all matches are generated up front.
    """

    def __init__(self, players: list[User]):
        """
        Initialize the round robin simulator.

        Args:
            players: List of User instances participating in the tournament
        """
        self.players = players
        self.matches = []  # List of tuples (player1, player2)
        self.results = {}  # Key: (player1.id, player2.id), Value: winner.id
        self.generate_matches()

    def generate_matches(self) -> None:
        """
        Generate all match pairings for the round robin (every player vs every other player).
        """
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                self.matches.append((self.players[i], self.players[j]))

    def simulate_all_matches(self) -> None:
        """
        Simulate the result of all matches by randomly picking a winner.
        """
        for player1, player2 in self.matches:
            winner = random.choice([player1, player2])
            self.results[(player1.id, player2.id)] = winner.id

    def get_standings(self) -> dict:
        """
        Get the number of wins for each player.

        Returns:
            A dictionary mapping player.id to number of wins
        """
        standings = {player.id: 0 for player in self.players}

        for (p1_id, p2_id), winner_id in self.results.items():
            standings[winner_id] += 1

        return standings

    def get_sorted_standings(self) -> list[tuple[User, int]]:
        """
        Get the standings sorted by number of wins descending.

        Returns:
            A list of tuples (User instance, wins)
        """
        standings = self.get_standings()
        player_map = {player.id: player for player in self.players}

        sorted_standings = sorted(
            [(player_map[player_id], wins) for player_id, wins in standings.items()], key=lambda x: -x[1]
        )
        return sorted_standings

    def get_match_data(self) -> list[dict]:
        """
        Build a list of match dictionaries with match id, players, and winner.
        """
        match_data = []
        for idx, (player1, player2) in enumerate(self.matches):
            match_info = {
                "id": idx,
                "players": [
                    {"id": player1.id},
                    {"id": player2.id},
                ],
                "winner": self.results.get((player1.id, player2.id)),
            }
            match_data.append(match_info)
        return match_data

    def get_bracket_data(self) -> dict:
        """
        Returns the simulation data formatted for the frontend template.
        """
        return {
            "matches": self.get_match_data(),
            "tournament_winner": (self.get_sorted_standings()[0][0].id if self.results else None),
        }


class MultiStageSimulator(RoundRobinSimulator):
    """
    A multi-stage simulator where we first run a round robin stage and then
    proceed to a single elimination bracket for the top players.
    """

    def __init__(self, players: list[User], num_qualifiers: int = 4):
        super().__init__(players)
        self.num_qualifiers = num_qualifiers
        self.final_matches = []  # Bracket matches for final stage
        self.final_results = {}
        self.round_robin_simulated = False

    def simulate_round_robin_only(self) -> None:
        """
        Simulate only the round robin stage.
        """
        self.simulate_all_matches()
        self.round_robin_simulated = True

    def simulate_knockout_only(self) -> None:
        """
        Simulate only the knockout stage based on round robin standings.
        Assumes round robin matches have been simulated already.
        """
        if not self.round_robin_simulated:
            raise ValueError("Round robin phase must be completed before knockout phase.")

        # Get top qualifiers from round robin
        sorted_standings = self.get_sorted_standings()
        qualifiers = [player for player, _ in sorted_standings[: self.num_qualifiers]]

        self.reset_final_stage()

        # Now simulate knockout
        while len(qualifiers) > 1:
            next_round = []
            for i in range(0, len(qualifiers), 2):
                if i + 1 < len(qualifiers):
                    p1 = qualifiers[i]
                    p2 = qualifiers[i + 1]
                    winner = random.choice([p1, p2])
                    self.final_matches.append((p1, p2))
                    self.final_results[(p1.id, p2.id)] = winner.id
                    next_round.append(winner)
            qualifiers = next_round

    def simulate_tournament(self) -> None:
        """
        Full simulation: round robin + knockout.
        """
        self.simulate_round_robin_only()
        self.simulate_knockout_only()

    def reset_final_stage(self) -> None:
        """
        Reset the knockout phase data (for re-running).
        """
        self.final_matches = []
        self.final_results = {}

    def get_tournament_winner(self) -> User | None:
        """
        Get the winner of the tournament.
        """
        if not self.final_results:
            return None

        last_match = list(self.final_results.keys())[-1]
        winner_id = self.final_results[last_match]
        player_map = {player.id: player for player in self.players}

        return player_map.get(winner_id)

    def get_round_robin_match_data(self) -> list[dict]:
        """
        Format round robin match data.
        """
        match_data = []
        for idx, (player1, player2) in enumerate(self.matches):
            match_info = {
                "id": idx,
                "players": [
                    {"id": player1.id},
                    {"id": player2.id},
                ],
                "winner": self.results.get((player1.id, player2.id)),
            }
            match_data.append(match_info)
        return match_data

    def get_knockout_rounds(self) -> dict:
        rounds = {}
        current_round = 1
        matches_in_round = []
        last_match_idx = 0

        winners = []
        players_seen = set()

        for (p1_id, p2_id), winner_id in self.final_results.items():
            matches_in_round.append(
                {
                    "id": last_match_idx,
                    "players": [{"id": p1_id}, {"id": p2_id}],
                    "winner": winner_id,
                }
            )
            last_match_idx += 1
            winners.append(winner_id)

            players_seen.update([p1_id, p2_id])
            if len(players_seen) >= (2 ** (current_round)):
                rounds[current_round] = matches_in_round
                matches_in_round = []
                players_seen = set(winners)
                winners = []
                current_round += 1
        if matches_in_round:
            rounds[current_round] = matches_in_round

        return rounds

    def get_bracket_data(self) -> dict:
        """
        Return all data needed for frontend.
        """
        return {
            "round_robin_matches": self.get_round_robin_match_data(),
            "round_robin_complete": self.round_robin_simulated,
            "knockout_rounds": self.get_knockout_rounds(),
            "tournament_winner": (self.get_tournament_winner().id if self.get_tournament_winner() else None),
        }
