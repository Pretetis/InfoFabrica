import pygame
import random
import sys

# --- CLASSES ---

class Caminhao:
    def __init__(self, x, y, imagem):
        self.imagem = imagem
        self.largura, self.altura = self.imagem.get_size()
        self.pos_base = pygame.math.Vector2(x, y)
        self.rect = self.imagem.get_rect(topleft=self.pos_base)
        
        # Área de interação para o jogador (atrás do caminhão)
        self.area_carga = pygame.Rect(x + self.largura, y, 60, self.altura)

        self.estado = 'PARADO'  # PARADO, PARTINDO, VOLTANDO
        self.velocidade = 350 # Pixels por segundo
        self.carga = {} # Ex: {"Motor V1": 5}

    def update(self, dt, game_state, grid):
        if self.estado == 'PARTINDO':
            self.rect.x -= self.velocidade * dt
            # Se saiu da tela
            if self.rect.right < 0:
                self.processar_entrega(game_state)
                game_state.produzir_nas_maquinas(grid)
                game_state.avancar_turno()
                self.iniciar_retorno()

        elif self.estado == 'VOLTANDO':
            self.rect.x += self.velocidade * dt
            # Se voltou para a posição original
            if self.rect.x >= self.pos_base.x:
                self.rect.topleft = self.pos_base
                self.estado = 'PARADO'

    def draw(self, surface, fonte):
        surface.blit(self.imagem, self.rect)
        # Desenha um contorno na área de carga para feedback visual
        pygame.draw.rect(surface, (255, 200, 0, 150), self.area_carga, 2)

        # Desenha a carga atual do caminhão
        if self.carga:
            y_offset = 0
            for item, qtd in self.carga.items():
                texto_carga = fonte.render(f"{item}: {qtd}", True, COR_TITULO)
                pos = (self.rect.centerx - texto_carga.get_width() / 2, self.rect.y - 25 - y_offset)
                surface.blit(texto_carga, pos)
                y_offset += 20


    def iniciar_partida(self):
        if not self.estado == 'PARADO': return
        self.estado = 'PARTINDO'

    def iniciar_retorno(self):
        self.rect.x = -self.largura - 20 # Começa fora da tela à esquerda
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
                    recompensa = pedido.quantidade * 100 # Exemplo de recompensa
                    game_state.dinheiro += recompensa
                    game_state.reputacao += 10
                    pedidos_a_remover.append(pedido) # Marcar para remoção posterior se quiser
        
        self.carga.clear() # Esvazia o caminhão após a entrega

class Maquina:
    # (Sem alterações)
    def __init__(self, tipo, producao, custo, custo_energia, largura, altura, animacao=None):
        self.tipo, self.producao, self.custo, self.custo_energia = tipo, producao, custo, custo_energia
        self.largura, self.altura = largura, altura
        self.pecas_para_coletar = 0
        self.pos_lin, self.pos_col = -1, -1
        self.animation_frames = animacao
        self.current_frame_index, self.animation_timer, self.animation_speed = 0, 0, 0.15
    def update_animation(self, dt):
        if not self.animation_frames: return
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
    def get_current_frame(self):
        return self.animation_frames[self.current_frame_index] if self.animation_frames else None
    def produzir(self): self.pecas_para_coletar += self.producao


class GameState:
    def __init__(self):
        self.turno = 1
        self.tempo_restante = 60
        self.dinheiro = 1000
        self.reputacao = 100
        self.estoque = {}
        self.pedidos = []
        self.maquinas = []
        self.loja_maquinas = [
            {"tipo": "Motor V1", "producao": 5, "custo": 300, "custo_energia": 10, "largura": 2, "altura": 2},
            {"tipo": "Chassi Básico", "producao": 2, "custo": 500, "custo_energia": 15, "largura": 2, "altura": 2},
        ]
        self.estado_jogo = 'JOGANDO' # NOVO: JOGANDO, ANIMACAO_TURNO

    def produzir_nas_maquinas(self, grid):
        maquinas_processadas = set()
        for linha in grid:
            for celula in linha:
                if isinstance(celula, Maquina) and celula not in maquinas_processadas:
                    celula.produzir()
                    maquinas_processadas.add(celula)

    def avancar_turno(self):
        self.turno += 1
        self.tempo_restante = 60
        print(f"Iniciando Turno {self.turno}")

    def gerar_pedido(self):
        class Pedido:
            def __init__(self, tipo, quantidade, prazo):
                self.tipo, self.quantidade, self.prazo, self.entregue = tipo, quantidade, prazo, False
        self.pedidos.append(Pedido("Motor V1", 10, self.turno + 5))
        self.pedidos.append(Pedido("Chassi Básico", 5, self.turno + 8))





# --- Início do Código Principal ---
pygame.init()
# --- CONFIGURAÇÕES ---
JOGO_LARGURA, JOGO_ALTURA = 1200, 600
TELA = pygame.display.set_mode((JOGO_LARGURA, JOGO_ALTURA), pygame.RESIZABLE)
TELA_JOGO = pygame.Surface((JOGO_LARGURA, JOGO_ALTURA))
pygame.display.set_caption("Jogo de Gestão com Logística")
COR_FUNDO=(30,30,40);COR_PAINEL=(45,45,55);COR_TEXTO=(220,220,220);COR_TITULO=(255,255,255);COR_FUNDO_EXTERNO=(10,10,10);COR_BOTAO_NORMAL=(70,70,80);COR_BOTAO_HOVER=(100,100,110);COR_BOTAO_BORDA=(130,130,140);VERDE_BRILHANTE=(0,255,120);VERMELHO_BRILHANTE=(255,80,80);AMARELO_BRILHANTE=(255,200,0)
TAMANHO_CELULA=40;GRID_COLUNAS=20;GRID_LINHAS=12;OFFSET_X=420;OFFSET_Y=120
FONTE=pygame.font.SysFont("monospace",18);FONTE_TITULO=pygame.font.SysFont("monospace",22,bold=True)

# --- IMAGENS ---
IMG_MAQUINA_ESTATICA = pygame.transform.scale(pygame.image.load("assets/maquina.png").convert_alpha(), (TAMANHO_CELULA * 2, TAMANHO_CELULA * 2))
IMG_CHAO = pygame.transform.scale(pygame.image.load("assets/fabrica.png").convert_alpha(), (GRID_COLUNAS * TAMANHO_CELULA, GRID_LINHAS * TAMANHO_CELULA))
try:
    IMG_ENGRENAGEM = pygame.transform.scale(pygame.image.load("assets/itens/engine.png").convert_alpha(), (TAMANHO_CELULA // 2, TAMANHO_CELULA // 2))
except: IMG_ENGRENAGEM = None
try:
    ANIMACAO_MAQUINA_M1 = [pygame.transform.scale(pygame.image.load(f"assets/maquinas/m1/m1{i}.png").convert_alpha(), (TAMANHO_CELULA * 2, TAMANHO_CELULA * 2)) for i in range(1, 4)]
except: ANIMACAO_MAQUINA_M1 = None
# NOVO: Carregar imagem do caminhão
try:
    IMG_CAMINHAO = pygame.image.load("assets/maquinas/caminhao/caminhao1.png").convert_alpha()
    # Ajuste a escala conforme o tamanho da sua imagem
    IMG_CAMINHAO = pygame.transform.scale(IMG_CAMINHAO, (TAMANHO_CELULA * 4, TAMANHO_CELULA * 2))
except Exception as e:
    print(f"Erro ao carregar imagem do caminhão: {e}"); IMG_CAMINHAO = None

def converter_pos_mouse(pos, tela_rect, jogo_largura, jogo_altura):
    x, y = pos; x -= tela_rect.left; y -= tela_rect.top
    x = x * (jogo_largura / tela_rect.width); y = y * (jogo_altura / tela_rect.height)
    return int(x), int(y)

def desenhar_interface(game, grid, jogador, pos_mouse, dt, caminhao):
    # (Interface de painéis, loja, etc. - sem alterações)
    TELA_JOGO.fill(COR_FUNDO)
    pygame.draw.rect(TELA_JOGO,COR_PAINEL,(0,0,JOGO_LARGURA,80));info=[f"Turno: {game.turno}",f"Tempo: {int(game.tempo_restante)}s",f"Dinheiro: ${game.dinheiro}",f"Reputação: {game.reputacao}"];[TELA_JOGO.blit(FONTE.render(linha,True,COR_TEXTO),(20+i*250,30))for i,linha in enumerate(info)]
    pygame.draw.rect(TELA_JOGO,COR_PAINEL,(0,80,400,JOGO_ALTURA-80));y_painel=100
    TELA_JOGO.blit(FONTE_TITULO.render("Estoque:",True,COR_TITULO),(20,y_painel));y_painel+=30
    if game.estoque: [ (TELA_JOGO.blit(FONTE.render(f"{k}: {v}",True,COR_TEXTO),(30,y_painel)), y_painel:=y_painel+20) for k,v in game.estoque.items() ]
    else: TELA_JOGO.blit(FONTE.render("Vazio",True,COR_TEXTO),(30,y_painel));y_painel+=20
    y_painel+=20;TELA_JOGO.blit(FONTE_TITULO.render("Pedidos:",True,COR_TITULO),(20,y_painel));y_painel+=30
    for pedido in game.pedidos:
        cor=VERDE_BRILHANTE if pedido.entregue else (COR_TEXTO if pedido.prazo > game.turno else VERMELHO_BRILHANTE)
        txt=f"{pedido.quantidade}x {pedido.tipo} (Prazo: {pedido.prazo})";TELA_JOGO.blit(FONTE.render(txt,True,cor),(30,y_painel));y_painel+=25
    y_painel+=15;TELA_JOGO.blit(FONTE_TITULO.render("Máquinas:",True,COR_TITULO),(20,y_painel));y_painel+=30
    [ (TELA_JOGO.blit(FONTE.render(f"{maquina.tipo}",True,COR_TEXTO),(30,y_painel)), y_painel:=y_painel+25) for maquina in game.maquinas]
    y_painel+=15;TELA_JOGO.blit(FONTE_TITULO.render("Loja:",True,COR_TITULO),(20,y_painel));y_painel+=30
    botoes_loja=[]
    for i,modelo in enumerate(game.loja_maquinas):
        rect=pygame.Rect(20,y_painel,360,35);cor_botao=COR_BOTAO_HOVER if rect.collidepoint(pos_mouse)else COR_BOTAO_NORMAL;pygame.draw.rect(TELA_JOGO,cor_botao,rect);pygame.draw.rect(TELA_JOGO,COR_BOTAO_BORDA,rect,2);TELA_JOGO.blit(FONTE.render(f"{modelo['tipo']} | P:{modelo['producao']} | ${modelo['custo']}",True,COR_TEXTO),(30,y_painel+7));botoes_loja.append((rect,modelo));y_painel+=45
    btn_turno=pygame.Rect(100,JOGO_ALTURA-60,200,40);cor_btn_turno=AMARELO_BRILHANTE if btn_turno.collidepoint(pos_mouse)else VERMELHO_BRILHANTE;pygame.draw.rect(TELA_JOGO,cor_btn_turno,btn_turno);texto_btn_turno=FONTE_TITULO.render("Passar Turno",True,(30,30,30));TELA_JOGO.blit(texto_btn_turno,(130,JOGO_ALTURA-55))
    TELA_JOGO.blit(FONTE_TITULO.render("Fábrica:",True,COR_TITULO),(OFFSET_X,OFFSET_Y-30))
    desenhar_fabrica(grid, jogador, dt, caminhao)
    return botoes_loja, btn_turno

def desenhar_fabrica(grid, jogador, dt, caminhao):
    TELA_JOGO.blit(IMG_CHAO, (OFFSET_X, OFFSET_Y))
    
    # Desenha o caminhão primeiro para que os outros itens fiquem por cima
    if caminhao:
        caminhao.draw(TELA_JOGO, FONTE)

    maquinas_desenhadas = set()
    for i in range(GRID_LINHAS):
        for j in range(GRID_COLUNAS):
            maquina = grid[i][j]
            if maquina and maquina not in maquinas_desenhadas:
                x = OFFSET_X + maquina.pos_col * TAMANHO_CELULA; y = OFFSET_Y + maquina.pos_lin * TAMANHO_CELULA
                maquina.update_animation(dt); frame = maquina.get_current_frame()
                TELA_JOGO.blit(frame if frame else IMG_MAQUINA_ESTATICA, (x, y))
                if maquina.pecas_para_coletar > 0 and IMG_ENGRENAGEM:
                    icone_x = x + (maquina.largura * TAMANHO_CELULA) // 2 - IMG_ENGRENAGEM.get_width() // 2
                    icone_y = y - IMG_ENGRENAGEM.get_height() // 2
                    TELA_JOGO.blit(IMG_ENGRENAGEM, (icone_x, icone_y))
                    texto_pecas = FONTE.render(str(maquina.pecas_para_coletar), True, COR_TITULO)
                    texto_rect = texto_pecas.get_rect(midleft=(icone_x + IMG_ENGRENAGEM.get_width() + 5, icone_y + IMG_ENGRENAGEM.get_height() // 2))
                    fundo_rect = texto_rect.inflate(6, 4)
                    pygame.draw.rect(TELA_JOGO, COR_PAINEL, fundo_rect, border_radius=3)
                    TELA_JOGO.blit(texto_pecas, texto_rect)
                maquinas_desenhadas.add(maquina)
    jogador.draw(TELA_JOGO)


def pode_posicionar_maquina(grid, lin, col, maquina):
    # (Sem alterações)
    if not (0<=lin<GRID_LINHAS and 0<=col<GRID_COLUNAS): return False
    try:
        if lin+maquina.altura>GRID_LINHAS or col+maquina.largura>GRID_COLUNAS: return False
        for dl in range(maquina.altura):
            for dc in range(maquina.largura):
                if grid[lin+dl][col+dc] is not None: return False
        return True
    except IndexError: return False

def main():
    global TELA
    clock = pygame.time.Clock(); game = GameState()
    grid = [[None for _ in range(GRID_COLUNAS)] for _ in range(GRID_LINHAS)]
    jogador = Jogador(OFFSET_X + GRID_COLUNAS * TAMANHO_CELULA / 2, OFFSET_Y + GRID_LINHAS * TAMANHO_CELULA / 2, TAMANHO_CELULA)
    
    # NOVO: Instancia o caminhão
    caminhao = Caminhao(OFFSET_X, OFFSET_Y, IMG_CAMINHAO) if IMG_CAMINHAO else None

    direcao_x, direcao_y = 0, 0; game.gerar_pedido(); tempo_anterior = pygame.time.get_ticks()

    rodando = True
    while rodando:
        agora = pygame.time.get_ticks(); decorrido = (agora - tempo_anterior) / 1000; tempo_anterior = agora
        clock.tick(60)

        # Atualiza o tempo apenas se o jogo não estiver em uma animação
        if game.estado_jogo == 'JOGANDO':
            game.tempo_restante -= decorrido
            if game.tempo_restante <= 0:
                game.estado_jogo = 'ANIMACAO_TURNO'
                caminhao.iniciar_partida()

        # Calcula a posição do mouse e o rect da tela escalada
        tela_rect = TELA.get_rect(); ratio = JOGO_LARGURA/JOGO_ALTURA; nova_largura, nova_altura = TELA.get_size()
        if nova_largura/nova_altura > ratio: escala_largura=int(nova_altura*ratio); escala_altura=nova_altura
        else: escala_largura=nova_largura; escala_altura=int(nova_largura/ratio)
        tela_jogo_rect = pygame.Rect(0,0,escala_largura,escala_altura); tela_jogo_rect.center=tela_rect.center
        pos_mouse_real=pygame.mouse.get_pos(); pos_mouse_convertida=converter_pos_mouse(pos_mouse_real,tela_jogo_rect,JOGO_LARGURA,JOGO_ALTURA)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: rodando = False
            elif evento.type == pygame.VIDEORESIZE: TELA = pygame.display.set_mode(evento.size, pygame.RESIZABLE)
            
            # Só processa eventos de input se não estiver em animação
            if game.estado_jogo == 'JOGANDO':
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_LEFT, pygame.K_a): direcao_x = -1
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d): direcao_x = 1
                    elif evento.key in (pygame.K_UP, pygame.K_w): direcao_y = -1
                    elif evento.key in (pygame.K_DOWN, pygame.K_s): direcao_y = 1
                    
                    lin, col = jogador.get_pos_grid(OFFSET_X, OFFSET_Y)
                    
                    if evento.key == pygame.K_m and game.maquinas and pode_posicionar_maquina(grid, lin, col, game.maquinas[0]):
                        maquina = game.maquinas.pop(0); maquina.pos_lin, maquina.pos_col = lin, col
                        for dl in range(maquina.altura):
                            for dc in range(maquina.largura): grid[lin+dl][col+dc] = maquina
                    
                    if evento.key == pygame.K_e:
                        if 0<=lin<GRID_LINHAS and 0<=col<GRID_COLUNAS and grid[lin][col]:
                            maquina = grid[lin][col]
                            if maquina.pecas_para_coletar > 0:
                                if maquina.tipo not in game.estoque: game.estoque[maquina.tipo] = 0
                                game.estoque[maquina.tipo] += maquina.pecas_para_coletar
                                maquina.pecas_para_coletar = 0
                    
                    # NOVO: Interação com o caminhão para depositar
                    if evento.key == pygame.K_d and caminhao and caminhao.area_carga.colliderect(jogador.rect):
                        # Tenta carregar o primeiro pedido não entregue
                        for pedido in game.pedidos:
                            if not pedido.entregue and pedido.tipo in game.estoque and game.estoque[pedido.tipo] > 0:
                                qtd_a_mover = min(game.estoque[pedido.tipo], pedido.quantidade)
                                caminhao.receber_carga(pedido.tipo, qtd_a_mover)
                                game.estoque[pedido.tipo] -= qtd_a_mover
                                if game.estoque[pedido.tipo] == 0:
                                    del game.estoque[pedido.tipo]
                                break # Carrega apenas um tipo de item por vez

                elif evento.type == pygame.KEYUP:
                    if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d): direcao_x = 0
                    elif evento.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s): direcao_y = 0

                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    botoes_loja, btn_turno = desenhar_interface(game, grid, jogador, pos_mouse_convertida, 0, caminhao)
                    for rect, modelo in botoes_loja:
                        if rect.collidepoint(pos_mouse_convertida) and game.dinheiro >= modelo["custo"]:
                            nova_maquina=Maquina(modelo["tipo"],modelo["producao"],modelo["custo"],modelo["custo_energia"],modelo.get("largura",2),modelo.get("altura",2),animacao=ANIMACAO_MAQUINA_M1)
                            game.maquinas.append(nova_maquina); game.dinheiro -= modelo["custo"]
                    if btn_turno and btn_turno.collidepoint(pos_mouse_convertida):
                        game.estado_jogo = 'ANIMACAO_TURNO'
                        caminhao.iniciar_partida()

        # Atualiza a posição do jogador apenas se o jogo não estiver em animação
        if game.estado_jogo == 'JOGANDO':
            jogador.update(direcao_x, direcao_y, decorrido, (OFFSET_X, OFFSET_Y, GRID_COLUNAS, GRID_LINHAS))

        # Atualiza o caminhão (ele se move independentemente do estado do jogo)
        if caminhao:
            caminhao.update(decorrido, game, grid)
            # Se o caminhão terminou de voltar, o jogo pode continuar
            if caminhao.estado == 'VOLTANDO' and game.estado_jogo == 'ANIMACAO_TURNO':
                game.estado_jogo = 'JOGANDO'

        # Desenho
        botoes_loja, btn_turno = desenhar_interface(game, grid, jogador, pos_mouse_convertida, decorrido, caminhao)
        TELA.fill(COR_FUNDO_EXTERNO)
        tela_escalada = pygame.transform.scale(TELA_JOGO, (tela_jogo_rect.width, tela_jogo_rect.height))
        TELA.blit(tela_escalada, tela_jogo_rect)
        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()