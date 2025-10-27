import pygame

COR_TITULO=(255,255,255)
class Caminhao:
    def __init__(self, x, y, imagem):
        self.imagem = imagem
        self.largura, self.altura = self.imagem.get_size()
        # --- MODIFICADO (Request 1) ---
        self.pos_base = pygame.math.Vector2(x, y)
        self.rect = self.imagem.get_rect(center=self.pos_base) # Usar 'center'
        
        # Área de interação para o jogador (atrás do caminhão)
        # self.area_carga = pygame.Rect(x + self.largura, y, 60, self.altura) # Original (Lado)
        self.area_carga = pygame.Rect(x - self.largura / 2, y + self.altura / 2, self.largura, 60) # Novo (Abaixo)
        # -------------------------------

        self.estado = 'PARADO'  # PARADO, PARTINDO, VOLTANDO
        self.velocidade = 350 # Pixels por segundo
        self.carga = {} # Ex: {"Motor V1": 5}

    def update(self, dt, game_state, grid):
        # --- MODIFICADO (Request 1: Lógica Top-Down) ---
        if self.estado == 'PARTINDO':
            # self.rect.x -= self.velocidade * dt # Original
            self.rect.y -= self.velocidade * dt # Novo (Move para Cima)
            
            # Se saiu da tela
            # if self.rect.right < 0: # Original
            if self.rect.bottom < 0: # Novo
                self.processar_entrega(game_state)
                game_state.produzir_nas_maquinas(grid) # Chama a produção
                game_state.avancar_turno() # Avança o turno
                self.iniciar_retorno()

        elif self.estado == 'VOLTANDO':
            # self.rect.x += self.velocidade * dt # Original
            self.rect.y += self.velocidade * dt # Novo (Move para Baixo)

            # Se voltou para a posição original
            # if self.rect.x >= self.pos_base.x: # Original
            if self.rect.centery >= self.pos_base.y: # Novo
                self.rect.center = self.pos_base # Reposiciona no centro
                self.estado = 'PARADO'
                game_state.estado_jogo = 'JOGANDO'
        
        # Atualizar a area_carga para seguir o caminhão
        self.area_carga.midtop = self.rect.midbottom
        # ----------------------------------------------


    def draw(self, surface, fonte, camera): # --- MODIFICADO: Adiciona 'camera'
        # --- MODIFICADO (Request 1: Aplicar Câmera) ---
        pos_na_tela = camera.apply_to_rect(self.rect)
        surface.blit(self.imagem, pos_na_tela)
        
        # Desenha um contorno na área de carga para feedback visual
        area_carga_na_tela = camera.apply_to_rect(self.area_carga)
        pygame.draw.rect(surface, (255, 200, 0, 150), area_carga_na_tela, 2)
        # -----------------------------------------------

        # Desenha a carga atual do caminhão
        if self.carga:
            y_offset = 0
            for item, qtd in self.carga.items():
                texto_carga = fonte.render(f"{item}: {qtd}", True, COR_TITULO)
                # --- MODIFICADO (Request 1: Posicionar texto relativo à tela) ---
                pos = (pos_na_tela.centerx - texto_carga.get_width() / 2, pos_na_tela.y - 25 - y_offset)
                surface.blit(texto_carga, pos)
                y_offset += 20


    def iniciar_partida(self):
        if not self.estado == 'PARADO': return
        self.estado = 'PARTINDO'

    def iniciar_retorno(self):
        # --- MODIFICADO (Request 1: Lógica Top-Down) ---
        # self.rect.x = -self.largura - 20 # Original
        self.rect.y = -self.altura - 20 # Novo (Começa fora da tela, em cima)
        self.estado = 'VOLTANDO'
        # ----------------------------------------------

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