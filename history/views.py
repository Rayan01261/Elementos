from django.shortcuts import render
from .models import Partida
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def index(request):
    partidas = Partida.objects.filter(
        jogador1=request.user
    ).union(
        Partida.objects.filter(jogador2=request.user)
    )  # Ordem decrescente
    context = {"partidas": partidas}
    return render(request, "history/index.html", context)
