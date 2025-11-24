import pygame
import sys
import os

class Jogador:
    def __init__(self, x, y, tamanho_celula):
        caminho_script = os.path.dirname(__file__)
        caminho_assets = os.path.join(caminho_script, '..', 'assets')
        caminho_spritesheet = os.path.join(caminho_assets, 'andar.png') #

        try:
            self.spritesheet = pygame.image.load(caminho_spritesheet).convert_alpha() #
        except pygame.error as e:
            print(f"[ERRO JOGADOR __init__] Não foi possível carregar a imagem: {caminho_spritesheet}")
            pygame.quit()
            sys.exit()

        self.tamanho_celula = tamanho_celula
        self.velocidade = 120
        
        self.inventario = {} 
        self.carga_maxima = 20 

        # Posições de Ponto Flutuante para movimento preciso
        self.pos_x_px = float(x) #
        self.pos_y_px = float(y) #
        
        self.animacoes = self.carregar_sprites() #
        self.estado_atual = "parado_baixo" #
        self.frame_atual = 0
        self.tempo_animacao = 100
        self.ultimo_update = pygame.time.get_ticks()

        # --- CORREÇÃO DA HITBOX ---
        # Em vez de usar o rect da imagem, criamos um rect MANUAL pequeno para os pés.
        # Aumentei um pouco para (40, 20) para facilitar a colisão
        self.rect = pygame.Rect(0, 0, 35, 70) 
        self.rect.center = (round(self.pos_x_px), round(self.pos_y_px))

    def carregar_sprites(self):
        # (Este método permanece igual ao original, carregando e cortando o spritesheet)
        sheet_largura, sheet_altura = self.spritesheet.get_size() #
        largura_sprite_original = sheet_largura / 4
        altura_sprite_original = sheet_altura

        animacoes = {
            "andando_baixo": [], "parado_baixo": [], "andando_cima": [], "parado_cima": [],
            "andando_esq": [], "parado_esq": [], "andando_dir": [], "parado_dir": [],
        }

        nova_altura = int(self.tamanho_celula * 1.5) #
        proporcao = largura_sprite_original / altura_sprite_original
        nova_largura = int(nova_altura * proporcao) #

        for i in range(4):
            x = i * largura_sprite_original
            imagem = self.spritesheet.subsurface(pygame.Rect(x, 0, largura_sprite_original, altura_sprite_original))
            imagem_redimensionada = pygame.transform.scale(imagem, (nova_largura, nova_altura)) #
            
            animacoes["andando_dir"].append(imagem_redimensionada) #
            animacoes["andando_esq"].append(pygame.transform.flip(imagem_redimensionada, True, False)) #

        animacoes["andando_baixo"] = animacoes["andando_dir"]
        animacoes["andando_cima"] = animacoes["andando_dir"]
        animacoes["parado_baixo"] = [animacoes["andando_baixo"][0]]
        animacoes["parado_esq"] = [animacoes["andando_esq"][0]]
        animacoes["parado_dir"] = [animacoes["andando_dir"][0]]
        animacoes["parado_cima"] = [animacoes["andando_cima"][0]]
        
        return animacoes

    def update(self, direcao_x, direcao_y, decorrido):
        # Lógica de animação
        estado_anterior = self.estado_atual
        if direcao_x == 0 and direcao_y == 0:
            if "andando" in self.estado_atual: self.estado_atual = self.estado_atual.replace("andando", "parado") #
        else:
            if direcao_y > 0: self.estado_atual = "andando_baixo"
            elif direcao_y < 0: self.estado_atual = "andando_cima"
            elif direcao_x > 0: self.estado_atual = "andando_dir"
            elif direcao_x < 0: self.estado_atual = "andando_esq"
        if self.estado_atual != estado_anterior: self.frame_atual = 0 #
        
        # --- ATENÇÃO: O movimento físico (self.pos_x_px) é atualizado no main.py agora ---
        # Este update serve mais para a animação e sincronização final.
        
        # Sincroniza o Rect (Hitbox) com a posição float
        self.rect.center = (round(self.pos_x_px), round(self.pos_y_px))

        # Atualiza frames da animação
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.tempo_animacao: #
            self.ultimo_update = agora
            self.frame_atual = (self.frame_atual + 1) % len(self.animacoes[self.estado_atual]) #
    
    def draw(self, superficie, camera):
        imagem_atual = self.animacoes[self.estado_atual][self.frame_atual]
        
        # --- CORREÇÃO VISUAL ---
        # 1. Cria um retângulo temporário para a IMAGEM (não para a física)
        rect_visual = imagem_atual.get_rect()
        
        # 2. Alinha os pés da imagem (midbottom) com os pés da hitbox (midbottom)
        rect_visual.midbottom = self.rect.midbottom
        
        # 3. Aplica a câmera na posição visual corrigida
        posicao_na_tela = camera.apply_to_rect(rect_visual)
        
        superficie.blit(imagem_atual, posicao_na_tela)