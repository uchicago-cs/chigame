from django.shortcuts import render

# Create your views here.

def demo_game(request):
    return render(request, "achievements/demo_game.html")
