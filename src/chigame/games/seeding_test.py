import json

from django.contrib.auth import get_user_model

from chigame.games.models import Tournament
from chigame.games.simulation_utils import TournamentSimulator, compute_seeds, get_ordered_players_by_seeds


def test_compute_seeds():
    User = get_user_model()

    with open("src/chigame/games/fixtures/seeding_tournaments_fixtures.json") as f:
        fixture = json.load(f)

    results = compute_seeds(fixture)

    player_ids = [pid for pid, *_ in results]
    user_map = {u.id: u for u in User.objects.filter(id__in=player_ids)}

    print("Seed | Player Name     | Wins | Losses | Win Ratio")
    for seed, (pid, win, loss, ratio) in enumerate(results, start=1):
        name = user_map.get(pid).username if pid in user_map else f"(ID {pid})"
        print(f"{seed:>4} | {name:<15} | {win:^4} | {loss:^6} | {ratio:.3f}")


def test_bracket_generation_single_elim():
    User = get_user_model()

    # --- Load tournament fixture JSON (not from DB) ---
    with open("src/chigame/games/fixtures/seeding_tournaments_fixtures.json") as f:
        tournaments_data = json.load(f)

    # --- Compute seeds based on win/loss ratio ---
    seed_data = compute_seeds(tournaments_data)

    # --- Map player IDs to User objects already in DB ---
    user_ids = [player_id for player_id, _, _, _ in seed_data]
    user_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    # --- Convert seed data to ordered list of User instances ---
    seeded_players = get_ordered_players_by_seeds(seed_data, user_map)

    # --- Load a test tournament from the DB (any one will do) ---
    tournament = Tournament.objects.first()

    # --- Run seeded bracket simulation ---
    simulator = TournamentSimulator(tournament)
    simulator.set_tournament_type(is_double_elimination=False)
    simulator.set_seeded_players(seeded_players)
    simulator.initialize_simulation()

    # --- Print the generated matchups ---
    print("\nSeeded Bracket Matches for single elim:")
    for match_id, match in simulator.simulated_matches.items():
        player_names = [p.username for p in match["players"]]
        print(f"{match_id}: {player_names}")


test_compute_seeds()
test_bracket_generation_single_elim()
