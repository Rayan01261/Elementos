# Generated by Django 5.1.6 on 2025-03-27 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardgame', '0002_remove_baralho_partida_baralho_jogador_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partida',
            name='status',
            field=models.CharField(choices=[('em andamento', 'Em andamento'), ('finalizada', 'Finalizada')], default='em andamento', max_length=20),
        ),
    ]
