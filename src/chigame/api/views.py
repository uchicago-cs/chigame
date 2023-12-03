# from django.shortcuts import render

from dj_rest_auth.models import TokenModel
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from chigame.api.filters import GameFilter
from chigame.api.serializers import (
    FriendInvitationSerializer,
    GameSerializer,
    LobbySerializer,
    MessageSerializer,
    TournamentSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from chigame.games.models import Game, Lobby, Message, Tournament
from chigame.users.models import FriendInvitation, User, UserProfile


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view
    pagination_class = PageNumberPagination


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

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
    pagination_class = PageNumberPagination


class LobbyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class CustomTokenObtainPairView(TokenObtainPairView):
    # Add any custom behavior if needed
    pass


class CustomTokenRefreshView(TokenRefreshView):
    # Add any custom behavior if needed
    pass


class CustomTokenVerifyView(TokenVerifyView):
    # Add any custom behavior if needed
    pass


class MessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class SendFriendInvitationView(APIView):
    def post(self, request, *args, **kwargs):
        sender_pk = self.kwargs["sender_pk"]
        receiver_pk = self.kwargs["receiver_pk"]

        sender = get_object_or_404(User, pk=sender_pk)
        receiver = get_object_or_404(User, pk=receiver_pk)

        if sender == receiver:
            return Response(
                {"detail": "You cannot send an invitation to yourself."}, status=status.HTTP_400_BAD_REQUEST
            )

        invitation = FriendInvitation(sender=sender, receiver=receiver)
        invitation.save()

        serializer = FriendInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptFriendInvitationView(APIView):
    def post(self, request, *args, **kwargs):
        invitation_pk = self.kwargs["invitation_pk"]
        invitation = get_object_or_404(FriendInvitation, pk=invitation_pk)

        if invitation.accepted:
            return Response(
                {"detail": "This invitation has already been accepted."}, status=status.HTTP_400_BAD_REQUEST
            )
        invitation.accept_invitation()  # Error with this method in the users.models
        serializer = FriendInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendInvitationList(generics.ListAPIView):
    queryset = FriendInvitation.objects.all()
    serializer_class = FriendInvitationSerializer


class UserProfileCreateView(APIView):
    def post(self, request, *args, **kwargs):
        user_pk = self.kwargs["user_pk"]
        user = get_object_or_404(User, pk=user_pk)
        existing_profile = UserProfile.objects.filter(user=user).first()
        if existing_profile:
            serializer = UserProfileSerializer(existing_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save(user=user)
            return Response(UserProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, *args, **kwargs):
        user_profile_pk = self.kwargs["user_profile_pk"]
        user_profile = get_object_or_404(UserProfile, pk=user_profile_pk)

        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(UserProfileSerializer(updated_profile).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
