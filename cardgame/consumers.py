import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Baralho, Carta, Jogador  # Modificado para usar Jogador
import random

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = f"game_room"

        player_count = cache.get('player_count', 0)
        if player_count >= 2:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

        player_count += 1
        cache.set('player_count', player_count)
        
        player_ids = cache.get("player_ids", [])
        player_ids.append(self.scope['user'].id)
        cache.set("player_ids", player_ids)

        # Inicializa a pontuação dos jogadores
        if player_count == 2:
            cache.set("score_1", 0)
            cache.set("score_2", 0)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'message': 'O jogo começou!'
                }
            )

        try:
            jogador = await sync_to_async(Jogador.objects.get)(id=self.scope['user'].id)
            baralho_obj = await sync_to_async(Baralho.objects.get)(jogador=jogador)
            baralho = list(await sync_to_async(lambda: list(baralho_obj.cartas.all()))())
            random.shuffle(baralho)
        except Baralho.DoesNotExist:
            baralho = []

        mao = baralho[:5]
        baralho = baralho[5:]

        cache.set(f"baralho_{self.scope['user'].id}", [carta.id for carta in baralho])
        cache.set(f"mao_{self.scope['user'].id}", [carta.id for carta in mao])

        await self.send(text_data=json.dumps({
            'type': 'update_hand',
            'hand': [{'id': carta.id, 'tipo': carta.tipo, 'numero': carta.numero} for carta in mao]
        }))

    async def disconnect(self, close_code):
        user_id = self.scope['user'].id

        # Remove o jogador do grupo WebSocket
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Atualiza a contagem de jogadores
        player_count = max(0, cache.get('player_count', 0) - 1)
        cache.set('player_count', player_count)

        # Remove o jogador da lista de IDs no cache
        player_ids = cache.get("player_ids", [])
        if user_id in player_ids:
            player_ids.remove(user_id)
        cache.set("player_ids", player_ids)

        # Apaga os dados do jogador no cache
        cache.delete(f"mao_{user_id}")
        cache.delete(f"baralho_{user_id}")
        cache.delete(f"jogada_{user_id}")

        # Apagar o placar do jogador
        if player_count == 0:  # Se for o último jogador saindo
            cache.delete("score_1")
            cache.delete("score_2")

        # Se restar apenas 1 jogador, encerrar o jogo
        if player_count == 1:
            other_player_id = player_ids[0] if player_ids else None
            if other_player_id:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': 'O outro jogador desconectou. O jogo foi encerrado!'
                    }
                )

            await self.end_game()


    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')

        if message.startswith('play_card:'):
            card_played_id = int(message.split(':')[1])
            user_id = self.scope['user'].id

            mao_ids = cache.get(f"mao_{user_id}", [])
            baralho_ids = cache.get(f"baralho_{user_id}", [])

            mao = list(await sync_to_async(lambda: list(Carta.objects.filter(id__in=mao_ids)))())
            baralho = list(await sync_to_async(lambda: list(Carta.objects.filter(id__in=baralho_ids)))())

            card_played = next((carta for carta in mao if carta.id == card_played_id), None)
            if card_played:
                mao.remove(card_played)
                nome = await self.get_username(user_id)
                cache.set(f"jogada_{user_id}", {
                    'id': card_played.id,
                    'tipo': card_played.tipo,
                    'numero': card_played.numero,
                    'nome': nome
                })
                player_ids = cache.get("player_ids", [])
                if len(player_ids) == 2:
                    jogador1_id, jogador2_id = player_ids
                    jogada1 = cache.get(f"jogada_{jogador1_id}")
                    jogada2 = cache.get(f"jogada_{jogador2_id}")

                    if jogada1 and jogada2:
                        jogador1_name = await self.get_username(jogador1_id)
                        jogador2_name = await self.get_username(jogador2_id)

                        vencedor = self.check_round_winner(jogada1, jogada2)

                        # Atualiza o placar
                        if vencedor == jogador1_name:
                            current_score = cache.get("score_1", 0)
                            cache.set("score_1", current_score + 1)
                        elif vencedor == jogador2_name:
                            current_score = cache.get("score_2", 0)
                            cache.set("score_2", current_score + 1)

                        # Envia as jogadas e o vencedor
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'update_round',
                                'vencedor': vencedor,
                                'jogadas': [
                                    {'nome': jogador1_name, 'jogada': jogada1},
                                    {'nome': jogador2_name, 'jogada': jogada2}
                                ],
                                'placar': {
                                    jogador1_name: cache.get("score_1", 0),
                                    jogador2_name: cache.get("score_2", 0)
                                }
                            }
                        )

                        cache.delete(f"jogada_{jogador1_id}")
                        cache.delete(f"jogada_{jogador2_id}")

                if baralho:
                    new_card = baralho.pop(0)
                    mao.append(new_card)

                cache.set(f"mao_{user_id}", [carta.id for carta in mao])
                cache.set(f"baralho_{user_id}", [carta.id for carta in baralho])

                await self.send(text_data=json.dumps({
                    'type': 'update_hand',
                    'hand': [{'id': carta.id, 'tipo': carta.tipo, 'numero': carta.numero} for carta in mao]
                }))
        if message.startswith('A partida foi encerrada!'):
            await self.end_game()
    async def update_round(self, event):
        vencedor = event['vencedor']
        jogadas = event['jogadas']
        placar = event['placar']

        await self.send(text_data=json.dumps({
            'type': 'round_update',
            'vencedor': vencedor,
            'jogadas': jogadas,
            'placar': placar  # Envia o placar atualizado
        }))

    async def start_game(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'start',
            'message': message
        }))

    async def end_game(self):
        cache.set('player_count', 0)

        player_ids = cache.get("player_ids", [])
        for player_id in player_ids:
            cache.delete(f"mao_{player_id}")
            cache.delete(f"baralho_{player_id}")
            cache.delete(f"jogada_{player_id}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'A partida foi encerrada!'
            }
        )

        cache.delete('player_ids')

        for player_id in player_ids:
            # Aqui você precisa garantir que está enviando a mensagem de desconexão para o canal certo
            # Esse código pode precisar ser ajustado dependendo da sua implementação do "channel_name"
            player_channel_name = self.channel_name  # Ajuste se necessário
            await self.channel_layer.group_discard(self.room_group_name, player_channel_name)

    async def get_username(self, user_id):
        jogador = await sync_to_async(Jogador.objects.get)(id=user_id)
        return jogador.username
    
    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    def check_round_winner(self, jogada1, jogada2):
        element_map = {
            'agua': 'fogo',
            'fogo': 'neve',
            'neve': 'agua',
        }

        tipo1, tipo2 = jogada1['tipo'], jogada2['tipo']

        if tipo1 == tipo2:
            if jogada1['numero'] > jogada2['numero']:
                return jogada1['nome']
            elif jogada1['numero'] < jogada2['numero']:
                return jogada2['nome']
            else:
                return 'Empate'
        elif element_map.get(tipo1) == tipo2:
            return jogada1['nome']
        elif element_map.get(tipo2) == tipo1:
            return jogada2['nome']
        else:
            return 'Empate'
