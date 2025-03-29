from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Jogador, Baralho
import random

def index(request):
    jogadores = Jogador.objects.order_by('-vitorias')  # Ordem decrescente
    register_toggle = False  # Default to Login
    context = {"jogadores": jogadores, "register_toggle": register_toggle}

    if request.method == 'POST':
        if 'register' in request.POST:  # Check if the "REGISTER" button was clicked
            register_toggle = True
        elif 'login' in request.POST:  # Check if the "LOGIN" button was clicked
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("cardgame:goToHub")  # Redireciona para a página do jogo
            else:
                context['error'] = 'Usuário ou senha inválidos'

        context["register_toggle"] = register_toggle
        if 'register_submit' in request.POST:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            password_confirm = request.POST.get('password_confirmation', '').strip()

            if password != password_confirm:
                context['error'] = 'As senhas não coincidem'
            else:
                Jogador.objects.create_user(username=username, password=password)
                context['error'] = 'Usuário cadastrado com sucesso'

    return render(request, "cardgame/index.html", context)

@login_required
def goTogame(request):
    baralho = Baralho.objects.get(jogador=request.user)
    card_list = list(baralho.cartas.all())
    random.shuffle(card_list)
    return render(request, "cardgame/game.html", {'card_list':card_list})

@login_required
def goToHub(request):
    return render(request, "cardgame/hub.html")
