import pygame
import random
import sys

# --- CLASSES ---
from classes.game_state import GameState
from classes.jogador import Jogador
from classes.maquina import Maquina
from classes.caminhao import Caminhao

# --- NOVA CLASSE: CAMERA ---
class Camera:
    def __init__(self, largura_tela, altura_tela):
        self.offset = pygame.math.Vector2(0, 0)
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela

    def center_on(self, target_rect):
        self.offset.x = target_rect.centerx - self.largura_tela // 2
        self.offset.y = target_rect.centery - self.altura_tela // 2

    def apply_to_rect(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def screen_to_world(self, screen_pos):
        # Converte coordenadas da tela (ex: mouse) para coordenadas do mundo
        return (screen_pos[0] + self.offset.x, screen_pos[1] + self.offset.y)

# --- Início do Código Principal ---
pygame.init()
# --- CONFIGURAÇÕES ---
JOGO_LARGURA, JOGO_ALTURA = 1200, 600
TELA = pygame.display.set_mode((JOGO_LARGURA, JOGO_ALTURA), pygame.RESIZABLE)
TELA_JOGO = pygame.Surface((JOGO_LARGURA, JOGO_ALTURA))
pygame.display.set_caption("Jogo de Gestão com Logística")
COR_FUNDO=(30,30,40);COR_PAINEL=(45,45,55);COR_TEXTO=(220,220,220);COR_TITULO=(255,255,255);COR_FUNDO_EXTERNO=(10,10,10);COR_BOTAO_NORMAL=(70,70,80);COR_BOTAO_HOVER=(100,100,110);COR_BOTAO_BORDA=(130,130,140);VERDE_BRILHANTE=(0,255,120);VERMELHO_BRILHANTE=(255,80,80);AMARELO_BRILHANTE=(255,200,0)
FONTE=pygame.font.SysFont("monospace",18);FONTE_TITULO=pygame.font.SysFont("monospace",22,bold=True)

# --- CONFIGURAÇÕES DO GRID E SLOTS ---
TAMANHO_CELULA = 60
# Dimensões de um único slot em termos de células (ex: 7x5 células)
SLOT_LARGURA_CELULAS = 7
SLOT_ALTURA_CELULAS = 5
# Dimensões de um slot em pixels
SLOT_LARGURA_PX = SLOT_LARGURA_CELULAS * TAMANHO_CELULA
SLOT_ALTURA_PX = SLOT_ALTURA_CELULAS * TAMANHO_CELULA

# --- IMAGENS ---
IMG_MAQUINA_ESTATICA = pygame.transform.scale(pygame.image.load("assets/maquina.png").convert_alpha(), (TAMANHO_CELULA, TAMANHO_CELULA))
try:
    # Carrega todas as imagens de fábrica disponíveis
    IMG_FABRICA_TILES = {
        "meio": pygame.image.load("assets/fabrica/meio.jpg").convert(),
        "superior": pygame.image.load("assets/fabrica/superior.jpg").convert(),
        "baixo": pygame.image.load("assets/fabrica/baixo.jpg").convert(),
        "esquerda": pygame.image.load("assets/fabrica/esquerda.jpg").convert(),
        "direita": pygame.image.load("assets/fabrica/direita.jpg").convert(),
        "doca": pygame.image.load("assets/fabrica/doca.jpg").convert(),
    }
    # Redimensiona todas as imagens para o tamanho do slot
    for key, img in IMG_FABRICA_TILES.items():
        IMG_FABRICA_TILES[key] = pygame.transform.scale(img, (SLOT_LARGURA_PX, SLOT_ALTURA_PX))
except Exception as e:
    print(f"Erro ao carregar tiles da fábrica: {e}"); IMG_FABRICA_TILES = None
# ... (outros carregamentos de imagem) ...

# --- FUNÇÕES AUXILIARES ---
def get_slot_from_world_pos(world_x, world_y):
    # Converte uma posição de pixel no mundo para uma coordenada de slot
    slot_col = world_x // SLOT_LARGURA_PX
    slot_row = world_y // SLOT_ALTURA_PX
    return slot_row, slot_col

# --- FUNÇÕES DE DESENHO ---
def desenhar_interface(game, selected_slot_type, pos_mouse):
    # (Código da interface da esquerda - sem grandes mudanças, apenas adiciona a loja de slots)
    y_painel=100
    # ... (código do estoque, pedidos, máquinas) ...
    y_painel+=15;TELA_JOGO.blit(FONTE_TITULO.render("Loja de Máquinas:",True,COR_TITULO),(20,y_painel));y_painel+=30
    botoes_loja_maquinas = []
    # ... (loop de botões de máquinas) ...

    # NOVA SEÇÃO: LOJA DE SLOTS
    y_painel+=15;TELA_JOGO.blit(FONTE_TITULO.render("Loja de Slots:",True,COR_TITULO),(20,y_painel));y_painel+=30
    botoes_loja_slots = []
    for tipo, dados in game.loja_slots.items():
        rect = pygame.Rect(20, y_painel, 360, 35)
        # Destaca o slot selecionado
        is_selected = tipo == selected_slot_type
        cor_borda = AMARELO_BRILHANTE if is_selected else COR_BOTAO_BORDA
        cor_botao = COR_BOTAO_HOVER if rect.collidepoint(pos_mouse) or is_selected else COR_BOTAO_NORMAL
        
        pygame.draw.rect(TELA_JOGO, cor_botao, rect)
        pygame.draw.rect(TELA_JOGO, cor_borda, rect, 2)
        texto = f"{tipo.capitalize()} | ${dados['custo']}"
        TELA_JOGO.blit(FONTE.render(texto, True, COR_TEXTO), (30, y_painel + 7))
        botoes_loja_slots.append((rect, tipo))
        y_painel += 45
    
    return botoes_loja_maquinas, botoes_loja_slots

def desenhar_mundo(game, jogador, caminhao, camera, mouse_world_pos, selected_slot_type):
    TELA_JOGO.fill(COR_FUNDO) # Limpa a tela

    # 1. Desenha os slots da fábrica (os que o jogador comprou)
    for (r, c), tipo_slot in game.owned_slots.items():
        if tipo_slot in IMG_FABRICA_TILES:
            slot_rect = pygame.Rect(c * SLOT_LARGURA_PX, r * SLOT_ALTURA_PX, SLOT_LARGURA_PX, SLOT_ALTURA_PX)
            TELA_JOGO.blit(IMG_FABRICA_TILES[tipo_slot], camera.apply_to_rect(slot_rect))

    # 2. Desenha os placeholders para compra de novos slots
    if selected_slot_type:
        # Pega a posição do mouse no grid de slots
        mouse_slot_r, mouse_slot_c = get_slot_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
        
        # Verifica se o local é adjacente e não comprado
        is_valid_spot = False
        if (mouse_slot_r, mouse_slot_c) not in game.owned_slots:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (mouse_slot_r + dr, mouse_slot_c + dc) in game.owned_slots:
                    is_valid_spot = True; break
        
        if is_valid_spot:
            placeholder_rect = pygame.Rect(mouse_slot_c * SLOT_LARGURA_PX, mouse_slot_r * SLOT_ALTURA_PX, SLOT_LARGURA_PX, SLOT_ALTURA_PX)
            # Cria uma surface semi-transparente para o placeholder
            s = pygame.Surface((SLOT_LARGURA_PX, SLOT_ALTURA_PX), pygame.SRCALPHA)
            s.fill((0, 255, 120, 100)) # Verde semi-transparente
            TELA_JOGO.blit(s, camera.apply_to_rect(placeholder_rect))

    # 3. Desenha o jogador e outros elementos do mundo
    TELA_JOGO.blit(jogador.animacoes[jogador.estado_atual][jogador.frame_atual], camera.apply_to_rect(jogador.rect))

# --- LÓGICA PRINCIPAL ---
def main():
    game = GameState()
    # Posição inicial do jogador no centro do slot inicial (0,0)
    start_pos_x = (0.5 * SLOT_LARGURA_PX)
    start_pos_y = (0.5 * SLOT_ALTURA_PX)
    jogador = Jogador(start_pos_x, start_pos_y, TAMANHO_CELULA)
    
    camera = Camera(JOGO_LARGURA, JOGO_ALTURA)
    caminhao = None # Caminhão pode ser adicionado depois
    
    direcao_x, direcao_y = 0, 0
    tempo_anterior = pygame.time.get_ticks()
    selected_slot_type = None # Mantém o controle de qual slot da loja está selecionado
    
    rodando = True
    while rodando:
        agora = pygame.time.get_ticks()
        decorrido = (agora - tempo_anterior) / 1000.0
        tempo_anterior = agora
        
        # --- LÓGICA DE EVENTOS ---
        pos_mouse_tela = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: rodando = False
            
            # Eventos de teclado
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_LEFT, pygame.K_a): direcao_x = -1
                elif evento.key in (pygame.K_RIGHT, pygame.K_d): direcao_x = 1
                elif evento.key in (pygame.K_UP, pygame.K_w): direcao_y = -1
                elif evento.key in (pygame.K_DOWN, pygame.K_s): direcao_y = 1
            if evento.type == pygame.KEYUP:
                if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d): direcao_x = 0
                elif evento.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s): direcao_y = 0

            # Eventos de Mouse
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Botão esquerdo
                    # Lógica para a interface (painel esquerdo)
                    if pos_mouse_tela[0] < 400:
                        b_maquinas, b_slots = desenhar_interface(game, selected_slot_type, pos_mouse_tela)
                        # Checa cliques nos botões da loja de slots
                        for rect, tipo in b_slots:
                            if rect.collidepoint(pos_mouse_tela):
                                selected_slot_type = tipo if selected_slot_type != tipo else None # Clicar de novo deseleciona
                    # Lógica para o mundo do jogo (área da fábrica)
                    else:
                        if selected_slot_type:
                            mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
                            slot_r, slot_c = get_slot_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
                            if game.expandir_fabrica(slot_r, slot_c, selected_slot_type):
                                selected_slot_type = None # Deseleciona após a compra

        # --- LÓGICA DE ATUALIZAÇÃO ---
        # Movimentação do jogador com colisão nos limites dos slots
        next_pos_x = jogador.rect.x + direcao_x * jogador.velocidade * decorrido
        next_pos_y = jogador.rect.y + direcao_y * jogador.velocidade * decorrido
        next_slot_r, next_slot_c = get_slot_from_world_pos(next_pos_x + jogador.rect.width / 2, next_pos_y + jogador.rect.height / 2)
        
        if (next_slot_r, next_slot_c) in game.owned_slots:
            jogador.update(direcao_x, direcao_y, decorrido, None) # None para limites, já que estamos checando manualmente
        else:
            jogador.update(0, 0, decorrido, None) # Para a animação
        
        camera.center_on(jogador.rect)

        # --- LÓGICA DE DESENHO ---
        mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
        desenhar_mundo(game, jogador, caminhao, camera, mouse_world_pos, selected_slot_type)
        desenhar_interface(game, selected_slot_type, pos_mouse_tela)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()