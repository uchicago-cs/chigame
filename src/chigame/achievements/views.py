from django.shortcuts import render


def demo_game(request):
    return render(request, "achievements/demo_game.html")
