import pygame
import random
import sys

# --- CLASSES ---
from classes.game_state import GameState
from classes.jogador import Jogador
from classes.maquina import Maquina
from classes.caminhao import Caminhao

# ... (Logo após as cores e antes das configurações de grid)
DEBUG_COLISAO = True  # Mude para False para esconder as linhas vermelhas

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
# TAMANHO_MAQUINA_VISUAL = int(TAMANHO_CELULA * 1.2) # (72 pixels)

TAMANHO_M1_VISUAL = (int(TAMANHO_CELULA * 1.2), int(TAMANHO_CELULA * 1.2)) # (72, 72) - Quadrada
TAMANHO_M2_VISUAL = (int(TAMANHO_CELULA * 1.8), int(TAMANHO_CELULA * 1.2)) # (108, 72) - Larga (Braço Robótico)
TAMANHO_M3_VISUAL = (int(TAMANHO_CELULA * 1.6), int(TAMANHO_CELULA * 2.2)) # (72, 108) - Alta (Torre)

TAMANHO_ICONE_ITEM = 20 

SLOT_LARGURA_CELULAS = 7
SLOT_ALTURA_CELULAS = 5
SLOT_LARGURA_PX = SLOT_LARGURA_CELULAS * TAMANHO_CELULA
SLOT_ALTURA_PX = SLOT_ALTURA_CELULAS * TAMANHO_CELULA

# --- IMAGENS ---
# IMG_MAQUINA_ESTATICA = pygame.transform.scale(pygame.image.load("assets/maquina.png").convert_alpha(), (TAMANHO_MAQUINA_VISUAL, TAMANHO_MAQUINA_VISUAL))
# ANIMACAO_MAQUINA_M1 = [pygame.transform.scale(pygame.image.load(f"assets/maquinas/m1/m1{i}.png").convert_alpha(), (TAMANHO_MAQUINA_VISUAL, TAMANHO_MAQUINA_VISUAL)) for i in range(1, 4)]


# M1 (Fábrica de Motor)
ANIMACAO_MAQUINA_M1 = [pygame.transform.smoothscale(pygame.image.load(f"assets/maquinas/m1/m1{i}.png").convert_alpha(), TAMANHO_M1_VISUAL) for i in range(1, 4)]

# NOVO: M2 (Fábrica de Chassi)
ANIMACAO_MAQUINA_M2 = [pygame.transform.smoothscale(pygame.image.load(f"assets/maquinas/m2/m2{i}.png").convert_alpha(), TAMANHO_M2_VISUAL) for i in range(1, 4)]

# NOVO: M3 (Fábrica de Motor Rápida)
ANIMACAO_MAQUINA_M3 = [pygame.transform.smoothscale(pygame.image.load(f"assets/maquinas/m3/m3{i}.png").convert_alpha(), TAMANHO_M3_VISUAL) for i in range(1, 4)]

ANIMACAO_MAQUINAS_VISUAIS = {
    "M1": ANIMACAO_MAQUINA_M1,
    "M2": ANIMACAO_MAQUINA_M2,
    "M3": ANIMACAO_MAQUINA_M3,
}

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
def desenhar_interface(game, jogador, selected_slot_type, pos_mouse, maquina_para_colocar):
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

    y_painel+=20

    # --- LOJA (MÁQUINAS E SLOTS) ---
    TELA_JOGO.blit(FONTE_TITULO.render("Loja:",True,COR_TITULO),(20,y_painel));y_painel+=30

    botoes_loja_maquinas = []
    
    # 1. Desenha MÁQUINAS
    for i,modelo in enumerate(game.loja_maquinas):
        rect=pygame.Rect(20,y_painel,360,35)
        
        is_selected = (maquina_para_colocar is not None and maquina_para_colocar.custo == modelo['custo'] and maquina_para_colocar.tipo == modelo['tipo'])
        cor_borda = AMARELO_BRILHANTE if is_selected else COR_BOTAO_BORDA
        cor_botao=COR_BOTAO_HOVER if rect.collidepoint(pos_mouse) or is_selected else COR_BOTAO_NORMAL
        
        pygame.draw.rect(TELA_JOGO,cor_botao,rect);pygame.draw.rect(TELA_JOGO,cor_borda,rect,2)
        
        nome_maquina = modelo.get('nome', modelo['tipo'])
        prod_texto = "Multi" if isinstance(modelo['producao'], dict) else modelo['producao']
        texto_botao = f"{nome_maquina} | P:{prod_texto} | ${modelo['custo']}"
        TELA_JOGO.blit(FONTE.render(texto_botao,True,COR_TEXTO),(30,y_painel+7))

        botoes_loja_maquinas.append((rect,modelo));y_painel+=45

    # 2. Desenha SLOTS
    botoes_loja_slots = []
    for tipo, dados in game.loja_slots.items():
        rect = pygame.Rect(20, y_painel, 360, 35)
        is_selected = tipo == selected_slot_type
        cor_borda = AMARELO_BRILHANTE if is_selected else COR_BOTAO_BORDA
        cor_botao = COR_BOTAO_HOVER if rect.collidepoint(pos_mouse) or is_selected else COR_BOTAO_NORMAL
        
        pygame.draw.rect(TELA_JOGO, cor_botao, rect); pygame.draw.rect(TELA_JOGO, cor_borda, rect, 2)
        
        texto = f"Expandir Fábrica ({tipo.capitalize()}) | ${dados['custo']}"
        TELA_JOGO.blit(FONTE.render(texto, True, COR_TEXTO), (30, y_painel + 7))
        
        botoes_loja_slots.append((rect, tipo))
        y_painel += 45
    
    y_painel+=15
    TELA_JOGO.blit(FONTE_TITULO.render("Pedidos Ativos:",True,COR_TITULO),(20,y_painel))

    y_painel+=30
    
    # --- LÓGICA DE EXIBIÇÃO DE PEDIDOS (MODIFICADA) ---
    pedidos_visiveis = game.pedidos 
    if pedidos_visiveis:
        for pedido in pedidos_visiveis:
            # SE O PEDIDO FALHOU (PENALIZADO), NÃO DESENHA (SOME DA TELA)
            if pedido.penalizado:
                continue 
            
            prazo_restante = pedido.prazo - game.turno
            
            # Cores e Status
            cor_prazo = COR_TEXTO
            texto_status = f"(Prazo: {prazo_restante})"
            
            if pedido.entregue:
                cor_prazo = VERDE_BRILHANTE
                texto_status = "(ENTREGUE)"
            elif prazo_restante < 0: 
                # Caso raro onde atrasou mas ainda não foi processada a penalidade
                cor_prazo = VERMELHO_BRILHANTE
                texto_status = "(ATRASADO)"
            elif prazo_restante <= 1: 
                cor_prazo = AMARELO_BRILHANTE
            
            x_pos = 30
            icon = IMG_ITENS.get(pedido.tipo)
            if icon:
                TELA_JOGO.blit(icon, (x_pos, y_painel))
                x_pos += TAMANHO_ICONE_ITEM + 5 
            
            texto = f"{pedido.quantidade}x {pedido.tipo} {texto_status}"
            pos_y_texto = y_painel + (TAMANHO_ICONE_ITEM // 2 - FONTE.get_height() // 2)
            if not icon: pos_y_texto = y_painel
                
            TELA_JOGO.blit(FONTE.render(texto, True, cor_prazo),(x_pos, pos_y_texto))
            y_painel += TAMANHO_ICONE_ITEM + 5 
    else:
        TELA_JOGO.blit(FONTE.render("Nenhum pedido ativo",True,COR_TEXTO),(30,y_painel))
        y_painel+=20

    return botoes_loja_maquinas, botoes_loja_slots, None

def desenhar_mundo(game, grid, grid_decoracoes, jogador, caminhao, camera, mouse_world_pos, selected_slot_type, maquina_para_colocar):
    TELA_JOGO.fill(COR_FUNDO)
    
    # 1. Desenha o Chão
    for (r, c), tipo_slot in game.owned_slots.items():
        if tipo_slot in IMG_FABRICA_TILES:
            slot_rect = pygame.Rect(c * SLOT_LARGURA_PX, r * SLOT_ALTURA_PX, SLOT_LARGURA_PX, SLOT_ALTURA_PX)
            TELA_JOGO.blit(IMG_FABRICA_TILES[tipo_slot], camera.apply_to_rect(slot_rect))
    
    for (r, c), img_faixa in grid_decoracoes.items():
        faixa_rect = pygame.Rect(c * TAMANHO_CELULA, r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
        TELA_JOGO.blit(img_faixa, camera.apply_to_rect(faixa_rect))

    # --- LISTA DE RENDERIZAÇÃO (Y-SORT) ---
    objetos_para_desenhar = []

    # A. Adiciona o JOGADOR
    objetos_para_desenhar.append({
        'tipo': 'jogador',
        'y_sort': jogador.rect.bottom,
        'obj': jogador
    })

    # B. Adiciona as MÁQUINAS
    for (r, c), maquinas_na_celula in grid.items():
        for idx, maquina in enumerate(maquinas_na_celula):
            offset_visual = idx * 5
            
            img_maquina = maquina.get_current_frame()
            
            # Centraliza visualmente
            cx = (c * TAMANHO_CELULA) + (TAMANHO_CELULA / 2) + offset_visual
            cy = (r * TAMANHO_CELULA) + (TAMANHO_CELULA / 2) + offset_visual
            rect_maquina_visual = img_maquina.get_rect(center=(cx, cy))
            
            # Y-Sort baseado na base da CÉLULA
            y_base_celula = ((r + 1) * TAMANHO_CELULA)
            
            objetos_para_desenhar.append({
                'tipo': 'maquina',
                'y_sort': y_base_celula, 
                'obj': maquina,
                'img': img_maquina,
                'rect_visual': rect_maquina_visual, # Retângulo da IMAGEM
                'grid_pos': (r, c) # Guardamos a posição na grade para o Debug
            })

    # C. ORDENA E DESENHA
    objetos_para_desenhar.sort(key=lambda item: item['y_sort'])

    for item in objetos_para_desenhar:
        if item['tipo'] == 'jogador':
            jogador_obj = item['obj']
            jogador_obj.draw(TELA_JOGO, camera)
            
            # --- DEBUG HITBOX JOGADOR (CIANO) ---
            if DEBUG_COLISAO:
                # Desenha a hitbox exata usada na lógica (levemente mais estreita)
                hitbox_player = jogador_obj.rect.inflate(0, -10)
                pygame.draw.rect(TELA_JOGO, (0, 255, 255), camera.apply_to_rect(hitbox_player), 1)
            
        elif item['tipo'] == 'maquina':
            # Desenha a Máquina
            maquina = item['obj']
            rect_visual = item['rect_visual']
            TELA_JOGO.blit(item['img'], camera.apply_to_rect(rect_visual))

            # --- DEBUG HITBOX MÁQUINA (VERMELHO) ---
            if DEBUG_COLISAO:
                r, c = item['grid_pos']
                # Recria exatamente o retângulo usado na lógica de colisão
                rect_base_celula = pygame.Rect(c * TAMANHO_CELULA, r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
                hitbox_real = rect_base_celula.inflate(-10, -10)
                
                # Desenha o contorno vermelho
                pygame.draw.rect(TELA_JOGO, (255, 0, 0), camera.apply_to_rect(hitbox_real), 1)

            # --- LÓGICA DE ÍCONES (Mantida igual) ---
            y_offset_item = 0 
            for item_tipo, pecas_count in maquina.pecas_para_coletar.items():
                icon = IMG_ITENS.get(item_tipo)
                if icon:
                    TELA_LARGURA, TELA_ALTURA = 48, 24
                    pos_x_tela = rect_visual.centerx - (TELA_LARGURA / 2)
                    pos_y_tela = rect_visual.top - 30 - y_offset_item 
                    
                    rect_tela = pygame.Rect(pos_x_tela, pos_y_tela, TELA_LARGURA, TELA_ALTURA)
                    rect_tela_na_camera = camera.apply_to_rect(rect_tela)
                    
                    pygame.draw.rect(TELA_JOGO, COR_PAINEL, rect_tela_na_camera)
                    pygame.draw.rect(TELA_JOGO, COR_BOTAO_BORDA, rect_tela_na_camera, 1)

                    pos_x_icon = rect_tela.left + 2
                    pos_y_icon = rect_tela.centery - (TAMANHO_ICONE_ITEM / 2)
                    icon_rect = icon.get_rect(topleft=(pos_x_icon, pos_y_icon))
                    TELA_JOGO.blit(icon, camera.apply_to_rect(icon_rect))

                    cor_texto_qtd = VERDE_BRILHANTE if pecas_count > 0 else COR_TEXTO
                    texto_pecas = FONTE_PEQUENA.render(f"{pecas_count}", True, cor_texto_qtd)
                    
                    pos_x_texto = icon_rect.right + 4
                    pos_y_texto = rect_tela.centery - (texto_pecas.get_height() / 2)
                    TELA_JOGO.blit(texto_pecas, camera.apply_to_rect(pygame.Rect(pos_x_texto, pos_y_texto, texto_pecas.get_width(), texto_pecas.get_height())))
                    y_offset_item += TELA_ALTURA + 2 
                elif pecas_count > 0: 
                    texto_pecas = FONTE.render(f"{pecas_count}x {item_tipo}", True, VERDE_BRILHANTE)
                    pos_texto = (rect_visual.centerx - texto_pecas.get_width() // 2, rect_visual.top - 20 - y_offset_item)
                    TELA_JOGO.blit(texto_pecas, camera.apply_to_rect(pygame.Rect(pos_texto, texto_pecas.get_size())))
                    y_offset_item += 20

    # --- FANTASMA DE COLOCAÇÃO ---
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

    if maquina_para_colocar:
        mouse_cell_r, mouse_cell_c = get_cell_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
        img_maquina = maquina_para_colocar.get_current_frame()
        if img_maquina:
            cx = (mouse_cell_c * TAMANHO_CELULA) + (TAMANHO_CELULA / 2)
            cy = (mouse_cell_r * TAMANHO_CELULA) + (TAMANHO_CELULA / 2)
            rect_fantasma = img_maquina.get_rect(center=(cx, cy))
            
            celula_ocupada = (mouse_cell_r, mouse_cell_c) in grid and grid.get((mouse_cell_r, mouse_cell_c))
            s = img_maquina.copy()
            if celula_ocupada: s.fill((255, 50, 50, 180), special_flags=pygame.BLEND_RGBA_MULT)
            else: s.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
            TELA_JOGO.blit(s, camera.apply_to_rect(rect_fantasma))

            # Debug Fantasma (Opcional)
            if DEBUG_COLISAO:
                 # Mostra onde a colisão vai ficar
                 rect_base_fantasma = pygame.Rect(mouse_cell_c * TAMANHO_CELULA, mouse_cell_r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
                 pygame.draw.rect(TELA_JOGO, (255, 255, 0), camera.apply_to_rect(rect_base_fantasma), 1)

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
    # Posição inicial padrão caso não ache doca
    start_pos_x, start_pos_y = (0.5 * SLOT_LARGURA_PX), (0.5 * SLOT_ALTURA_PX) 

    # Procura onde está a doca para posicionar o caminhão e o jogador
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
    maquina_para_colocar = None
    
    # Inicia com tutorial
    mostrando_tutorial = True
    
    while rodando:
        agora = pygame.time.get_ticks()
        decorrido = (agora - tempo_anterior) / 1000.0
        tempo_anterior = agora
        pos_mouse_tela = pygame.mouse.get_pos()
        
        # --- LÓGICA DE EVENTOS ---
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
                        # Interação com Caminhão
                        if caminhao and caminhao.estado == 'PARADO' and jogador.rect.colliderect(caminhao.area_carga):
                            if jogador.inventario:
                                for tipo, qtd in jogador.inventario.items():
                                    caminhao.receber_carga(tipo, qtd)
                                print(f"Descarregou {jogador.inventario} no caminhão.")
                                jogador.inventario.clear()
                            else:
                                print("Inventário vazio, nada para descarregar.")
                        
                        else: 
                            # Interação com Máquina (Coleta)
                            cell_r, cell_c = get_cell_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                            if (cell_r, cell_c) in grid_maquinas:
                                maquina_na_celula = grid_maquinas[(cell_r, cell_c)][0] 
                                
                                # Lógica de coleta inteligente
                                tipo_para_coletar = None
                                if jogador.inventario:
                                    tipo_para_coletar = list(jogador.inventario.keys())[0]
                                else:
                                    for item_tipo, qtd in maquina_na_celula.pecas_para_coletar.items():
                                        if qtd > 0:
                                            tipo_para_coletar = item_tipo
                                            break 
                                
                                if tipo_para_coletar is None:
                                    print("Máquina vazia ou jogador com inventário incompatível.")
                                elif maquina_na_celula.pecas_para_coletar.get(tipo_para_coletar, 0) > 0:
                                    carga_atual_jogador = sum(jogador.inventario.values())
                                    espaco_livre = jogador.carga_maxima - carga_atual_jogador
                                    
                                    if espaco_livre > 0:
                                        quantidade_na_maquina = maquina_na_celula.pecas_para_coletar[tipo_para_coletar]
                                        quantidade_a_pegar = min(quantidade_na_maquina, espaco_livre)
                                        
                                        jogador.inventario[tipo_para_coletar] = jogador.inventario.get(tipo_para_coletar, 0) + quantidade_a_pegar
                                        maquina_na_celula.pecas_para_coletar[tipo_para_coletar] -= quantidade_a_pegar
                                        print(f"Pegou {quantidade_a_pegar}x {tipo_para_coletar}.")
                                    else:
                                        print("Inventário do jogador está cheio!")
                                else:
                                    print(f"Máquina não tem '{tipo_para_coletar}' para coletar.")
                    
                    if evento.key == pygame.K_t:
                        if caminhao and caminhao.estado == 'PARADO':
                            caminhao.iniciar_partida()
                            game.estado_jogo = 'CAMINHAO_PARTINDO' 
                            print("Turno encerrado manualmente! Caminhão partindo...")

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
                
                if evento.type == pygame.KEYUP:
                    if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d): direcao_x = 0
                    elif evento.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s): direcao_y = 0
                
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    
                    # --- Botão Direito: CANCELAR AÇÕES ---
                    if evento.button == 3: 
                        if maquina_para_colocar:
                            maquina_para_colocar = None
                            print("Modo de colocação cancelado.")
                        if selected_slot_type:
                            selected_slot_type = None
                            print("Seleção de slot cancelada.")

                    # --- Botão Esquerdo: AÇÕES PRINCIPAIS ---
                    if evento.button == 1:
                        if pos_mouse_tela[0] < 400: # Clicou no PAINEL ESQUERDO
                            
                            # Atualiza interface e pega cliques
                            b_maquinas, b_slots, _ = desenhar_interface(game, jogador, selected_slot_type, pos_mouse_tela, maquina_para_colocar)
                            
                            # Lógica da Loja de Slots
                            for rect, tipo in b_slots:
                                if rect.collidepoint(pos_mouse_tela):
                                    selected_slot_type = tipo if selected_slot_type != tipo else None
                                    maquina_para_colocar = None 

                            # Lógica da Loja de Máquinas
                            for rect, modelo in b_maquinas:
                                if rect.collidepoint(pos_mouse_tela):
                                    if game.dinheiro >= modelo['custo']:
                                        anim_key = modelo.get("anim_key", "M1") 
                                        animacao_maquina = ANIMACAO_MAQUINAS_VISUAIS.get(anim_key)
                                        
                                        nova_maquina = Maquina(
                                            modelo["tipo"], modelo["producao"], modelo["custo"],
                                            modelo.get("custo_energia", 10), 1, 1,
                                            animacao=animacao_maquina
                                        )
                                        
                                        maquina_para_colocar = nova_maquina
                                        selected_slot_type = None
                                        print(f"Selecionado para compra: {modelo.get('nome', modelo['tipo'])}")
                                    else:
                                        print("Dinheiro insuficiente para esta máquina!")
                                    
                        else: # Clicou no MUNDO (direita do painel)
                            mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
                            
                            # 1. Tentar Colocar Máquina
                            if maquina_para_colocar:
                                cell_r, cell_c = get_cell_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
                                slot_r, slot_c = get_slot_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
                                
                                # Verifica slot válido
                                if (slot_r, slot_c) in game.owned_slots and game.owned_slots.get((slot_r, slot_c)) != 'doca':
                                    
                                    # Verifica LIMITE de máquinas
                                    maquinas_no_slot_atual = 0
                                    for (m_cell_r, m_cell_c) in grid_maquinas.keys():
                                        m_slot_r = int(m_cell_r * TAMANHO_CELULA // SLOT_ALTURA_PX)
                                        m_slot_c = int(m_cell_c * TAMANHO_CELULA // SLOT_LARGURA_PX)
                                        if m_slot_r == slot_r and m_slot_c == slot_c:
                                            maquinas_no_slot_atual += 1
                                    
                                    LIMIT_MAQUINAS_POR_SLOT = 5

                                    if maquinas_no_slot_atual >= LIMIT_MAQUINAS_POR_SLOT:
                                        print(f"Slot cheio! Limite de {LIMIT_MAQUINAS_POR_SLOT} máquinas.")
                                    
                                    # Verifica se célula está livre
                                    elif not ((cell_r, cell_c) in grid_maquinas and grid_maquinas[(cell_r, cell_c)]):
                                        if game.dinheiro >= maquina_para_colocar.custo:
                                            game.dinheiro -= maquina_para_colocar.custo 
                                            grid_maquinas[(cell_r, cell_c)] = [maquina_para_colocar] 
                                            print(f"Compra realizada! Máquina em {(cell_r, cell_c)}")
                                            maquina_para_colocar = None 
                                        else:
                                            print("Opa, dinheiro acabou antes de colocar!")
                                            maquina_para_colocar = None
                                    else:
                                        print("Célula já ocupada!")
                                else:
                                    print("Local inválido ou Doca.")

                            # 2. Tentar Colocar Slot (CORREÇÃO AQUI)
                            elif selected_slot_type:
                                slot_r, slot_c = get_slot_from_world_pos(mouse_world_pos[0], mouse_world_pos[1])
                                # Chama função do game_state que lida com validação e dinheiro
                                if game.expandir_fabrica(slot_r, slot_c, selected_slot_type):
                                    selected_slot_type = None # Desmarca após comprar
                                    
        # Atualizações do jogo (física, lógica)
        if not mostrando_tutorial and game.estado_jogo != 'GAME_OVER':
            if game.estado_jogo == 'JOGANDO':
                
                game.tempo_restante -= decorrido
                if game.tempo_restante <= 0:
                    game.tempo_restante = 0 
                    if caminhao and caminhao.estado == 'PARADO':
                        caminhao.iniciar_partida()
                        game.estado_jogo = 'CAMINHAO_PARTINDO' 
                        print("Tempo esgotado! Caminhão partindo...")
                
                # --- LÓGICA DE MOVIMENTO E COLISÃO ---
                def ponto_valido(x, y):
                    sr, sc = get_slot_from_world_pos(x, y)
                    return (sr, sc) in game.owned_slots

                # Eixo X
                step_x = direcao_x * jogador.velocidade * decorrido
                jogador.pos_x_px += step_x
                jogador.rect.centerx = round(jogador.pos_x_px)

                hitbox_jogador = jogador.rect.inflate(0, -10)
                for (cell_r, cell_c), maquinas in grid_maquinas.items():
                    if maquinas:
                        rect_maquina = pygame.Rect(cell_c * TAMANHO_CELULA, cell_r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
                        hitbox_maquina = rect_maquina.inflate(-10, -10)

                        if hitbox_jogador.colliderect(hitbox_maquina):
                            if step_x > 0: jogador.rect.right = hitbox_maquina.left
                            elif step_x < 0: jogador.rect.left = hitbox_maquina.right
                            jogador.pos_x_px = float(jogador.rect.centerx)

                if step_x > 0:
                    if not ponto_valido(jogador.rect.right, jogador.rect.top) or not ponto_valido(jogador.rect.right, jogador.rect.bottom):
                        slot_atual_c = int(jogador.rect.centerx // SLOT_LARGURA_PX)
                        limite_direita = (slot_atual_c + 1) * SLOT_LARGURA_PX
                        if jogador.rect.right > limite_direita:
                            jogador.rect.right = limite_direita - 1
                            jogador.pos_x_px = float(jogador.rect.centerx)

                elif step_x < 0: 
                    if not ponto_valido(jogador.rect.left, jogador.rect.top) or not ponto_valido(jogador.rect.left, jogador.rect.bottom):
                        slot_atual_c = int(jogador.rect.centerx // SLOT_LARGURA_PX)
                        limite_esquerda = slot_atual_c * SLOT_LARGURA_PX
                        if jogador.rect.left < limite_esquerda:
                            jogador.rect.left = limite_esquerda + 1
                            jogador.pos_x_px = float(jogador.rect.centerx)

                # Eixo Y
                step_y = direcao_y * jogador.velocidade * decorrido
                jogador.pos_y_px += step_y
                jogador.rect.centery = round(jogador.pos_y_px)

                hitbox_jogador = jogador.rect.inflate(-10, 0)
                for (cell_r, cell_c), maquinas in grid_maquinas.items():
                    if maquinas:
                        rect_maquina = pygame.Rect(cell_c * TAMANHO_CELULA, cell_r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
                        hitbox_maquina = rect_maquina.inflate(-10, -10)

                        if hitbox_jogador.colliderect(hitbox_maquina):
                            if step_y > 0: jogador.rect.bottom = hitbox_maquina.top
                            elif step_y < 0: jogador.rect.top = hitbox_maquina.bottom
                            jogador.pos_y_px = float(jogador.rect.centery)

                if step_y > 0:
                    if not ponto_valido(jogador.rect.left, jogador.rect.bottom) or not ponto_valido(jogador.rect.right, jogador.rect.bottom):
                        slot_atual_r = int(jogador.rect.centery // SLOT_ALTURA_PX)
                        limite_baixo = (slot_atual_r + 1) * SLOT_ALTURA_PX
                        if jogador.rect.bottom > limite_baixo:
                            jogador.rect.bottom = limite_baixo - 1
                            jogador.pos_y_px = float(jogador.rect.centery)

                elif step_y < 0:
                    if not ponto_valido(jogador.rect.left, jogador.rect.top) or not ponto_valido(jogador.rect.right, jogador.rect.top):
                        slot_atual_r = int(jogador.rect.centery // SLOT_ALTURA_PX)
                        limite_cima = slot_atual_r * SLOT_ALTURA_PX
                        if jogador.rect.top < limite_cima:
                            jogador.rect.top = limite_cima + 1
                            jogador.pos_y_px = float(jogador.rect.centery)

                if step_x != 0 or step_y != 0:
                     jogador.update(direcao_x, direcao_y, decorrido)
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
            jogador.update(0, 0, decorrido)

        # --- DESENHO ---
        mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
        
        desenhar_mundo(game, grid_maquinas, grid_decoracoes, jogador, caminhao, camera, mouse_world_pos, selected_slot_type, maquina_para_colocar)
        b_maquinas, b_slots, b_colocar = desenhar_interface(game, jogador, selected_slot_type, pos_mouse_tela, maquina_para_colocar)
        
        if mostrando_tutorial:
            desenhar_tutorial(TELA_JOGO)
        elif game.estado_jogo == 'GAME_OVER':
            desenhar_game_over(TELA_JOGO)
            
        TELA.blit(TELA_JOGO, (0,0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()