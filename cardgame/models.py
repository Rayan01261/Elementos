from django.db import models

class Jogador(models.Model):
    nome = models.CharField(max_length=100)
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
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    cartas = models.ManyToManyField(Carta)

class Jogada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE)
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE)
