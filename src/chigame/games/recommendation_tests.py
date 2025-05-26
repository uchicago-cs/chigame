"""
Simple test script for the tournament recommendation service.
This is just to verify the general idea works correctly.
Uses the tournament simulation fixtures.
"""

from chigame.games.models import Game, Tournament
from chigame.games.recommendation import TournamentRecommendationService, get_tournament_recommendations
from chigame.users.models import User


def test_recommendation_service():
    """Test the recommendation service with tournament fixtures."""
    print("Testing Tournament Recommendation Service...")

    # Get the test game (ID 1 from fixtures)
    try:
        game = Game.objects.get(id=1)
        print(f"Using game: {game.name}")
    except Game.DoesNotExist:
        print("Test game not found. Please load the fixtures first.")
        return

    # Get the tournament from fixtures
    tournaments = Tournament.objects.filter(game=game)
    if not tournaments:
        print("No tournaments found for the test game. Please load the fixtures first.")
        return

    tournament = tournaments.first()
    print(f"Using tournament: {tournament.name}")
    print(f"Tournament owner: {tournament.created_by}")

    # Get test players (IDs 101-108 from fixtures)
    test_players = User.objects.filter(id__range=(101, 108))
    print(f"Found {test_players.count()} test players")

    # Create the recommendation service
    service = TournamentRecommendationService(tournament)

    # Test friendship score for some players
    print("\nTesting friendship scores:")
    for user in test_players[:3]:  # Just test a few players
        score = service._get_friendship_score(user)
        print(f"Friendship score for {user}: {score}")

    # Test game experience score
    print("\nTesting game experience scores:")
    for user in test_players[:3]:
        score = service._get_game_experience_score(user)
        print(f"Game experience score for {user}: {score}")

    # Test owner tournament score
    print("\nTesting owner tournament scores:")
    for user in test_players[:3]:
        score = service._get_owner_tournament_score(user)
        print(f"Owner tournament score for {user}: {score}")

    # Test tournament format score
    print("\nTesting tournament format scores:")
    for user in test_players[:3]:
        score = service._get_tournament_format_score(user)
        print(f"Tournament format score for {user}: {score}")

    # Test overall recommendations
    print("\nTesting overall recommendations:")
    recommendations = service.get_recommendations()
    print(f"Found {len(recommendations)} recommendations")

    for i, (user, score, reasons) in enumerate(recommendations[:5], 1):  # Show top 5
        print(f"\nRecommendation #{i}:")
        print(f"User: {user}")
        print(f"Score: {score}")
        print(f"Reasons: {', '.join(reasons)}")

    # Test the helper function
    print("\nTesting helper function:")
    helper_recommendations = get_tournament_recommendations(tournament, max_recommendations=3)
    print(f"Found {len(helper_recommendations)} recommendations using helper function")

    for i, (user, score, reasons) in enumerate(helper_recommendations, 1):
        print(f"\nRecommendation #{i}:")
        print(f"User: {user}")
        print(f"Score: {score}")
        print(f"Reasons: {', '.join(reasons)}")


# Run the test
test_recommendation_service()
