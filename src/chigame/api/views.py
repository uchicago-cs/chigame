# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from chigame.api.filters import GameFilter
from chigame.api.serializers import (
    CategorySerializer,
    GameSerializer,
    GroupSerializer,
    LobbySerializer,
    MechanicSerializer,
    MessageFeedSerializer,
    MessageSerializer,
    UserSerializer,
)
from chigame.games.models import Game, Lobby, Message, User
from chigame.users.models import Group, UserProfile


# Helper function to get user from slug
def get_user(lookup_value):
    # If the lookup_value is an integer, use the id field
    if lookup_value.isdigit():
        return get_object_or_404(User, pk=lookup_value)
    else:
        # Otherwise, use the slug field
        return get_object_or_404(User, username=lookup_value)


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view
    pagination_class = PageNumberPagination


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
        user_profile = get_object_or_404(UserProfile, user=user_id)
        return user_profile.friends.all()


class LobbyListView(generics.ListCreateAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer
    pagination_class = PageNumberPagination


class LobbyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer


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


class MessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class GroupListView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNumberPagination


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


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


class MessageFeedView(APIView):
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
