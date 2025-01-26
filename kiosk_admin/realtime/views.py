from django.shortcuts import render


def index(request):
    return render(request, "realtime/index.html")

def room(request, room_name):
    return render(request, "realtime/room_live.html", {"room_name": room_name})