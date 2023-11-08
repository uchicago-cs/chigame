# from django.shortcuts import render
from rest_framework import generics

from chigame.api.serializers import GameSerializer, UserProfileSerializer
from chigame.games.models import Game
from chigame.users.models import UserProfile


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class UserProfileListView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserFriendsAPIView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        user_id = self.kwargs["user_id"]
        user_profile = UserProfile.objects.get(user_id=user_id)
        return user_profile.friends.all()

    # def get(self, request, *args, **kwargs):
    #     friends = self.get_object()
    #     serializer = UserProfileSerializer(friends, many=True)
    #     return Response(serializer.data)
