# from django.shortcuts import render

from dj_rest_auth.models import TokenModel
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from chigame.api.serializers import GameSerializer, LobbySerializer, TournamentSerializer, UserSerializer
from chigame.games.models import Game, Lobby, Tournament
from chigame.users.models import User, UserProfile

from django_filters.rest_framework import DjangoFilterBackend

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



class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class UserRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer_class = UserSerializer(data=request.data)
        if serializer_class.is_valid():
            user = serializer_class.save()
            UserProfile.objects.create(user=user, display_name=user.name)
            refresh = TokenModel.objects.create(user=user)
            access_token = str(refresh.key)

            return Response({"access_token": access_token}, status=status.HTTP_201_CREATED)
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class TournamentCreateView(generics.CreateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAdminUser]


class TournamentListView(generics.ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

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


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer



class CustomTokenObtainPairView(TokenObtainPairView):
    # Add any custom behavior if needed
    pass


class CustomTokenRefreshView(TokenRefreshView):
    # Add any custom behavior if needed
    pass


class CustomTokenVerifyView(TokenVerifyView):
    # Add any custom behavior if needed
    pass

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

