# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from chigame.achievements.models import Achievement, UserAchievement
from chigame.api.filters import GameFilter
from chigame.api.serializers import (
    AchievementSerializer,
    CategorySerializer,
    FeedbackSerializer,
    GameSerializer,
    GroupSerializer,
    LobbySerializer,
    MechanicSerializer,
    MessageFeedSerializer,
    MessageSerializer,
    ReviewSerializer,
    UserAchievementSerializer,
    UserSerializer,
)
from chigame.api.spam_utils import is_spam
from chigame.games.models import Feedback, Game, Lobby, Message, Review, Tournament
from chigame.users.models import Group, User


# Helper function to get user from slug
def get_user(lookup_value):
    # If the lookup_value is an integer, use the id field
    if lookup_value.isdigit():
        return get_object_or_404(User, pk=lookup_value)
    else:
        # Otherwise, use the slug field
        return get_object_or_404(User, username=lookup_value)


class GameListView(generics.ListCreateAPIView):
    """
    API endpoint that returns a paginated list of games.

    Pagination:
    - Page size: 10
    - Uses DRF's PageNumberPagination
    """

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameCategoriesAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        game_id = self.kwargs["pk"]
        game = Game.objects.get(id=game_id)
        return game.categories.all()


class GameMechanicsAPIView(generics.ListAPIView):
    serializer_class = MechanicSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        game_id = self.kwargs["pk"]
        game = Game.objects.get(id=game_id)
        return game.mechanics.all()


class UserFriendsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        user = get_object_or_404(User, id=user_id)
        return user.friends.all()


class LobbyListView(generics.ListCreateAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer
    pagination_class = PageNumberPagination

    permission_classes = [IsAuthenticatedOrReadOnly]  # similar to GameListView

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class LobbyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer

    def perform_destroy(self, instance):
        if self.request.user != instance.created_by and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this lobby.")
        instance.delete()

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.created_by and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to update this lobby.")
        serializer.save()


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


# Bug with PATCH'ing emails -- refer to Issue #394
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "slug"

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        return get_user(lookup_value)


# Custom permission class for authentification
class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return request.user and request.user.is_authenticated


class MessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        content = serializer.validated_data.get("content", "")
        if is_spam(content):
            raise ValidationError("Your message appears to be spam.")

        # serializer.save()
        serializer.save(sender=self.request.user)

    # Need Livechat in order to use this endpoint


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsGroupAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        group = view.get_object()
        return request.user == group.created_by or group.members.filter(id=request.user.id).exists()


class GroupListView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        group.members.add(self.request.user)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsGroupAdminOrReadOnly]

    def perform_update(self, request, *args, **kwargs):
        group = self.get_object()
        if not group.group_admin_permissions and request.user != group.created_by:
            raise PermissionDenied("You do not have permission to update this group.")
        return super().perform_update(request, *args, **kwargs)

    def perform_destroy(self, request, *args, **kwargs):
        group = self.get_object()
        if group.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to delete this group.")
        return super().perform_destroy(request, *args, **kwargs)


class GroupMembersView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        group_id = self.kwargs["pk"]
        group = Group.objects.get(pk=group_id)
        return group.members.all()


class UserGroupsView(generics.ListAPIView):
    serializer_class = GroupSerializer
    lookup_field = "slug"

    def get_queryset(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        user_id = get_user(lookup_value).id
        groups = Group.objects.filter(members__pk=user_id)
        return groups


class GroupJoinView(LoginRequiredMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user = request.user

        if not group.members.filter(id=user.id).exists():
            group.members.add(user)
        return redirect("api-group-detail", pk=group_id)


class GroupLeaveView(LoginRequiredMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user = request.user

        if group.members.filter(id=user.id).exists():
            group.members.remove(user)
        return redirect("api-group-detail", pk=group_id)


class MessageFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get data from the frontend
        token_id = request.data.get("token_id")
        tournament_id = request.data.get("tournament")

        try:
            # Retrieve messages with a token_id greater than the one sent from the frontend
            messages = Message.objects.filter(chat__tournament_id=tournament_id, token_id__gt=token_id).order_by(
                "token_id"
            )

            # Serialize the messages
            serializer = MessageFeedSerializer(messages, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GameReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        game_id = self.kwargs["pk"]
        return Review.objects.filter(game__id=game_id)


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.none()

    def perform_create(self, serializer):
        review_text = serializer.validated_data.get("review", "")
        if is_spam(review_text):
            raise ValidationError("Your review appears to be spam. Please revise your content.")

        # user_id = self.request.data.get("user")
        game_id = self.kwargs["pk"]
        game = get_object_or_404(Game, pk=game_id)
        # user = get_object_or_404(User, pk=user_id)
        # serializer.save(user=user, game_id=game_id)
        serializer.save(user=self.request.user, game=game)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    queryset = Review.objects.none()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this review.")
        instance.delete()

    def perform_update(self, serializer):
        user_id = self.request.data.get("user")
        user = get_object_or_404(User, pk=user_id)

        if user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this review.")
        serializer.save()


class AchievementListView(generics.ListAPIView):
    serializer_class = AchievementSerializer

    def get_queryset(self):
        game_id = self.kwargs["pk"]
        return Achievement.objects.filter(game__id=game_id)


class UserAchievementCreateView(generics.CreateAPIView):
    serializer_class = UserAchievementSerializer

    def perform_create(self, serializer):
        achievement_id = self.kwargs["pk"]
        serializer.save(achievement_id=achievement_id)

    def create(self, request, *args, **kwargs):
        user_id = self.request.data.get("user")
        user = get_object_or_404(User, pk=user_id)
        achievement = Achievement.objects.get(id=self.kwargs["pk"])

        if UserAchievement.objects.filter(achievement=achievement, user=user).exists():
            return Response(
                {"error": f"This achievement already exists for user '{user.email}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response(
            {"message": "Achievement created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED
        )


class AchievementCreateView(generics.CreateAPIView):
    serializer_class = AchievementSerializer

    def perform_create(self, serializer):
        game_id = self.kwargs["pk"]
        serializer.save(game_id=game_id)

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        game = Game.objects.get(id=self.kwargs["pk"])

        if Achievement.objects.filter(name=name, game=game).exists():
            return Response(
                {"error": f"An achievement with the name '{name}' already exists for this game."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response(
            {"message": "Achievement assigned to user!", "data": serializer.data}, status=status.HTTP_201_CREATED
        )


class FeedbackListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = []

    def get_queryset(self):
        tournament_id = self.kwargs["pk"]
        return Feedback.objects.filter(tournament__id=tournament_id)

    def perform_create(self, serializer):
        tournament_id = self.kwargs["pk"]
        tournament = get_object_or_404(Tournament, id=tournament_id)
        user = User.objects.first()
        serializer.save(user=user, tournament=tournament)


class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = []

    def get_queryset(self):
        return Feedback.objects.all()

    def perform_update(self, serializer):
        feedback = self.get_object()
        user = User.objects.first()
        if feedback.user != user:
            raise PermissionDenied("You can only update your own feedback.")
        serializer.save()

    def perform_destroy(self, instance):
        user = User.objects.first()
        if instance.user != user:
            raise PermissionDenied("You can only delete your own feedback.")
        instance.delete()
