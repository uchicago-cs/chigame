from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Game, Lobby, User


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"


def lobby_list(request):
    lobbies = Lobby.objects.all()
    context = {"object_list": lobbies}
    return render(request, "games/lobby_list.html", context)


def lobby_join(request, pk):
    lobby = get_object_or_404(Lobby, pk=pk)
    joined = Lobby.objects.filter(members=request.user.id)
    print(joined, lobby)
    if lobby in joined:
        return HttpResponseNotFound("Already joined.")
    lobby.members.add(request.user)
    return redirect(reverse("lobby-details", kwargs={"pk": lobby.id}))


@login_required
def leave_lobby(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        lobby_id = request.POST.get(
            "lobby_id"
        )  # You need to pass the lobby_id from the view that renders this template

        user = get_object_or_404(User, username=user_id)
        lobby = get_object_or_404(Lobby, id=lobby_id)

        if user in lobby.members.all():
            lobby.members.remove(user)
            # Redirect to the lobby details page
            return HttpResponseRedirect(reverse("lobby_details", args=[lobby_id]))

    # Redirect to the 404 page if the user is not in the lobby
    return render(request, "templates/404.html")


class ViewLobbyDetails(DetailView):
    model = Lobby
    template_name = "games/lobby_details.html"
    context_object_name = "lobby_detail"
    """
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ViewLobbyDetails, self).get_context_data(**kwargs)
        context['user'] = self.request.user
    """


class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"


class GameCreateView(UserPassesTestMixin, CreateView):
    model = Game
    fields = ["name", "description", "min_players", "max_players"]
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game-list")
    raise_exception = True  # if user is not staff member, raise exception

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


class GameEditView(UserPassesTestMixin, UpdateView):
    model = Game
    fields = ["name", "description", "min_players", "max_players"]
    template_name = "games/game_form.html"
    raise_exception = True  # if user is not staff member, raise exception

    # if edit is successful, redirect to that game's detail page
    def get_success_url(self):
        return reverse_lazy("game-detail", kwargs={"pk": self.kwargs["pk"]})

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff
