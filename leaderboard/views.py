from django.shortcuts import render
from .models import Jogador
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def index(request):
    jogadores = Jogador.objects.order_by('-vitorias')  # Ordem decrescente
    context = {"jogadores": jogadores}
    return render(request, "leaderboard/index.html", context)