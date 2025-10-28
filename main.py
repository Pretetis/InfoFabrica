import pygame
import random
import sys

# --- CLASSES ---
from classes.game_state import GameState
from classes.jogador import Jogador
from classes.maquina import Maquina
from classes.caminhao import Caminhao

# --- CLASSE CAMERA ---
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
        return (screen_pos[0] + self.offset.x, screen_pos[1] + self.offset.y)

# --- Início do Código Principal ---
pygame.init()
# --- CONFIGURAÇÕES ---
JOGO_LARGURA, JOGO_ALTURA = 1800, 1000
TELA = pygame.display.set_mode((JOGO_LARGURA, JOGO_ALTURA), pygame.RESIZABLE)
TELA_JOGO = pygame.Surface((JOGO_LARGURA, JOGO_ALTURA))
pygame.display.set_caption("Jogo de Gestão com Logística")
COR_FUNDO=(30,30,40);COR_PAINEL=(45,45,55);COR_TEXTO=(220,220,220);COR_TITULO=(255,255,255);COR_FUNDO_EXTERNO=(10,10,10);COR_BOTAO_NORMAL=(70,70,80);COR_BOTAO_HOVER=(100,100,110);COR_BOTAO_BORDA=(130,130,140);VERDE_BRILHANTE=(0,255,120);VERMELHO_BRILHANTE=(255,80,80);AMARELO_BRILHANTE=(255,200,0)
FONTE=pygame.font.SysFont("monospace",18);FONTE_TITULO=pygame.font.SysFont("monospace",22,bold=True)
FONTE_PEQUENA = pygame.font.SysFont("monospace", 14, bold=True)
# --- NOVO: FONTE GRANDE PARA GAME OVER ---
FONTE_GAMEOVER = pygame.font.SysFont("monospace", 72, bold=True)


# --- CONFIGURAÇÕES DO GRID E SLOTS ---
TAMANHO_CELULA = 60
TAMANHO_MAQUINA_VISUAL = int(TAMANHO_CELULA * 1.2) # (72 pixels)
TAMANHO_ICONE_ITEM = 20 

SLOT_LARGURA_CELULAS = 7
SLOT_ALTURA_CELULAS = 5
SLOT_LARGURA_PX = SLOT_LARGURA_CELULAS * TAMANHO_CELULA
SLOT_ALTURA_PX = SLOT_ALTURA_CELULAS * TAMANHO_CELULA

# --- IMAGENS ---
IMG_MAQUINA_ESTATICA = pygame.transform.scale(pygame.image.load("assets/maquina.png").convert_alpha(), (TAMANHO_MAQUINA_VISUAL, TAMANHO_MAQUINA_VISUAL))
ANIMACAO_MAQUINA_M1 = [pygame.transform.scale(pygame.image.load(f"assets/maquinas/m1/m1{i}.png").convert_alpha(), (TAMANHO_MAQUINA_VISUAL, TAMANHO_MAQUINA_VISUAL)) for i in range(1, 4)]

try:
    IMG_CAMINHAO_LOGICA = pygame.image.load("assets/maquinas/caminhao/caminhao2.png").convert_alpha()
    IMG_CAMINHAO_LOGICA = pygame.transform.scale(IMG_CAMINHAO_LOGICA, (int(TAMANHO_CELULA * 4), int(TAMANHO_CELULA * 4)))
except Exception as e:
    print(f"Erro ao carregar caminhao2.png: {e}")
    IMG_CAMINHAO_LOGICA = pygame.Surface((TAMANHO_CELULA * 1.5, TAMANHO_CELULA * 1.5)) 

try:
    IMG_FAIXA = pygame.image.load("assets/fabrica/faixa.png").convert_alpha()
    IMG_FAIXA = pygame.transform.scale(IMG_FAIXA, (TAMANHO_CELULA, TAMANHO_CELULA)) 
except Exception as e:
    print(f"Erro ao carregar faixa.png: {e}")
    IMG_FAIXA = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA)) 

IMG_ITENS = {}
try:
    img_motor = pygame.image.load("assets/itens/engine.png").convert_alpha()
    IMG_ITENS["Motor V1"] = pygame.transform.scale(img_motor, (TAMANHO_ICONE_ITEM, TAMANHO_ICONE_ITEM))
    
    img_chassi = pygame.image.load("assets/itens/chassi.png").convert_alpha() 
    IMG_ITENS["Chassi Básico"] = pygame.transform.scale(img_chassi, (TAMANHO_ICONE_ITEM, TAMANHO_ICONE_ITEM))
    
except Exception as e:
    print(f"ERRO AO CARREGAR ÍCONES DE ITENS: {e}")

try:
    IMG_FABRICA_TILES = {
        "meio": pygame.image.load("assets/fabrica/meio.jpg").convert(),
        "superior": pygame.image.load("assets/fabrica/superior.jpg").convert(),
        "baixo": pygame.image.load("assets/fabrica/baixo.jpg").convert(),
        "esquerda": pygame.image.load("assets/fabrica/esquerda.jpg").convert(),
        "direita": pygame.image.load("assets/fabrica/direita.jpg").convert(),
        "doca": pygame.image.load("assets/fabrica/doca.jpg").convert(),
    }
    for key, img in IMG_FABRICA_TILES.items():
        IMG_FABRICA_TILES[key] = pygame.transform.scale(img, (SLOT_LARGURA_PX, SLOT_ALTURA_PX))
except Exception as e:
    print(f"Erro ao carregar tiles da fábrica: {e}"); IMG_FABRICA_TILES = None

# --- FUNÇÕES AUXILIARES ---
def get_slot_from_world_pos(world_x, world_y):
    slot_col = int(world_x // SLOT_LARGURA_PX)
    slot_row = int(world_y // SLOT_ALTURA_PX)
    return slot_row, slot_col

def get_cell_from_world_pos(world_x, world_y):
    cell_col = int(world_x // TAMANHO_CELULA)
    cell_row = int(world_y // TAMANHO_CELULA)
    return cell_row, cell_col

# --- FUNÇÕES DE DESENHO ---
def desenhar_interface(game, jogador, selected_slot_type, pos_mouse):
    TELA_JOGO.fill(COR_PAINEL, (0, 0, 400, JOGO_ALTURA))
    pygame.draw.rect(TELA_JOGO,COR_PAINEL,(0,0,JOGO_LARGURA,80))
    info=[f"Turno: {game.turno}",f"Tempo: {int(game.tempo_restante)}s",f"Dinheiro: ${game.dinheiro}",f"Reputação: {game.reputacao}"]
    for i, linha in enumerate(info): TELA_JOGO.blit(FONTE.render(linha, True, COR_TEXTO), (20 + i * 250, 30))
    y_painel=100
    
    TELA_JOGO.blit(FONTE_TITULO.render("Estoque (Global):",True,COR_TITULO),(20,y_painel));y_painel+=30
    if game.estoque:
        for k,v in game.estoque.items(): TELA_JOGO.blit(FONTE.render(f"{k}: {v}",True,COR_TEXTO),(30,y_painel)); y_painel+=20
    else: TELA_JOGO.blit(FONTE.render("Vazio",True,COR_TEXTO),(30,y_painel));y_painel+=20
    
    y_painel+=20
    carga_atual = sum(jogador.inventario.values())
    texto_inv = f"Inventário Jogador: ({carga_atual}/{jogador.carga_maxima})"
    TELA_JOGO.blit(FONTE_TITULO.render(texto_inv, True, COR_TITULO), (20, y_painel))
    y_painel += 30
    if jogador.inventario:
        for k,v in jogador.inventario.items(): 
            TELA_JOGO.blit(FONTE.render(f"{k}: {v}",True,COR_TEXTO),(30,y_painel)); y_painel+=20
    else: 
        TELA_JOGO.blit(FONTE.render("Vazio",True,COR_TEXTO),(30,y_painel));y_painel+=20

    y_painel+=20;TELA_JOGO.blit(FONTE_TITULO.render("Máquinas (Inventário):",True,COR_TITULO),(20,y_painel));y_painel+=30
    for maquina in game.maquinas: TELA_JOGO.blit(FONTE.render(f"- {maquina.tipo}",True,COR_TEXTO),(30,y_painel)); y_painel+=20
    
    y_painel+=15;TELA_JOGO.blit(FONTE_TITULO.render("Loja de Máquinas:",True,COR_TITULO),(20,y_painel));y_painel+=30
    botoes_loja_maquinas = []
    for i,modelo in enumerate(game.loja_maquinas):
        rect=pygame.Rect(20,y_painel,360,35)
        cor_botao=COR_BOTAO_HOVER if rect.collidepoint(pos_mouse) else COR_BOTAO_NORMAL
        pygame.draw.rect(TELA_JOGO,cor_botao,rect);pygame.draw.rect(TELA_JOGO,COR_BOTAO_BORDA,rect,2)
        TELA_JOGO.blit(FONTE.render(f"{modelo['tipo']} | P:{modelo['producao']} | ${modelo['custo']}",True,COR_TEXTO),(30,y_painel+7))
        botoes_loja_maquinas.append((rect,modelo));y_painel+=45
    
    y_painel+=15
    TELA_JOGO.blit(FONTE_TITULO.render("Pedidos Ativos:",True,COR_TITULO),(20,y_painel))
    y_painel+=30
    pedidos_ativos = [p for p in game.pedidos if not p.entregue]
    if pedidos_ativos:
        for pedido in pedidos_ativos:
            prazo_restante = pedido.prazo - game.turno
            
            # --- MODIFICADO: Cor do prazo (Vermelho se < 0)
            cor_prazo = COR_TEXTO
            if prazo_restante < 0:
                cor_prazo = VERMELHO_BRILHANTE
            elif prazo_restante <= 1: 
                cor_prazo = AMARELO_BRILHANTE
            
            x_pos = 30
            icon = IMG_ITENS.get(pedido.tipo)
            if icon:
                TELA_JOGO.blit(icon, (x_pos, y_painel))
                x_pos += TAMANHO_ICONE_ITEM + 5 
            
            # --- MODIFICADO: Texto do prazo
            texto_prazo = f"(Prazo: {prazo_restante} turnos)"
            if prazo_restante < 0:
                texto_prazo = "(ATRASADO)"
                
            texto = f"{pedido.quantidade}x {pedido.tipo} {texto_prazo}"
            pos_y_texto = y_painel + (TAMANHO_ICONE_ITEM // 2 - FONTE.get_height() // 2)
            if not icon: 
                pos_y_texto = y_painel
                
            TELA_JOGO.blit(FONTE.render(texto, True, cor_prazo),(x_pos, pos_y_texto))
            
            y_painel += TAMANHO_ICONE_ITEM + 5 
    else:
        TELA_JOGO.blit(FONTE.render("Nenhum pedido ativo",True,COR_TEXTO),(30,y_painel))
        y_painel+=20

    y_painel+=15;TELA_JOGO.blit(FONTE_TITULO.render("Loja de Slots:",True,COR_TITULO),(20,y_painel));y_painel+=30
    botoes_loja_slots = []
    for tipo, dados in game.loja_slots.items():
        rect = pygame.Rect(20, y_painel, 360, 35)
        is_selected = tipo == selected_slot_type
        cor_borda = AMARELO_BRILHANTE if is_selected else COR_BOTAO_BORDA
        cor_botao = COR_BOTAO_HOVER if rect.collidepoint(pos_mouse) or is_selected else COR_BOTAO_NORMAL
        pygame.draw.rect(TELA_JOGO, cor_botao, rect); pygame.draw.rect(TELA_JOGO, cor_borda, rect, 2)
        texto = f"{tipo.capitalize()} | ${dados['custo']}"
        TELA_JOGO.blit(FONTE.render(texto, True, COR_TEXTO), (30, y_painel + 7))
        botoes_loja_slots.append((rect, tipo))
        y_painel += 45
    return botoes_loja_maquinas, botoes_loja_slots

def desenhar_mundo(game, grid, grid_decoracoes, jogador, caminhao, camera, mouse_world_pos, selected_slot_type):
    TELA_JOGO.fill(COR_FUNDO)
    for (r, c), tipo_slot in game.owned_slots.items():
        if tipo_slot in IMG_FABRICA_TILES:
            slot_rect = pygame.Rect(c * SLOT_LARGURA_PX, r * SLOT_ALTURA_PX, SLOT_LARGURA_PX, SLOT_ALTURA_PX)
            TELA_JOGO.blit(IMG_FABRICA_TILES[tipo_slot], camera.apply_to_rect(slot_rect))
    
    for (r, c), img_faixa in grid_decoracoes.items():
        faixa_rect = pygame.Rect(c * TAMANHO_CELULA, r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
        TELA_JOGO.blit(img_faixa, camera.apply_to_rect(faixa_rect))

    for (r, c), maquinas_na_celula in grid.items():
        for idx, maquina in enumerate(maquinas_na_celula):
            offset_visual = idx * 5
            
            img_maquina = maquina.get_current_frame()
            if img_maquina is None:
                img_maquina = IMG_MAQUINA_ESTATICA 

            cell_center_x = (c * TAMANHO_CELULA) + (TAMANHO_CELULA / 2) + offset_visual
            cell_center_y = (r * TAMANHO_CELULA) + (TAMANHO_CELULA / 2) + offset_visual
            
            rect_maquina = img_maquina.get_rect(center=(cell_center_x, cell_center_y))
            
            TELA_JOGO.blit(img_maquina, camera.apply_to_rect(rect_maquina))

            icon = IMG_ITENS.get(maquina.tipo)
            
            if icon:
                TELA_LARGURA = 48
                TELA_ALTURA = 24
                pos_x_tela = rect_maquina.centerx - (TELA_LARGURA / 2)
                pos_y_tela = rect_maquina.top - 30 
                
                rect_tela = pygame.Rect(pos_x_tela, pos_y_tela, TELA_LARGURA, TELA_ALTURA)
                rect_tela_na_camera = camera.apply_to_rect(rect_tela)
                
                pygame.draw.rect(TELA_JOGO, COR_PAINEL, rect_tela_na_camera)
                pygame.draw.rect(TELA_JOGO, COR_BOTAO_BORDA, rect_tela_na_camera, 1)

                pos_x_icon = rect_tela.left + 2
                pos_y_icon = rect_tela.centery - (TAMANHO_ICONE_ITEM / 2)
                icon_rect = icon.get_rect(topleft=(pos_x_icon, pos_y_icon))
                TELA_JOGO.blit(icon, camera.apply_to_rect(icon_rect))

                if maquina.pecas_para_coletar > 0:
                    cor_texto_qtd = VERDE_BRILHANTE
                else:
                    cor_texto_qtd = COR_TEXTO 
                    
                texto_pecas = FONTE_PEQUENA.render(f"{maquina.pecas_para_coletar}", True, cor_texto_qtd)
                
                pos_x_texto = icon_rect.right + 4
                pos_y_texto = rect_tela.centery - (texto_pecas.get_height() / 2)
                
                TELA_JOGO.blit(texto_pecas, camera.apply_to_rect(pygame.Rect(pos_x_texto, pos_y_texto, texto_pecas.get_width(), texto_pecas.get_height())))

            elif maquina.pecas_para_coletar > 0:
                texto_pecas = FONTE.render(f"{maquina.pecas_para_coletar}", True, VERDE_BRILHANTE)
                pos_texto = (rect_maquina.centerx - texto_pecas.get_width() // 2, rect_maquina.top - 20)
                TELA_JOGO.blit(texto_pecas, camera.apply_to_rect(pygame.Rect(pos_texto, texto_pecas.get_size())))

    if selected_slot_type:
        mouse_slot_r, mouse_slot_c = get_slot_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
        is_valid_spot = False
        if (mouse_slot_r, mouse_slot_c) not in game.owned_slots:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (mouse_slot_r + dr, mouse_slot_c + dc) in game.owned_slots: is_valid_spot = True; break
        if is_valid_spot:
            placeholder_rect = pygame.Rect(mouse_slot_c * SLOT_LARGURA_PX, mouse_slot_r * SLOT_ALTURA_PX, SLOT_LARGURA_PX, SLOT_ALTURA_PX)
            s = pygame.Surface((SLOT_LARGURA_PX, SLOT_ALTURA_PX), pygame.SRCALPHA); s.fill((0, 255, 120, 100))
            TELA_JOGO.blit(s, camera.apply_to_rect(placeholder_rect))
    
    jogador.draw(TELA_JOGO, camera)

    if caminhao:
        caminhao.draw(TELA_JOGO, FONTE, camera)
    
def desenhar_tutorial(superficie):
    overlay = pygame.Surface((JOGO_LARGURA, JOGO_ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) 
    superficie.blit(overlay, (0, 0))
    
    painel_largura = 700
    painel_altura = 500
    painel_x = (JOGO_LARGURA / 2) - (painel_largura / 2)
    painel_y = (JOGO_ALTURA / 2) - (painel_altura / 2)
    painel_rect = pygame.Rect(painel_x, painel_y, painel_largura, painel_altura)
    pygame.draw.rect(superficie, COR_PAINEL, painel_rect)
    pygame.draw.rect(superficie, COR_BOTAO_BORDA, painel_rect, 3)

    def draw_text(texto, fonte, cor, x, y, center=False):
        superficie_texto = fonte.render(texto, True, cor)
        rect_texto = superficie_texto.get_rect()
        if center:
            rect_texto.center = (x, y)
        else:
            rect_texto.topleft = (x, y)
        superficie.blit(superficie_texto, rect_texto)

    draw_text("TUTORIAL - InfoFabrica", FONTE_TITULO, COR_TITULO, JOGO_LARGURA / 2, painel_y + 30, center=True)

    y_atalho = painel_y + 80
    x_atalho = painel_x + 30
    x_desc = painel_x + 230
    
    controles = [
        ("W, A, S, D:", "Mover o personagem"),
        ("E (na Máquina):", "Coletar peças (se houver)"),
        ("E (no Caminhão):", "Descarregar inventário no caminhão"),
        ("T:", "Encerrar o turno e enviar o caminhão"),
        ("M:", "Colocar máquina do inventário no chão"),
        ("F:", "Colocar/Remover faixa de sinalização"),
        ("Mouse (na Loja):", "Comprar máquinas e expandir a fábrica"),
        ("H:", "Fechar esta tela de ajuda")
    ]
    
    for atalho, desc in controles:
        draw_text(atalho, FONTE_TITULO, AMARELO_BRILHANTE, x_atalho, y_atalho)
        draw_text(desc, FONTE, COR_TEXTO, x_desc, y_atalho + 3) 
        y_atalho += 40

    draw_text("Objetivo:", FONTE_TITULO, COR_TITULO, x_atalho, y_atalho + 20)
    draw_text("Use as máquinas para produzir itens, carregue-os no", FONTE, COR_TEXTO, x_atalho, y_atalho + 50)
    draw_text("caminhão e envie-o (tecla T) para completar os pedidos!", FONTE, COR_TEXTO, x_atalho, y_atalho + 70)


# --- NOVO: FUNÇÃO PARA DESENHAR TELA DE GAME OVER ---
def desenhar_game_over(superficie):
    # 1. Overlay semi-transparente (vermelho)
    overlay = pygame.Surface((JOGO_LARGURA, JOGO_ALTURA), pygame.SRCALPHA)
    overlay.fill((150, 0, 0, 180)) # Cor vermelha com 180 de alpha
    superficie.blit(overlay, (0, 0))
    
    # 2. Textos
    def draw_text(texto, fonte, cor, x, y, center=False):
        superficie_texto = fonte.render(texto, True, cor)
        rect_texto = superficie_texto.get_rect()
        if center:
            rect_texto.center = (x, y)
        else:
            rect_texto.topleft = (x, y)
        superficie.blit(superficie_texto, rect_texto)

    # Título
    draw_text("GAME OVER", FONTE_GAMEOVER, VERMELHO_BRILHANTE, JOGO_LARGURA / 2, JOGO_ALTURA / 2 - 50, center=True)
    
    # Subtítulo
    draw_text("Sua reputação caiu muito e a fábrica faliu.", FONTE_TITULO, COR_TEXTO, JOGO_LARGURA / 2, JOGO_ALTURA / 2 + 30, center=True)
    draw_text("Pressione ESC para sair.", FONTE, COR_TEXTO, JOGO_LARGURA / 2, JOGO_ALTURA / 2 + 70, center=True)


# --- LÓGICA PRINCIPAL ---
def main():
    game = GameState()
    grid_maquinas = {}
    grid_decoracoes = {} 
    
    camera = Camera(JOGO_LARGURA, JOGO_ALTURA)
    caminhao = None
    start_pos_x, start_pos_y = (0.5 * SLOT_LARGURA_PX), (0.5 * SLOT_ALTURA_PX) 

    doca_slot_r, doca_slot_c = None, None
    for (r, c), tipo in game.owned_slots.items():
        if tipo == 'doca':
            doca_slot_r, doca_slot_c = r, c
            break
    
    if doca_slot_r is not None:
        pos_caminhao_x = (doca_slot_c * SLOT_LARGURA_PX) + (SLOT_LARGURA_PX / 2)
        pos_caminhao_y = (doca_slot_r * SLOT_ALTURA_PX) + (SLOT_ALTURA_PX / 2)
        caminhao = Caminhao(pos_caminhao_x, pos_caminhao_y, IMG_CAMINHAO_LOGICA, SLOT_ALTURA_PX)
        
        start_pos_x = pos_caminhao_x
        start_pos_y = caminhao.area_carga.bottom + 30
    
    jogador = Jogador(start_pos_x, start_pos_y, TAMANHO_CELULA)
    
    direcao_x, direcao_y = 0, 0
    tempo_anterior = pygame.time.get_ticks()
    selected_slot_type = None
    rodando = True
    
    # Inicia com tutorial
    mostrando_tutorial = True
    
    while rodando:
        agora = pygame.time.get_ticks()
        decorrido = (agora - tempo_anterior) / 1000.0
        tempo_anterior = agora
        pos_mouse_tela = pygame.mouse.get_pos()
        
        # --- LÓGICA DE EVENTOS (MODIFICADA PARA GAME OVER) ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: rodando = False
            
            # --- Se o tutorial estiver aberto, só processa 'H' ---
            if mostrando_tutorial:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_h:
                        mostrando_tutorial = False
            
            # --- Se for Game Over, só processa 'ESC' para sair ---
            elif game.estado_jogo == 'GAME_OVER':
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        rodando = False # Fecha o jogo
            
            # --- Se o jogo estiver rodando normalmente ---
            elif not mostrando_tutorial and game.estado_jogo != 'GAME_OVER':
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_LEFT, pygame.K_a): direcao_x = -1
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d): direcao_x = 1
                    elif evento.key in (pygame.K_UP, pygame.K_w): direcao_y = -1
                    elif evento.key in (pygame.K_DOWN, pygame.K_s): direcao_y = 1
                    
                    if evento.key == pygame.K_h:
                        mostrando_tutorial = True
                        direcao_x, direcao_y = 0, 0 
                    
                    if evento.key == pygame.K_e: 
                        if caminhao and caminhao.estado == 'PARADO' and jogador.rect.colliderect(caminhao.area_carga):
                            if jogador.inventario:
                                for tipo, qtd in jogador.inventario.items():
                                    caminhao.receber_carga(tipo, qtd)
                                print(f"Descarregou {jogador.inventario} no caminhão.")
                                jogador.inventario.clear()
                            else:
                                print("Inventário vazio, nada para descarregar.")
                        
                        else:
                            cell_r, cell_c = get_cell_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                            if (cell_r, cell_c) in grid_maquinas:
                                maquina_na_celula = grid_maquinas[(cell_r, cell_c)][0] 
                                
                                if maquina_na_celula.pecas_para_coletar > 0:
                                    carga_atual_jogador = sum(jogador.inventario.values())
                                    espaco_livre = jogador.carga_maxima - carga_atual_jogador
                                    
                                    if espaco_livre > 0:
                                        tipo_peca = maquina_na_celula.tipo
                                        
                                        if not jogador.inventario or tipo_peca in jogador.inventario:
                                            quantidade_a_pegar = min(maquina_na_celula.pecas_para_coletar, espaco_livre)
                                            
                                            jogador.inventario[tipo_peca] = jogador.inventario.get(tipo_peca, 0) + quantidade_a_pegar
                                            maquina_na_celula.pecas_para_coletar -= quantidade_a_pegar
                                            
                                            print(f"Pegou {quantidade_a_pegar}x {tipo_peca}. Máquina agora tem {maquina_na_celula.pecas_para_coletar}.")
                                        else:
                                            print("Inventário cheio ou com item de outro tipo! Esvazie no caminhão.")
                                    else:
                                        print("Inventário do jogador está cheio!")
                                else:
                                    print("Máquina vazia, aguardando produção.")
                    
                    if evento.key == pygame.K_t:
                        if caminhao and caminhao.estado == 'PARADO':
                            caminhao.iniciar_partida()
                            game.estado_jogo = 'CAMINHAO_PARTINDO' 
                            print("Turno encerrado manually! Caminhão partindo...")

                    if evento.key == pygame.K_f:
                        cell_r, cell_c = get_cell_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                        mouse_world_pos_jogador = (jogador.rect.centerx, jogador.rect.centery)
                        slot_r, slot_c = get_slot_from_world_pos(mouse_world_pos_jogador[0], mouse_world_pos_jogador[1])

                        if (slot_r, slot_c) in game.owned_slots:
                            if (cell_r, cell_c) in grid_decoracoes:
                                del grid_decoracoes[(cell_r, cell_c)]
                                print(f"Faixa removida de {cell_r, cell_c}")
                            else:
                                grid_decoracoes[(cell_r, cell_c)] = IMG_FAIXA
                                print(f"Faixa colocada em {cell_r, cell_c}")
                    
                    if evento.key == pygame.K_m and game.maquinas:
                        cell_r, cell_c = get_cell_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                        slot_r, slot_c = get_slot_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                        
                        if (slot_r, slot_c) in game.owned_slots:
                            if game.owned_slots.get((slot_r, slot_c)) != 'doca':
                                maquina_a_colocar = game.maquinas.pop(0)
                                
                                if (cell_r, cell_c) not in grid_maquinas:
                                    grid_maquinas[(cell_r, cell_c)] = []
                                
                                grid_maquinas[(cell_r, cell_c)].append(maquina_a_colocar)
                                print(f"Máquina colocada em {cell_r, cell_c}")
                            else:
                                print("Não pode colocar máquinas na doca.")

                if evento.type == pygame.KEYUP:
                    if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d): direcao_x = 0
                    elif evento.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s): direcao_y = 0
                
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if pos_mouse_tela[0] < 400:
                        b_maquinas, b_slots = desenhar_interface(game, jogador, selected_slot_type, pos_mouse_tela)
                        for rect, tipo in b_slots:
                            if rect.collidepoint(pos_mouse_tela): selected_slot_type = tipo if selected_slot_type != tipo else None
                        
                        for rect, modelo in b_maquinas:
                            if rect.collidepoint(pos_mouse_tela) and game.dinheiro >= modelo["custo"]:
                                game.dinheiro -= modelo['custo']
                                nova_maquina = Maquina(modelo["tipo"],modelo["producao"],modelo["custo"],modelo.get("custo_energia", 10),1,1,animacao=ANIMACAO_MAQUINA_M1)
                                game.maquinas.append(nova_maquina)
                                print(f"Máquina '{modelo['tipo']}' comprada e adicionada ao inventário!")
                    else:
                        if selected_slot_type:
                            mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
                            slot_r, slot_c = get_slot_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
                            if game.expandir_fabrica(slot_r, slot_c, selected_slot_type): selected_slot_type = None

        # --- LÓGICA DE ATUALIZAÇÃO (MODIFICADA PARA PAUSAR) ---
        # Só atualiza o jogo se o tutorial NÃO estiver sendo exibido E NÃO for game over
        if not mostrando_tutorial and game.estado_jogo != 'GAME_OVER':
            if game.estado_jogo == 'JOGANDO':
                
                game.tempo_restante -= decorrido

                if game.tempo_restante <= 0:
                    game.tempo_restante = 0 
                    
                    if caminhao and caminhao.estado == 'PARADO':
                        caminhao.iniciar_partida()
                        game.estado_jogo = 'CAMINHAO_PARTINDO' 
                        print("Tempo esgotado! Caminhão partindo...")
                
                if game.estado_jogo == 'JOGANDO': 
                    next_pos_x = jogador.pos_x_px + direcao_x * jogador.velocidade * decorrido
                    next_pos_y = jogador.pos_y_px + direcao_y * jogador.velocidade * decorrido
                    next_slot_r, next_slot_c = get_slot_from_world_pos(next_pos_x, next_pos_y)
                    
                    if (next_slot_r, next_slot_c) in game.owned_slots:
                        jogador.update(direcao_x, direcao_y, decorrido)
                    else:
                        jogador.update(0, 0, decorrido) 
            else:
                 jogador.update(0, 0, decorrido) 
            
            camera.center_on(jogador.rect)

            if game.estado_jogo == 'JOGANDO':
                for (r, c), maquinas_na_celula in grid_maquinas.items():
                    for maquina in maquinas_na_celula:
                        maquina.update_animation(decorrido)

            if caminhao:
                caminhao.update(decorrido, game, grid_maquinas)
        
        else:
            # Se o tutorial ou game over estiverem ativos, força o jogador a parar
            jogador.update(0, 0, decorrido)


        # --- LÓGICA DE DESENHO (MODIFICADA) ---
        mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
        
        # 1. Desenha o mundo e a interface (sempre)
        desenhar_mundo(game, grid_maquinas, grid_decoracoes, jogador, caminhao, camera, mouse_world_pos, selected_slot_type)
        desenhar_interface(game, jogador, selected_slot_type, pos_mouse_tela)
        
        # 2. Desenha o Tutorial (se ativo)
        if mostrando_tutorial:
            desenhar_tutorial(TELA_JOGO)
            
        # 3. Desenha o Game Over (se ativo)
        elif game.estado_jogo == 'GAME_OVER':
            desenhar_game_over(TELA_JOGO)
            
        # 4. Atualiza a tela final
        TELA.blit(TELA_JOGO, (0,0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()