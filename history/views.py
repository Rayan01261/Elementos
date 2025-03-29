from django.shortcuts import render
from models import Partida
# Create your views here.

def index(request):
    partidas = Partida.objects.all()
    context = {"partidas": partidas}
    return render(request, "history/index.html", context)
