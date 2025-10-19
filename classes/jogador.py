import pygame
import sys
import os

class Jogador:
    def __init__(self, x, y, tamanho_celula):
        caminho_script = os.path.dirname(__file__)
        caminho_assets = os.path.join(caminho_script, '..', 'assets')
        caminho_spritesheet = os.path.join(caminho_assets, 'personagem_spritesheet.png')

        try:
            self.spritesheet = pygame.image.load(caminho_spritesheet).convert_alpha()
            # --- DEBUG 1: VERIFICAR IMAGEM CARREGADA ---
            print(f"[DEBUG JOGADOR __init__] Sucesso! Spritesheet carregada. Dimensões: {self.spritesheet.get_size()}")
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
        self.tempo_animacao = 150
        self.ultimo_update = pygame.time.get_ticks()

    def carregar_sprites(self):
        largura_sprite = 16
        altura_sprite = 16
        animacoes = {
            "andando_baixo": [], "parado_baixo": [], "andando_cima": [], "parado_cima": [],
            "andando_esq": [], "parado_esq": [], "andando_dir": [], "parado_dir": [],
        }
        for i in range(4):
            for j in range(4):
                x = j * largura_sprite; y = i * altura_sprite
                imagem = self.spritesheet.subsurface(pygame.Rect(x, y, largura_sprite, altura_sprite))
                imagem = pygame.transform.scale(imagem, (self.tamanho_celula, self.tamanho_celula))
                if i == 0: animacoes["andando_baixo"].append(imagem)
                elif i == 1: animacoes["andando_esq"].append(imagem)
                elif i == 2: animacoes["andando_dir"].append(imagem)
                elif i == 3: animacoes["andando_cima"].append(imagem)
        animacoes["parado_baixo"] = [animacoes["andando_baixo"][0]]
        animacoes["parado_cima"] = [animacoes["andando_cima"][0]]
        animacoes["parado_esq"] = [animacoes["andando_esq"][0]]
        animacoes["parado_dir"] = [animacoes["andando_dir"][0]]
        
        # --- DEBUG 2: VERIFICAR DICIONÁRIO DE ANIMAÇÕES ---
        print(f"[DEBUG JOGADOR carregar_sprites] Frames 'andando_baixo': {len(animacoes['andando_baixo'])} sprites")
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
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.tempo_animacao:
            self.ultimo_update = agora
            self.frame_atual = (self.frame_atual + 1) % len(self.animacoes[self.estado_atual])
        self.rect.topleft = (self.pos_x_px, self.pos_y_px)

    def get_pos_grid(self, offset_x, offset_y):
        col = int((self.pos_x_px - offset_x) // self.tamanho_celula)
        lin = int((self.pos_y_px - offset_y) // self.tamanho_celula)
        return lin, col

    def draw(self, superficie):
        imagem_atual = self.animacoes[self.estado_atual][self.frame_atual]
        # --- DEBUG 3: VERIFICAR O QUE ESTÁ A SER DESENHADO ---
        #print(f"[DEBUG JOGADOR draw] Desenhando estado '{self.estado_atual}' frame {self.frame_atual} em {self.rect}")
        superficie.blit(imagem_atual, self.rect)