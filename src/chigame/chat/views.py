from django.shortcuts import render, redirect

def chat(request):
    return render(request, "chat/index.html")
