from django.db import models
from django.contrib.auth.models import AbstractUser

class Jogador(AbstractUser):
    vitorias = models.SmallIntegerField(default=0)


class Partida(models.Model):
    jogador1 = models.ForeignKey(
        Jogador, on_delete=models.CASCADE, related_name='partidas_como_jogador1'
    )
    jogador2 = models.ForeignKey(
        Jogador, on_delete=models.CASCADE, related_name='partidas_como_jogador2'
    )
    status = models.CharField(max_length=20, default='em andamento')

class Carta(models.Model):
    tipo = models.CharField(max_length=20)
    numero = models.SmallIntegerField()

class Baralho(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, default=None)
    cartas = models.ManyToManyField(Carta)

class Jogada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE)
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE)
