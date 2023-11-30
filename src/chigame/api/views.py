# from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from chigame.api.filters import GameFilter
from chigame.api.serializers import GameSerializer, LobbySerializer, MessageSerializer, UserSerializer
from chigame.games.models import Game, Lobby, Message, User
from chigame.users.models import UserProfile


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class UserFriendsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        user_profile = UserProfile.objects.get(user=user_id)
        return user_profile.friends.all()


class LobbyListView(generics.ListCreateAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer


class LobbyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


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
            serializer = MessageSerializer(messages, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
