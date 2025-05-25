import json
from collections import defaultdict

from django.contrib.auth import get_user_model

from chigame.games.simulation_utils import RoundRobinSimulator


def test_round_robin_seeds():
    User = get_user_model()

    # Load tournament fixture
    with open("src/chigame/games/fixtures/spacebeans_tournament_history_fixture.json") as f:
        fixture = json.load(f)

    # Extract all players from tournament objects
    tournament_objs = [obj for obj in fixture if obj["model"] == "games.tournament"]

    player_ids = {pid for t in tournament_objs for pid in t["fields"].get("players", [])}
    players = list(User.objects.filter(id__in=player_ids))

    # Instantiate simulator
    simulator = RoundRobinSimulator(players=players, fixture=fixture, tiebreaker_mode="seed")

    player_map = {p.id: p for p in players}

    # Recompute win/loss counts for display
    wins = defaultdict(int)
    losses = defaultdict(int)

    for tournament in tournament_objs:
        fields = tournament["fields"]
        t_players = fields.get("players", [])
        t_winners = set(fields.get("winners", []))

        for pid in t_players:
            if pid in player_map:
                if pid in t_winners:
                    wins[pid] += 1
                else:
                    losses[pid] += 1

    print("\nSeed | Player ID | Wins | Losses")
    print("----------------------------------")
    for pid, seed in sorted(simulator.seeds.items(), key=lambda x: x[1]):
        win = wins[pid]
        loss = losses[pid]
        print(f"{seed:>4} | {pid:>9} | {win:^4} | {loss:^6}")


def test_round_robin_simulation_with_seeds():
    User = get_user_model()

    # Load tournament fixture
    with open("src/chigame/games/fixtures/spacebeans_tournament_history_fixture.json") as f:
        fixture = json.load(f)

    # Get all players involved in tournaments
    tournament_objs = [obj for obj in fixture if obj["model"] == "games.tournament"]
    player_ids = {pid for t in tournament_objs for pid in t["fields"].get("players", [])}
    players = list(User.objects.filter(id__in=player_ids))

    # Create and simulate tournament
    simulator = RoundRobinSimulator(players=players, fixture=fixture, tiebreaker_mode="seed")
    simulator.simulate_all_matches()

    # Get win/loss stats
    standings = simulator.get_standings()
    seeds = simulator.seeds

    # Build stats list
    stats = []
    for player in players:
        pid = player.id
        win = standings.get(pid, 0)
        total_matches = len(players) - 1
        loss = total_matches - win
        stats.append((player, win, loss, seeds.get(pid, float("inf"))))

    # Sort by win count desc, then seed asc
    stats.sort(key=lambda x: (-x[1], x[3]))

    print("\nFinal Standings (after Round Robin Simulation):")
    print("Seed | Player ID | Wins | Losses")
    print("----------------------------------")
    for player, win, loss, seed in stats:
        print(f"{seed:>4} | {player.id:>9} | {win:^4} | {loss:^6}")

    # Determine winner(s)
    top_score = stats[0][1]
    top_players = [s for s in stats if s[1] == top_score]

    print("\nWinner Determination:")
    if len(top_players) == 1:
        print(f"Winner: Player {top_players[0][0].id} (Seed {top_players[0][3]})")
    else:
        top_players.sort(key=lambda x: x[3])  # break tie by seed
        winner = top_players[0]
        tied_ids = ", ".join(f"Player {p[0].id}" for p in top_players)
        print(f"Tie between: {tied_ids}")
        print(f"Winner by seed: Player {winner[0].id} (Seed {winner[3]})")


# Run both tests
test_round_robin_seeds()
test_round_robin_simulation_with_seeds()
