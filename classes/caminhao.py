import pygame
import random 

COR_TITULO=(255,255,255)
class Caminhao:
    def __init__(self, x, y, imagem, slot_altura_px): # <--- 1. RECEBE A ALTURA DO SLOT
        self.imagem = imagem
        self.largura, self.altura = self.imagem.get_size()
        self.pos_base = pygame.math.Vector2(x, y)
        self.rect = self.imagem.get_rect(center=self.pos_base) 
        
        # --- NOVO: Armazena a altura do slot
        self.slot_altura = slot_altura_px
        # Define o "ponto de fuga" (a borda superior do slot da doca)
        self.y_topo_slot = self.pos_base.y - (self.slot_altura / 2) +80
        # -------------------------------

        #self.area_carga = pygame.Rect(x - self.largura / 2, y + self.altura / 2, self.largura, 60) 
        nova_y = (y + self.altura / 2) - 60 # Termina na borda inferior do caminhão
        self.area_carga = pygame.Rect(x - self.largura / 2, nova_y, self.largura, 60)

        self.estado = 'PARADO'  # PARADO, PARTINDO, VOLTANDO
        self.velocidade = 350 
        self.carga = {} 

    def update(self, dt, game_state, grid):
            if self.estado == 'PARTINDO':
                self.rect.y -= self.velocidade * dt 
                
                # --- 2. CORREÇÃO DA ANIMAÇÃO ---
                # Verifica se o *centro* do caminhão passou do topo do slot
                if self.rect.centery < self.y_topo_slot:
                    self.processar_entrega(game_state)
                    game_state.produzir_nas_maquinas(grid) 
                    game_state.avancar_turno() 
                    self.iniciar_retorno() 
            
            # --- 3. CORREÇÃO DO BUG DE TRAVAMENTO ---
            # Deve ser um 'if' independente, e NÃO um 'elif'
            if self.estado == 'VOLTANDO':
                    self.rect.y += self.velocidade * dt 

                    # Se voltou para a posição original
                    if self.rect.centery >= self.pos_base.y: 
                        self.rect.center = self.pos_base 
                        self.estado = 'PARADO'
                        game_state.estado_jogo = 'JOGANDO' # Libera o jogador


    def draw(self, surface, fonte, camera): 
        pos_na_tela = camera.apply_to_rect(self.rect)
        
        # Lógica de vibração (mantida)
        pos_final_blit = pos_na_tela
        if self.estado == 'PARTINDO' or self.estado == 'VOLTANDO':
            offset_x = random.randint(-1, 1) 
            offset_y = random.randint(-1, 1) 
            pos_final_blit = pos_na_tela.move(offset_x, offset_y)
        
        # --- 4. CORREÇÃO DA ANIMAÇÃO (DESENHO) ---
        # Só desenha o caminhão se ele estiver "dentro" do slot
        # (Se o centro dele estiver abaixo do topo do slot)
        if self.rect.centery > self.y_topo_slot:
            surface.blit(self.imagem, pos_final_blit) 

        # Desenha a área de carga (apenas se o caminhão estiver parado)
        if self.estado == 'PARADO':
            area_carga_na_tela = camera.apply_to_rect(self.area_carga)
            # pygame.draw.rect(surface, (255, 200, 0, 150), area_carga_na_tela, 2)
        
        # Desenha a carga atual do caminhão
        if self.carga and self.rect.centery > self.y_topo_slot:
            y_offset = 0
            for item, qtd in self.carga.items():
                texto_carga = fonte.render(f"{item}: {qtd}", True, COR_TITULO)
                pos = (pos_na_tela.centerx - texto_carga.get_width() / 2, pos_na_tela.y - 25 - y_offset)
                surface.blit(texto_carga, pos)
                y_offset += 20


    def iniciar_partida(self):
        if not self.estado == 'PARADO': return
        self.estado = 'PARTINDO'

    def iniciar_retorno(self):
            # --- 5. CORREÇÃO DA ANIMAÇÃO (RETORNO) ---
            # Posiciona o caminhão "acima" da porta, pronto para descer
            self.rect.centery = self.y_topo_slot - (self.altura / 2)
            self.estado = 'VOLTANDO'
            # --------------------------------------------------------------------

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
                    recompensa = pedido.quantidade * 100 
                    game_state.dinheiro += recompensa
                    game_state.reputacao += 10
                    pedidos_a_remover.append(pedido) 
        
        self.carga.clear()