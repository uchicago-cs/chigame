"""
Simple test script for the tournament recommendation system.

Run with: python manage.py shell < src/chigame/games/test_recommendations.py
"""

from chigame.games.models import Game, Tournament
from chigame.games.recommendation import TournamentRecommendationService
from chigame.users.models import User

# Get the test game (ID 1)
try:
    game = Game.objects.get(id=1)
    print(f"Using game: {game.name}")
except Game.DoesNotExist:
    print("Test game not found. Please load the game fixtures first.")
    exit()

# Get the active tournament for recommendation testing
try:
    tournament = Tournament.objects.get(id=2004)
    print(f"Tournament: {tournament.name}")
    print(f"Creator: {tournament.created_by}")
    print(f"Current players: {', '.join([str(user) for user in tournament.players.all()])}")
except Tournament.DoesNotExist:
    print("Active tournament not found. Please load the recommendation fixtures first.")
    exit()

# Get recommendation test users
test_users = User.objects.filter(id__range=(201, 210))
print(f"Found {test_users.count()} recommendation test users")

# Create the recommendation service
service = TournamentRecommendationService(tournament)

print("\n=== RECOMMENDATIONS ===")
recommendations = service.get_recommendations()
print(f"Found {len(recommendations)} recommendations")

for i, (user, score, reasons) in enumerate(recommendations, 1):
    print(f"\n#{i}: {user} (ID: {user.id}) - Score: {score}")
    print(f"Reasons: {', '.join(reasons)}")

    # Show breakdown of scores
    friendship = service._get_friendship_score(user)
    game_exp = service._get_game_experience_score(user)
    owner_exp = service._get_owner_tournament_score(user)
    format_exp = service._get_tournament_format_score(user)

    print(f"Breakdown: Friend({friendship}) + Game({game_exp}) + Owner({owner_exp}) + Format({format_exp})")
