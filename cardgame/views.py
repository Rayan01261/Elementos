from django.shortcuts import render
from django.http import HttpResponse
from .models import Jogador
from django.template import loader

# Create your views here.

def index(request):
    jogadores = Jogador.objects.order_by('vitorias')
    template = loader.get_template("cardgame/index.html")
    context = {
        "jogadores" : jogadores
    }
    return HttpResponse(template.render(context, request))