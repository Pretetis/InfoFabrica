import pygame

COR_TITULO=(255,255,255)
class Caminhao:
    def __init__(self, x, y, imagem):
        self.imagem = imagem
        self.largura, self.altura = self.imagem.get_size()
        self.pos_base = pygame.math.Vector2(x, y)
        self.rect = self.imagem.get_rect(topleft=self.pos_base)
        
        # Área de interação para o jogador (atrás do caminhão)
        self.area_carga = pygame.Rect(x + self.largura, y, 60, self.altura)

        self.estado = 'PARADO'  # PARADO, PARTINDO, VOLTANDO
        self.velocidade = 350 # Pixels por segundo
        self.carga = {} # Ex: {"Motor V1": 5}

    def update(self, dt, game_state, grid):
        if self.estado == 'PARTINDO':
            self.rect.x -= self.velocidade * dt
            # Se saiu da tela
            if self.rect.right < 0:
                self.processar_entrega(game_state)
                game_state.produzir_nas_maquinas(grid)
                game_state.avancar_turno()
                self.iniciar_retorno()

        elif self.estado == 'VOLTANDO':
            self.rect.x += self.velocidade * dt
            # Se voltou para a posição original
            if self.rect.x >= self.pos_base.x:
                self.rect.topleft = self.pos_base
                self.estado = 'PARADO'
                game_state.estado_jogo = 'JOGANDO'

    def draw(self, surface, fonte):
        surface.blit(self.imagem, self.rect)
        # Desenha um contorno na área de carga para feedback visual
        pygame.draw.rect(surface, (255, 200, 0, 150), self.area_carga, 2)

        # Desenha a carga atual do caminhão
        if self.carga:
            y_offset = 0
            for item, qtd in self.carga.items():
                texto_carga = fonte.render(f"{item}: {qtd}", True, COR_TITULO)
                pos = (self.rect.centerx - texto_carga.get_width() / 2, self.rect.y - 25 - y_offset)
                surface.blit(texto_carga, pos)
                y_offset += 20


    def iniciar_partida(self):
        if not self.estado == 'PARADO': return
        self.estado = 'PARTINDO'

    def iniciar_retorno(self):
        self.rect.x = -self.largura - 20 # Começa fora da tela à esquerda
        self.estado = 'VOLTANDO'

    def receber_carga(self, tipo_item, quantidade):
        if tipo_item not in self.carga:
            self.carga[tipo_item] = 0
        self.carga[tipo_item] += quantidade
        print(f"Caminhão carregado com {quantidade}x {tipo_item}. Carga atual: {self.carga}")

    def processar_entrega(self, game_state):
        if not self.carga:
            print("Caminhão partiu vazio.")
            return

        print("Processando entrega...")
        pedidos_a_remover = []
        for pedido in game_state.pedidos:
            if not pedido.entregue and pedido.tipo in self.carga:
                if self.carga[pedido.tipo] >= pedido.quantidade:
                    print(f"Pedido de {pedido.quantidade}x {pedido.tipo} entregue!")
                    pedido.entregue = True
                    recompensa = pedido.quantidade * 100 # Exemplo de recompensa
                    game_state.dinheiro += recompensa
                    game_state.reputacao += 10
                    pedidos_a_remover.append(pedido) # Marcar para remoção posterior se quiser
        
        self.carga.clear() # Esvazia o caminhão após a entrega