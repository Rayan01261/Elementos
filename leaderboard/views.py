from django.shortcuts import render
from .models import Jogador
# Create your views here.
def index(request):
    jogadores = Jogador.objects.order_by('-vitorias')  # Ordem decrescente
    context = {"jogadores": jogadores}
    return render(request, "leaderboard/index.html", context)