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

# --- CONFIGURAÇÕES DO GRID E SLOTS ---
TAMANHO_CELULA = 60
SLOT_LARGURA_CELULAS = 7
SLOT_ALTURA_CELULAS = 5
SLOT_LARGURA_PX = SLOT_LARGURA_CELULAS * TAMANHO_CELULA
SLOT_ALTURA_PX = SLOT_ALTURA_CELULAS * TAMANHO_CELULA

# --- IMAGENS ---
IMG_MAQUINA_ESTATICA = pygame.transform.scale(pygame.image.load("assets/maquina.png").convert_alpha(), (TAMANHO_CELULA, TAMANHO_CELULA))
ANIMACAO_MAQUINA_M1 = [pygame.transform.scale(pygame.image.load(f"assets/maquinas/m1/m1{i}.png").convert_alpha(), (TAMANHO_CELULA, TAMANHO_CELULA)) for i in range(1, 4)]

# --- NOVO (Request 1, 3, 4) ---
try:
    IMG_CAMINHAO_LOGICA = pygame.image.load("assets/maquinas/caminhao/caminhao2.png").convert_alpha()
    IMG_CAMINHAO_LOGICA = pygame.transform.scale(IMG_CAMINHAO_LOGICA, (int(TAMANHO_CELULA * 4), int(TAMANHO_CELULA * 4)))
except Exception as e:
    print(f"Erro ao carregar caminhao2.png: {e}")
    IMG_CAMINHAO_LOGICA = pygame.Surface((TAMANHO_CELULA * 1.5, TAMANHO_CELULA * 1.5)) # Placeholder

try:
    IMG_FAIXA = pygame.image.load("assets/fabrica/faixa.png").convert_alpha()
    IMG_FAIXA = pygame.transform.scale(IMG_FAIXA, (TAMANHO_CELULA, TAMANHO_CELULA)) # Escala para o tamanho da célula
except Exception as e:
    print(f"Erro ao carregar faixa.png: {e}")
    IMG_FAIXA = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA)) # Placeholder
# -------------------------------


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
# --- MODIFICADO: Adiciona 'jogador' como parâmetro
def desenhar_interface(game, jogador, selected_slot_type, pos_mouse):
    TELA_JOGO.fill(COR_PAINEL, (0, 0, 400, JOGO_ALTURA))
    pygame.draw.rect(TELA_JOGO,COR_PAINEL,(0,0,JOGO_LARGURA,80))
    info=[f"Turno: {game.turno}",f"Tempo: {int(game.tempo_restante)}s",f"Dinheiro: ${game.dinheiro}",f"Reputação: {game.reputacao}"]
    for i, linha in enumerate(info): TELA_JOGO.blit(FONTE.render(linha, True, COR_TEXTO), (20 + i * 250, 30))
    y_painel=100
    
    # --- ESTOQUE (Do caminhão/global - o que foi entregue) ---
    TELA_JOGO.blit(FONTE_TITULO.render("Estoque (Global):",True,COR_TITULO),(20,y_painel));y_painel+=30
    if game.estoque:
        for k,v in game.estoque.items(): TELA_JOGO.blit(FONTE.render(f"{k}: {v}",True,COR_TEXTO),(30,y_painel)); y_painel+=20
    else: TELA_JOGO.blit(FONTE.render("Vazio",True,COR_TEXTO),(30,y_painel));y_painel+=20
    
    # --- NOVO: INVENTÁRIO DO JOGADOR ---
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
    # ------------------------------------

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
    
    # --- NOVO: PAINEL DE PEDIDOS ATIVOS ---
    y_painel+=15
    TELA_JOGO.blit(FONTE_TITULO.render("Pedidos Ativos:",True,COR_TITULO),(20,y_painel))
    y_painel+=30
    pedidos_ativos = [p for p in game.pedidos if not p.entregue]
    if pedidos_ativos:
        for pedido in pedidos_ativos:
            prazo_restante = pedido.prazo - game.turno
            cor_prazo = COR_TEXTO
            if prazo_restante <= 1: cor_prazo = VERMELHO_BRILHANTE
            elif prazo_restante <= 3: cor_prazo = AMARELO_BRILHANTE
            texto = f"- {pedido.quantidade}x {pedido.tipo} (Prazo: {prazo_restante} turnos)"
            TELA_JOGO.blit(FONTE.render(texto, True, cor_prazo),(30,y_painel))
            y_painel+=20
    else:
        TELA_JOGO.blit(FONTE.render("Nenhum pedido ativo",True,COR_TEXTO),(30,y_painel))
        y_painel+=20
    # ---------------------------------------

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

# --- MODIFICADO (Request 1, 3): Aceita caminhao e grid_decoracoes
def desenhar_mundo(game, grid, grid_decoracoes, jogador, caminhao, camera, mouse_world_pos, selected_slot_type):
    TELA_JOGO.fill(COR_FUNDO)
    for (r, c), tipo_slot in game.owned_slots.items():
        if tipo_slot in IMG_FABRICA_TILES:
            slot_rect = pygame.Rect(c * SLOT_LARGURA_PX, r * SLOT_ALTURA_PX, SLOT_LARGURA_PX, SLOT_ALTURA_PX)
            TELA_JOGO.blit(IMG_FABRICA_TILES[tipo_slot], camera.apply_to_rect(slot_rect))
    
    # --- NOVO: Desenha as decorações (faixas) (Request 3) ---
    for (r, c), img_faixa in grid_decoracoes.items():
        faixa_rect = pygame.Rect(c * TAMANHO_CELULA, r * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
        TELA_JOGO.blit(img_faixa, camera.apply_to_rect(faixa_rect))
    # -----------------------------------------------------

    # --- NOVO: Desenha as máquinas que estão no grid ---
    for (r, c), maquinas_na_celula in grid.items():
        for idx, maquina in enumerate(maquinas_na_celula):
            offset_visual = idx * 5
            pos_x = c * TAMANHO_CELULA + offset_visual
            pos_y = r * TAMANHO_CELULA + offset_visual
            rect_maquina = pygame.Rect(pos_x, pos_y, TAMANHO_CELULA, TAMANHO_CELULA)
            TELA_JOGO.blit(IMG_MAQUINA_ESTATICA, camera.apply_to_rect(rect_maquina))
            
            # --- NOVO: Feedback visual para peças prontas ---
            if maquina.pecas_para_coletar > 0:
                # Desenha um pequeno ícone ou contador
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

    # --- NOVO: Desenha o caminhão (Request 1 & 4) ---
    if caminhao:
        caminhao.draw(TELA_JOGO, FONTE, camera)
    # --------------------------------------------

# --- LÓGICA PRINCIPAL ---
def main():
    game = GameState()
    # --- NOVO: Grid agora é um dicionário para o mundo infinito ---
    grid_maquinas = {}
    grid_decoracoes = {} # --- NOVO (Request 3) ---
    
    # --- MODIFICADO (Request 1, 2, 4) ---
    # Encontrar o slot de doca inicial e posicionar jogador e caminhão
    camera = Camera(JOGO_LARGURA, JOGO_ALTURA)
    caminhao = None
    start_pos_x, start_pos_y = (0.5 * SLOT_LARGURA_PX), (0.5 * SLOT_ALTURA_PX) # Posição Padrão

    doca_slot_r, doca_slot_c = None, None
    for (r, c), tipo in game.owned_slots.items():
        if tipo == 'doca':
            doca_slot_r, doca_slot_c = r, c
            break
    
    if doca_slot_r is not None:
        # Centro do slot de doca
        pos_caminhao_x = (doca_slot_c * SLOT_LARGURA_PX) + (SLOT_LARGURA_PX / 2)
        pos_caminhao_y = (doca_slot_r * SLOT_ALTURA_PX) + (SLOT_ALTURA_PX / 2)
        caminhao = Caminhao(pos_caminhao_x, pos_caminhao_y, IMG_CAMINHAO_LOGICA)
        
        # Coloca o jogador abaixo da área de carga do caminhão
        start_pos_x = pos_caminhao_x
        start_pos_y = caminhao.area_carga.bottom + 30
    
    jogador = Jogador(start_pos_x, start_pos_y, TAMANHO_CELULA)
    # -------------------------------------
    
    direcao_x, direcao_y = 0, 0
    tempo_anterior = pygame.time.get_ticks()
    selected_slot_type = None
    rodando = True
    while rodando:
        agora = pygame.time.get_ticks()
        decorrido = (agora - tempo_anterior) / 1000.0
        tempo_anterior = agora
        pos_mouse_tela = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_LEFT, pygame.K_a): direcao_x = -1
                elif evento.key in (pygame.K_RIGHT, pygame.K_d): direcao_x = 1
                elif evento.key in (pygame.K_UP, pygame.K_w): direcao_y = -1
                elif evento.key in (pygame.K_DOWN, pygame.K_s): direcao_y = 1
                
                # --- LÓGICA 'E' (INTERAGIR) TOTALMENTE MODIFICADA ---
                if evento.key == pygame.K_e: 
                    # 1. TENTAR DESCARREGAR NO CAMINHÃO
                    if caminhao and caminhao.estado == 'PARADO' and jogador.rect.colliderect(caminhao.area_carga):
                        if jogador.inventario:
                            for tipo, qtd in jogador.inventario.items():
                                caminhao.receber_carga(tipo, qtd)
                            print(f"Descarregou {jogador.inventario} no caminhão.")
                            jogador.inventario.clear()
                        else:
                            print("Inventário vazio, nada para descarregar.")
                    
                    # 2. TENTAR PEGAR DE UMA MÁQUINA
                    else:
                        cell_r, cell_c = get_cell_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                        if (cell_r, cell_c) in grid_maquinas:
                            # Pega a primeira máquina na célula (ou a mais próxima)
                            maquina_na_celula = grid_maquinas[(cell_r, cell_c)][0] 
                            
                            if maquina_na_celula.pecas_para_coletar > 0:
                                # Calcula espaço livre no inventário do jogador
                                carga_atual_jogador = sum(jogador.inventario.values())
                                espaco_livre = jogador.carga_maxima - carga_atual_jogador
                                
                                if espaco_livre > 0:
                                    tipo_peca = maquina_na_celula.tipo
                                    
                                    # Permite pegar se o inventário estiver vazio OU se já tiver esse tipo de peça
                                    if not jogador.inventario or tipo_peca in jogador.inventario:
                                        quantidade_a_pegar = min(maquina_na_celula.pecas_para_coletar, espaco_livre)
                                        
                                        # Adiciona ao inventário do jogador
                                        jogador.inventario[tipo_peca] = jogador.inventario.get(tipo_peca, 0) + quantidade_a_pegar
                                        # Remove da máquina
                                        maquina_na_celula.pecas_para_coletar -= quantidade_a_pegar
                                        
                                        print(f"Pegou {quantidade_a_pegar}x {tipo_peca}. Máquina agora tem {maquina_na_celula.pecas_para_coletar}.")
                                    else:
                                        print("Inventário cheio ou com item de outro tipo! Esvazie no caminhão.")
                                else:
                                    print("Inventário do jogador está cheio!")
                            else:
                                print("Máquina vazia, aguardando produção.")
                
                # --- NOVO: TECLA 'T' PARA TERMINAR O TURNO ---
                if evento.key == pygame.K_t:
                    if caminhao and caminhao.estado == 'PARADO':
                        caminhao.iniciar_partida()
                        game.estado_jogo = 'CAMINHAO_PARTINDO' # Pausa o jogador
                        print("Turno encerrado manualmente! Caminhão partindo...")

                # --- NOVO (Request 3) ---
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
                
                # --- Lógica de posicionamento de máquinas ---
                if evento.key == pygame.K_m and game.maquinas:
                    cell_r, cell_c = get_cell_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                    slot_r, slot_c = get_slot_from_world_pos(jogador.rect.centerx, jogador.rect.centery)
                    
                    if (slot_r, slot_c) in game.owned_slots:
                        # --- MODIFICADO: Checa se não é uma doca ---
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
                    # --- MODIFICADO: Passa 'jogador' ---
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

        # --- MODIFICADO (Request 1) ---
        # --- MODIFICADO (Request 1) ---
        # LÓGICA DE ATUALIZAÇÃO DE MOVIMENTO
        if game.estado_jogo == 'JOGANDO':
            
            # --- CORREÇÃO: FAZ O CONTADOR DO TURNO DIMINUIR ---
            game.tempo_restante -= decorrido
            # ----------------------------------------------------

            # --- NOVO: FORÇA O FIM DO TURNO QUANDO O TEMPO ACABA ---
            if game.tempo_restante <= 0:
                game.tempo_restante = 0 # Trava em 0
                
                # Verifica se o caminhão está pronto para partir (evita bugs)
                if caminhao and caminhao.estado == 'PARADO':
                    caminhao.iniciar_partida()
                    game.estado_jogo = 'CAMINHAO_PARTINDO' # Trava o jogador
                    print("Tempo esgotado! Caminhão partindo...")
            # ------------------------------------------------------
            
            # Lógica de movimento (só executa se o tempo não tiver acabado de acabar)
            if game.estado_jogo == 'JOGANDO': # Checa de novo, pois o bloco acima pode ter mudado
                next_pos_x = jogador.pos_x_px + direcao_x * jogador.velocidade * decorrido
                next_pos_y = jogador.pos_y_px + direcao_y * jogador.velocidade * decorrido
                next_slot_r, next_slot_c = get_slot_from_world_pos(next_pos_x, next_pos_y)
                
                if (next_slot_r, next_slot_c) in game.owned_slots:
                    jogador.update(direcao_x, direcao_y, decorrido)
                else:
                    jogador.update(0, 0, decorrido) # Trava o movimento
        else:
             jogador.update(0, 0, decorrido) # Para o jogador se o caminhão estiver partindo
        
        camera.center_on(jogador.rect)

        # --- NOVO (Request 1) ---
        if caminhao:
            caminhao.update(decorrido, game, grid_maquinas)
        # -------------------------


        # LÓGICA DE DESENHO
        mouse_world_pos = camera.screen_to_world(pos_mouse_tela)
        
        # --- MODIFICADO (Request 1, 3) ---
        desenhar_mundo(game, grid_maquinas, grid_decoracoes, jogador, caminhao, camera, mouse_world_pos, selected_slot_type)
        
        # --- MODIFICADO: Passa 'jogador' ---
        desenhar_interface(game, jogador, selected_slot_type, pos_mouse_tela)
        
        TELA.blit(TELA_JOGO, (0,0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()