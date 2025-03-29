from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

 # Associa as cartas ao baralho
class Jogador(AbstractUser):
    vitorias = models.SmallIntegerField(default=0)

@receiver(post_save, sender=Jogador)
def criar_baralho_padrao(sender, instance, created, **kwargs):
    if created:  # Verifica se o jogador foi recém-criado
        # Cria o baralho para o jogador
        baralho = Baralho.objects.create(jogador=instance)

        # Adiciona cartas predeterminadas ao baralho
        cartas_padrao = []
        for tipo in ['fogo', 'agua', 'neve']:
            for numero in range(1, 11):
                carta, _ = Carta.objects.get_or_create(tipo=tipo, numero=numero)
                cartas_padrao.append(carta)
        baralho.cartas.set(cartas_padrao) 

class Partida(models.Model):
    jogador1 = models.ForeignKey(
        Jogador, on_delete=models.CASCADE, related_name='partidas_como_jogador1'
    )
    jogador2 = models.ForeignKey(
        Jogador, on_delete=models.CASCADE, related_name='partidas_como_jogador2'
    )
    PARTIDA_STATUS= [
        ('em andamento', 'Em andamento'),
        ('finalizada', 'Finalizada')
    ]
    vencedor = models.ForeignKey(
        Jogador, on_delete=models.CASCADE, null=True, blank=True, related_name='partidas_vencidas')
    status = models.CharField(max_length=20, choices=PARTIDA_STATUS, default='em andamento')

class Carta(models.Model):
    TIPO_CHOICES = [
        ('fogo', 'Fogo'),
        ('agua', 'Água'),
        ('neve', 'Neve'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    numero = models.SmallIntegerField()
    
class Baralho(models.Model):
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, default=None)
    cartas = models.ManyToManyField(Carta)

class Jogada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE)
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE)
