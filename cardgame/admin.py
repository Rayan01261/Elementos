from django.contrib import admin

from .models import Jogador, Partida, Carta, Baralho, Jogada

# Register your models here.
admin.site.register(Jogador)
admin.site.register(Partida)
admin.site.register(Carta)
admin.site.register(Baralho)
admin.site.register(Jogada)