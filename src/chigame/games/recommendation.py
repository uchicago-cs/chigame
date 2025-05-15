"""
Tournament player recommendation service.

This module provides functionality to recommend players for tournaments based on:
- Friendship relationships
- Experience with the same game
- Experience with similar tournament formats
- Previous participation in tournaments created by the same owner
"""

from chigame.games.models import Player, Tournament
from chigame.users.models import User


class TournamentRecommendationService:
    """Service for recommending players for tournaments."""

    def __init__(self, tournament, max_recommendations=10):
        """
        Initialize the recommendation service.

        Args:
            tournament: The tournament to recommend players for
            max_recommendations: Maximum number of recommendations to return
        """
        self.tournament = tournament
        self.max_recommendations = max_recommendations
        self.game = tournament.game
        self.owner = tournament.created_by

    def get_recommendations(self):
        """
        Get recommended players for the tournament.

        Returns:
            List of (user, score, reasons) tuples sorted by score in descending order
        """
        # get all users who are not already in the tournament
        all_users = User.objects.exclude(id__in=self.tournament.players.values_list("id", flat=True))

        # calculate scores for each user
        recommendations = []
        for user in all_users:
            score, reasons = self._calculate_score(user)
            if score > 0:  # only include users with a positive score
                recommendations.append((user, score, reasons))

        # sort by score and limit to max_recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[: self.max_recommendations]

    def _calculate_score(self, user):
        """
        Calculate a recommendation score for a user.

        Args:
            user: The user to calculate a score for

        Returns:
            Tuple of (score, reasons) where reasons is a list of strings
        """
        score = 0
        reasons = []

        # check if user is a friend of the tournament owner
        friend_score = self._get_friendship_score(user)
        if friend_score > 0:
            score += friend_score
            reasons.append("Friend of tournament creator")

        # check if user has played the same game before
        game_experience_score = self._get_game_experience_score(user)
        if game_experience_score > 0:
            score += game_experience_score
            reasons.append(f"Has experience with {self.game.name}")

        # check if user has participated in tournaments with the same owner before
        owner_tournament_score = self._get_owner_tournament_score(user)
        if owner_tournament_score > 0:
            score += owner_tournament_score
            reasons.append("Participated in tournaments by the same creator")

        # check if user has participated in similar tournament formats
        format_score = self._get_tournament_format_score(user)
        if format_score > 0:
            score += format_score
            reasons.append("Has experience with similar tournament formats")

        return score, reasons

    def _get_friendship_score(self, user):
        """
        Calculate a score based on friendship with the tournament owner.

        Args:
            user: The user to calculate a score for

        Returns:
            int: Friendship score (0 if not friends, 10 if friends)
        """
        if not self.owner:
            return 0

        # Check if user is in the owner's friends (friends field is in User model, not UserProfile)
        if user in self.owner.friends.all():
            return 10

        return 0

    def _get_game_experience_score(self, user):
        """
        Calculate a score based on user's experience with the game.

        Args:
            user: The user to calculate a score for

        Returns:
            int: Game experience score (0-15 based on number of matches played)
        """
        # count matches played with this game
        match_count = Player.objects.filter(user=user, match__game=self.game).count()

        # score based on number of matches played (max 15 points)
        if match_count > 10:
            return 15
        elif match_count > 5:
            return 10
        elif match_count > 0:
            return 5
        return 0

    def _get_owner_tournament_score(self, user):
        """
        Calculate a score based on participation in tournaments created by the same owner.

        Args:
            user: The user to calculate a score for

        Returns:
            int: Owner tournament score (0-8 based on number of tournaments)
        """
        if not self.owner:
            return 0

        # count tournaments by the same owner that the user has participated in
        tournament_count = Tournament.objects.filter(created_by=self.owner, players=user).count()

        # score based on number of tournaments (max 8 points)
        if tournament_count > 3:
            return 8
        elif tournament_count > 1:
            return 5
        elif tournament_count > 0:
            return 3
        return 0

    def _get_tournament_format_score(self, user):
        """
        Calculate a score based on experience with similar tournament formats.

        Args:
            user: The user to calculate a score for

        Returns:
            int: Tournament format score (0-7 based on similar tournaments)
        """
        # for now, we're just counting participation in any tournaments
        # in a more advanced implementation, we could compare tournament formats
        tournament_count = Tournament.objects.filter(players=user).count()

        # score based on number of tournamnts
        if tournament_count > 5:
            return 7
        elif tournament_count > 2:
            return 4
        elif tournament_count > 0:
            return 2
        return 0


def get_tournament_recommendations(tournament, max_recommendations=10):
    """
    Get recommended players for a tournament.

    Args:
        tournament: The tournament to recommend players for
        max_recommendations: Maximum number of recommendations to return

    Returns:
        List of (user, score, reasons) tuples sorted by score in descending order
    """
    service = TournamentRecommendationService(tournament, max_recommendations)
    return service.get_recommendations()
