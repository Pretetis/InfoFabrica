import pygame
import sys
import os

class Jogador:
    def __init__(self, x, y, tamanho_celula):
        caminho_script = os.path.dirname(__file__)
        caminho_assets = os.path.join(caminho_script, '..', 'assets')
        caminho_spritesheet = os.path.join(caminho_assets, 'andar.png')

        try:
            self.spritesheet = pygame.image.load(caminho_spritesheet).convert_alpha()
            print(f"[DEBUG JOGADOR __init__] Sucesso! Spritesheet 'andar.png' carregada. Dimensões: {self.spritesheet.get_size()}")

        except pygame.error as e:
            print(f"[ERRO JOGADOR __init__] Não foi possível carregar a imagem: {caminho_spritesheet}")
            pygame.quit()
            sys.exit()

        self.tamanho_celula = tamanho_celula
        self.pos_x_px = x
        self.pos_y_px = y
        self.velocidade = 120
        self.rect = pygame.Rect(self.pos_x_px, self.pos_y_px, self.tamanho_celula, self.tamanho_celula)

        self.animacoes = self.carregar_sprites()
        self.estado_atual = "parado_baixo"
        self.frame_atual = 0
        self.tempo_animacao = 100
        self.ultimo_update = pygame.time.get_ticks()

    def carregar_sprites(self):
        sheet_largura, sheet_altura = self.spritesheet.get_size()
        largura_sprite_original = sheet_largura / 4
        altura_sprite_original = sheet_altura

        animacoes = {
            "andando_baixo": [], "parado_baixo": [], "andando_cima": [], "parado_cima": [],
            "andando_esq": [], "parado_esq": [], "andando_dir": [], "parado_dir": [],
        }

        # --- CORREÇÃO DE ESCALA PARA TAMANHO VISUAL ADEQUADO ---
        # A nova altura será um pouco maior que a célula para um visual melhor.
        # Um fator de 1.5 (ou 60 pixels se a célula for 40) costuma funcionar bem.
        nova_altura = int(self.tamanho_celula * 1.5)
        
        # A nova largura é calculada para manter a proporção original.
        proporcao = largura_sprite_original / altura_sprite_original
        nova_largura = int(nova_altura * proporcao)


        for i in range(4):
            x = i * largura_sprite_original
            imagem = self.spritesheet.subsurface(pygame.Rect(x, 0, largura_sprite_original, altura_sprite_original))
            
            imagem_redimensionada = pygame.transform.scale(imagem, (nova_largura, nova_altura))
            
            animacoes["andando_dir"].append(imagem_redimensionada)
            animacoes["andando_esq"].append(pygame.transform.flip(imagem_redimensionada, True, False))

        animacoes["andando_baixo"] = animacoes["andando_dir"]
        animacoes["andando_cima"] = animacoes["andando_dir"]

        animacoes["parado_baixo"] = [animacoes["andando_baixo"][0]]
        animacoes["parado_esq"] = [animacoes["andando_esq"][0]]
        animacoes["parado_dir"] = [animacoes["andando_dir"][0]]
        animacoes["parado_cima"] = [animacoes["andando_cima"][0]]
        
        print(f"[DEBUG JOGADOR carregar_sprites] Animações carregadas. Novo tamanho do sprite: ({nova_largura}x{nova_altura})")
        return animacoes


    def update(self, direcao_x, direcao_y, decorrido, limites):
        estado_anterior = self.estado_atual
        if direcao_x == 0 and direcao_y == 0:
            if "andando" in self.estado_atual: self.estado_atual = self.estado_atual.replace("andando", "parado")
        else:
            if direcao_y > 0: self.estado_atual = "andando_baixo"
            elif direcao_y < 0: self.estado_atual = "andando_cima"
            elif direcao_x > 0: self.estado_atual = "andando_dir"
            elif direcao_x < 0: self.estado_atual = "andando_esq"
        if self.estado_atual != estado_anterior: self.frame_atual = 0
        
        self.pos_x_px += direcao_x * self.velocidade * decorrido
        self.pos_y_px += direcao_y * self.velocidade * decorrido
        offset_x, offset_y, grid_colunas, grid_linhas = limites
        self.pos_x_px = max(offset_x, min(self.pos_x_px, offset_x + (grid_colunas - 1) * self.tamanho_celula))
        self.pos_y_px = max(offset_y, min(self.pos_y_px, offset_y + (grid_linhas - 1) * self.tamanho_celula))
        self.rect.topleft = (self.pos_x_px, self.pos_y_px)

        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.tempo_animacao:
            self.ultimo_update = agora
            self.frame_atual = (self.frame_atual + 1) % len(self.animacoes[self.estado_atual])

    def get_pos_grid(self, offset_x, offset_y):
        col = int((self.pos_x_px - offset_x) // self.tamanho_celula)
        lin = int((self.pos_y_px - offset_y) // self.tamanho_celula)
        return lin, col

    def draw(self, superficie):
        imagem_atual = self.animacoes[self.estado_atual][self.frame_atual]
        
        # --- CENTRALIZA A IMAGEM MAIOR NA CÉLULA ---
        # Posiciona o centro inferior da imagem no centro inferior da caixa de colisão.
        # Isso faz o personagem "pisar" na célula corretamente.
        imagem_rect = imagem_atual.get_rect(midbottom = self.rect.midbottom)
        
        superficie.blit(imagem_atual, imagem_rect)