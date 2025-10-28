import pygame
import random 

COR_TITULO=(255,255,255)
class Caminhao:
    def __init__(self, x, y, imagem, slot_altura_px): 
        self.imagem = imagem
        self.largura, self.altura = self.imagem.get_size()
        self.pos_base = pygame.math.Vector2(x, y)
        self.rect = self.imagem.get_rect(center=self.pos_base) 
        
        self.slot_altura = slot_altura_px
        self.y_topo_slot = self.pos_base.y - (self.slot_altura / 2) +80 

        # --- ÁREA DE CARGA CORRIGIDA (PASSO ANTERIOR) ---
        altura_area_carga = 60
        nova_y = (y + self.altura / 2) - altura_area_carga # Termina na borda inferior do caminhão
        self.area_carga = pygame.Rect(x - self.largura / 2, nova_y, self.largura, altura_area_carga) 
        # ----------------------------------------------

        self.estado = 'PARADO'  # PARADO, PARTINDO, VOLTANDO
        self.velocidade = 350 
        self.carga = {} 

    def update(self, dt, game_state, grid):
            if self.estado == 'PARTINDO':
                self.rect.y -= self.velocidade * dt 
                
                # --- LÓGICA DE PARTIDA MODIFICADA ---
                if self.rect.centery < self.y_topo_slot:
                    
                    # 1. CHECA PENALIDADES E GAME OVER (ANTES DE PROCESSAR ENTREGAS)
                    if game_state.checar_penalidades_e_gameover():
                        # Se for game over, o caminhão "some" mas o jogo para
                        self.iniciar_retorno() # (Apenas para o caminhão sumir)
                        return # Não processa mais nada
                    
                    # 2. Se o jogo não acabou, processa o resto
                    self.processar_entrega(game_state) # Processa entregas (atrasadas ou não)
                    game_state.produzir_nas_maquinas(grid) 
                    game_state.avancar_turno() # Avança o turno (agora só incrementa)
                    self.iniciar_retorno() 
            
            if self.estado == 'VOLTANDO':
                    self.rect.y += self.velocidade * dt 

                    if self.rect.centery >= self.pos_base.y: 
                        self.rect.center = self.pos_base 
                        self.estado = 'PARADO'
                        
                        # Só libera o jogador se não for Game Over
                        if game_state.estado_jogo != 'GAME_OVER':
                            game_state.estado_jogo = 'JOGANDO' 


    def draw(self, surface, fonte, camera): 
        pos_na_tela = camera.apply_to_rect(self.rect)
        
        pos_final_blit = pos_na_tela
        if self.estado == 'PARTINDO' or self.estado == 'VOLTANDO':
            offset_x = random.randint(-1, 1) 
            offset_y = random.randint(-1, 1) 
            pos_final_blit = pos_na_tela.move(offset_x, offset_y)
        
        if self.rect.centery > self.y_topo_slot:
            surface.blit(self.imagem, pos_final_blit) 

        if self.estado == 'PARADO':
            area_carga_na_tela = camera.apply_to_rect(self.area_carga)
           # pygame.draw.rect(surface, (255, 200, 0, 150), area_carga_na_tela, 2)
        
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
            self.rect.centery = self.y_topo_slot - (self.altura / 2)
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
                    recompensa = pedido.quantidade * 100 
                    game_state.dinheiro += recompensa
                    game_state.reputacao += 2 # <--- Bônus de +2 (corrigido)
                    pedidos_a_remover.append(pedido) 
        
        self.carga.clear()