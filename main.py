import pygame
import random
import sys
from classes.maquina import Maquina
from classes.game_state import GameState

pygame.init()

# Configurações da janela
LARGURA, ALTURA = 1400, 800
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Gestão de Produção")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
CINZA = (200, 200, 200)

# Grade da fábrica (maior agora!)
TAMANHO_CELULA = 40
GRID_COLUNAS = 20
GRID_LINHAS = 12
OFFSET_X = 420   # puxado pra direita para caber HUD
OFFSET_Y = 120

# Fonte
FONTE = pygame.font.SysFont("arial", 20)
FONTE_TITULO = pygame.font.SysFont("arial", 24, bold=True)

# Imagens
IMG_MAQUINA = pygame.image.load("assets/maquina.png").convert_alpha()
IMG_MAQUINA = pygame.transform.scale(IMG_MAQUINA, (TAMANHO_CELULA * 2, TAMANHO_CELULA * 2))

IMG_PERSONAGEM = pygame.image.load("assets/personagem.png").convert_alpha()
IMG_PERSONAGEM = pygame.transform.scale(IMG_PERSONAGEM, (TAMANHO_CELULA, TAMANHO_CELULA))

IMG_CHAO = pygame.image.load("assets/fabrica.png").convert_alpha()
IMG_CHAO = pygame.transform.scale(IMG_CHAO, (GRID_COLUNAS * TAMANHO_CELULA, GRID_LINHAS * TAMANHO_CELULA))

def desenhar_interface(game, grid, personagem_pos_px):
    TELA.fill(BRANCO)

    botoes_loja = []  # lista de botões clicáveis
    btn_turno = None

    # --- Painel superior ---
    pygame.draw.rect(TELA, CINZA, (0, 0, LARGURA, 80))
    info = [
        f"Turno: {game.turno}",
        f"Tempo: {int(game.tempo_restante)}s",
        f"Dinheiro: ${game.dinheiro}",
        f"Reputação: {game.reputacao}"
    ]
    for i, linha in enumerate(info):
        texto = FONTE.render(linha, True, PRETO)
        TELA.blit(texto, (20 + i * 250, 30))  # espaçado horizontalmente

    # --- Painel lateral esquerdo ---
    pygame.draw.rect(TELA, CINZA, (0, 80, 400, ALTURA - 80))

    # Estoque
    TELA.blit(FONTE_TITULO.render("Estoque:", True, PRETO), (20, 100))
    y = 130
    if game.estoque:
        for k, v in game.estoque.items():
            TELA.blit(FONTE.render(f"{k}: {v}", True, PRETO), (30, y))
            y += 20
    else:
        TELA.blit(FONTE.render("Vazio", True, PRETO), (30, y))

    # Pedidos
    y += 40
    TELA.blit(FONTE_TITULO.render("Pedidos:", True, PRETO), (20, y))
    y += 30
    for pedido in game.pedidos[:5]:
        txt = f"{pedido.quantidade}x {pedido.tipo} (prazo: {pedido.prazo})"
        cor = VERMELHO if not pedido.entregue else VERDE
        TELA.blit(FONTE.render(txt, True, cor), (30, y))
        y += 25

    # Máquinas
    y += 40
    TELA.blit(FONTE_TITULO.render("Máquinas:", True, PRETO), (20, y))
    y += 30
    for maquina in game.maquinas:
        TELA.blit(FONTE.render(f"{maquina.tipo} | Prod: {maquina.producao}", True, PRETO), (30, y))
        y += 25

    # Loja de Máquinas (com botões clicáveis)
    y += 40
    TELA.blit(FONTE_TITULO.render("Loja:", True, PRETO), (20, y))
    y += 30
    for i, modelo in enumerate(game.loja_maquinas):
        rect = pygame.Rect(20, y, 360, 35)
        pygame.draw.rect(TELA, (180, 180, 180), rect)
        pygame.draw.rect(TELA, PRETO, rect, 2)
        TELA.blit(FONTE.render(f"{i+1}. {modelo['tipo']} | Prod:{modelo['producao']} | ${modelo['custo']}", True, PRETO), (30, y+7))
        botoes_loja.append((rect, modelo))
        y += 45

    # Botão passar turno
    btn_turno = pygame.Rect(100, ALTURA - 60, 200, 40)
    pygame.draw.rect(TELA, VERMELHO, btn_turno)
    texto_btn_turno = FONTE.render("Passar Turno", True, PRETO)
    TELA.blit(texto_btn_turno, (150, ALTURA - 50))

    # --- Fábrica visual ---
    TELA.blit(FONTE_TITULO.render("Fábrica:", True, PRETO), (OFFSET_X, OFFSET_Y - 30))
    desenhar_fabrica(grid, personagem_pos_px)

    pygame.display.update()
    return botoes_loja, btn_turno


def desenhar_fabrica(grid, personagem_pos_px):
    # Desenha o chão primeiro
    TELA.blit(IMG_CHAO, (OFFSET_X, OFFSET_Y))

    # Desenha a grade por cima (opcional)
    for i in range(GRID_LINHAS):
        for j in range(GRID_COLUNAS):
            x = OFFSET_X + j * TAMANHO_CELULA
            y = OFFSET_Y + i * TAMANHO_CELULA
            # pygame.draw.rect(TELA, CINZA, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 1)

            if grid[i][j]:
                maquina = grid[i][j]
                if (i == 0 or grid[i-1][j] != maquina) and (j == 0 or grid[i][j-1] != maquina):
                    TELA.blit(IMG_MAQUINA, (x, y))

    # Personagem
    TELA.blit(IMG_PERSONAGEM, (int(personagem_pos_px[0]), int(personagem_pos_px[1])))



def pode_posicionar_maquina(grid, lin, col, maquina):
    try:
        for dl in range(maquina.altura):
            for dc in range(maquina.largura):
                if grid[lin + dl][col + dc] is not None:
                    return False
        return True
    except IndexError:
        return False


def main():
    clock = pygame.time.Clock()
    game = GameState()
    grid = [[None for _ in range(GRID_COLUNAS)] for _ in range(GRID_LINHAS)]

    personagem_pos_px = [OFFSET_X, OFFSET_Y]

    VELOCIDADE = 120
    direcao_x = 0
    direcao_y = 0

    game.gerar_pedido()
    tempo_anterior = pygame.time.get_ticks()

    rodando = True
    while rodando:
        clock.tick(60)
        agora = pygame.time.get_ticks()
        decorrido = (agora - tempo_anterior) / 1000
        tempo_anterior = agora

        game.tempo_restante -= decorrido
        if game.tempo_restante <= 0:
            game.processar_turno(grid)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    direcao_x = -1
                elif evento.key == pygame.K_RIGHT:
                    direcao_x = 1
                elif evento.key == pygame.K_UP:
                    direcao_y = -1
                elif evento.key == pygame.K_DOWN:
                    direcao_y = 1

                # Colocar máquina
                lin = int((personagem_pos_px[1] - OFFSET_Y) // TAMANHO_CELULA)
                col = int((personagem_pos_px[0] - OFFSET_X) // TAMANHO_CELULA)
                if evento.key == pygame.K_m and game.maquinas and pode_posicionar_maquina(grid, lin, col, game.maquinas[0]):
                    maquina = game.maquinas.pop(0)
                    for dl in range(maquina.altura):
                        for dc in range(maquina.largura):
                            grid[lin + dl][col + dc] = maquina

            elif evento.type == pygame.KEYUP:
                if evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    direcao_x = 0
                elif evento.key in (pygame.K_UP, pygame.K_DOWN):
                    direcao_y = 0

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = evento.pos

                # Clique na loja
                for rect, modelo in botoes_loja:
                    if rect.collidepoint(x, y):
                        if game.dinheiro >= modelo["custo"]:
                            nova_maquina = Maquina(
                                modelo["tipo"],
                                modelo["producao"],
                                modelo["custo"],
                                modelo["custo_energia"],
                                modelo.get("largura", 2),
                                modelo.get("altura", 2)
                            )
                            game.maquinas.append(nova_maquina)
                            game.dinheiro -= modelo["custo"]

                # Clique no botão "Passar Turno"
                if btn_turno.collidepoint(x, y):
                    game.processar_turno(grid)

        # Atualiza posição do personagem
        personagem_pos_px[0] += direcao_x * VELOCIDADE * decorrido
        personagem_pos_px[1] += direcao_y * VELOCIDADE * decorrido
        personagem_pos_px[0] = max(OFFSET_X, min(personagem_pos_px[0], OFFSET_X + (GRID_COLUNAS - 1) * TAMANHO_CELULA))
        personagem_pos_px[1] = max(OFFSET_Y, min(personagem_pos_px[1], OFFSET_Y + (GRID_LINHAS - 1) * TAMANHO_CELULA))

        # Desenha
        botoes_loja, btn_turno = desenhar_interface(game, grid, personagem_pos_px)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
