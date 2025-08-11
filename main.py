import pygame
import random
import sys
from classes.maquina import Maquina

pygame.init()

# Configurações da janela
LARGURA, ALTURA = 1280, 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Gestão de Produção")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
CINZA = (200, 200, 200)
AZUL = (0, 100, 255)

# Grade da fábrica
TAMANHO_CELULA = 40
GRID_COLUNAS = 15
GRID_LINHAS = 10
OFFSET_X = 500
OFFSET_Y = 100

# Fonte
FONTE = pygame.font.SysFont("arial", 20)

# Importa o estado do jogo
from classes.game_state import GameState


def desenhar_interface(game, grid, personagem_pos):
    TELA.fill(BRANCO)

    # Informações do topo
    pygame.draw.rect(TELA, CINZA, (10, 10, 780, 80))
    info = [
        f"Turno: {game.turno}",
        f"Tempo restante: {int(game.tempo_restante)}s",
        f"Dinheiro: ${game.dinheiro}",
        f"Estoque: {game.estoque}",
        f"Reputação: {game.reputacao}"
    ]
    for i, linha in enumerate(info):
        texto = FONTE.render(linha, True, PRETO)
        TELA.blit(texto, (20, 20 + i * 20))

    # Pedidos
    y = 120
    for pedido in game.pedidos[:3]:
        txt = f"Pedido: {pedido.quantidade}x {pedido.tipo} (prazo: {pedido.prazo})"
        TELA.blit(FONTE.render(txt, True, VERMELHO), (20, y))
        y += 25

    # Máquinas compradas
    TELA.blit(FONTE.render("Máquinas:", True, PRETO), (20, 190))
    for i, maquina in enumerate(game.maquinas):
        x = 20 + (i % 2) * 230
        y = 220 + (i // 2) * 90
        pygame.draw.rect(TELA, CINZA, (x, y, 220, 80))
        pygame.draw.rect(TELA, PRETO, (x, y, 220, 80), 2)

        TELA.blit(FONTE.render(f"Tipo: {maquina.tipo}", True, PRETO), (x + 10, y + 10))
        TELA.blit(FONTE.render(f"Produção: {maquina.producao}/turno", True, PRETO), (x + 10, y + 30))
        TELA.blit(FONTE.render(f"Custo: ${maquina.custo}", True, PRETO), (x + 10, y + 50))

    # Loja de máquinas
    TELA.blit(FONTE.render("Loja de Máquinas:", True, PRETO), (20, 420))
    if OFFSET_Y <= y <= OFFSET_Y + GRID_LINHAS * TAMANHO_CELULA and x >= OFFSET_X:
        # Clique na fábrica
        col = (x - OFFSET_X) // TAMANHO_CELULA
        lin = (y - OFFSET_Y) // TAMANHO_CELULA
        if maquina_selecionada and pode_posicionar_maquina(grid, lin, col, maquina_selecionada):
            for dl in range(maquina_selecionada.altura):
                for dc in range(maquina_selecionada.largura):
                    grid[lin + dl][col + dc] = maquina_selecionada
            game.dinheiro -= maquina_selecionada.custo
            maquina_selecionada = None
    else:
        # Clique na loja
        for i, modelo in enumerate(game.loja_maquinas):
            btn_x = 20 + i * 230
            btn_y = 450
            if btn_x <= x <= btn_x + 220 and btn_y <= y <= btn_y + 80:
                if game.dinheiro >= modelo["custo"]:
                    # Cria nova máquina com tamanho
                    maquina_selecionada = Maquina(
                        modelo["tipo"],
                        modelo["producao"],
                        modelo["custo"],
                        modelo["custo_energia"],
                        modelo.get("largura", 2),
                        modelo.get("altura", 2)
                    )
                break

    # Botão: Passar Turno
    pygame.draw.rect(TELA, VERMELHO, (600, 550, 180, 40))
    texto_btn_turno = FONTE.render("Passar Turno", True, PRETO)
    TELA.blit(texto_btn_turno, (635, 560))

    # Fábrica visual
    TELA.blit(FONTE.render("Fábrica:", True, PRETO), (OFFSET_X, OFFSET_Y - 30))
    desenhar_fabrica(grid, personagem_pos)

    y = 200 + len(game.maquinas) * 90  # Logo após mostrar as máquinas
    entregues = [p for p in game.pedidos if p.entregue]
    if entregues:
        TELA.blit(FONTE.render("Pedidos entregues:", True, PRETO), (20, y))
        y += 25
        for p in entregues:
            TELA.blit(FONTE.render(f"{p.quantidade}x {p.tipo}", True, VERDE), (20, y))
            y += 25

    pygame.display.update()


def desenhar_fabrica(grid, personagem_pos):
    for i in range(GRID_LINHAS):
        for j in range(GRID_COLUNAS):
            x = OFFSET_X + j * TAMANHO_CELULA
            y = OFFSET_Y + i * TAMANHO_CELULA

            # Célula
            pygame.draw.rect(TELA, CINZA, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 1)

            # Máquina
            if grid[i][j]:
                maquina = grid[i][j]
                # só desenha no canto superior esquerdo dela
                if (i == 0 or grid[i-1][j] != maquina) and (j == 0 or grid[i][j-1] != maquina):
                    largura_px = maquina.largura * TAMANHO_CELULA
                    altura_px = maquina.altura * TAMANHO_CELULA
                    pygame.draw.rect(
                        TELA, VERDE,
                        (x + 1, y + 1, largura_px - 2, altura_px - 2)
                    )

            # Personagem
            if personagem_pos == [i, j]:
                pygame.draw.rect(
                    TELA, AZUL,
                    (x + TAMANHO_CELULA // 4, y + TAMANHO_CELULA // 4, TAMANHO_CELULA * 1.5, TAMANHO_CELULA * 1.5)
                )


def mover_personagem(tecla, pos, grid):
    nova_pos = pos.copy()
    if tecla == pygame.K_UP and pos[0] > 0:
        nova_pos[0] -= 1
    elif tecla == pygame.K_DOWN and pos[0] < GRID_LINHAS - 1:
        nova_pos[0] += 1
    elif tecla == pygame.K_LEFT and pos[1] > 0:
        nova_pos[1] -= 1
    elif tecla == pygame.K_RIGHT and pos[1] < GRID_COLUNAS - 1:
        nova_pos[1] += 1

    if grid[nova_pos[0]][nova_pos[1]] is None:
        pos[0], pos[1] = nova_pos[0], nova_pos[1]

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
    personagem_pos = [0, 0]
    game.gerar_pedido()
    tempo_anterior = pygame.time.get_ticks()
    maquina_selecionada = None

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
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = evento.pos

                # Clique em modelo da loja
                for i, modelo in enumerate(game.loja_maquinas):
                    btn_x = 20 + i * 230
                    btn_y = 450
                    if btn_x <= x <= btn_x + 220 and btn_y <= y <= btn_y + 80:
                        if game.dinheiro >= modelo["custo"]:
                            maquina_selecionada = Maquina(
                                modelo["tipo"],
                                modelo["producao"],
                                modelo["custo"],
                                modelo["custo_energia"],
                                modelo["largura"],
                                modelo["altura"]
                            )
                            break

                # Clique na fábrica (posição válida para colocar máquina)
                col = (x - OFFSET_X) // TAMANHO_CELULA
                lin = (y - OFFSET_Y) // TAMANHO_CELULA
                if maquina_selecionada and pode_posicionar_maquina(grid, lin, col, maquina_selecionada):
                    for dl in range(maquina_selecionada.altura):
                        for dc in range(maquina_selecionada.largura):
                            grid[lin + dl][col + dc] = maquina_selecionada
                    game.dinheiro -= maquina_selecionada.custo
                    maquina_selecionada = None

                # Clique no botão "Passar Turno"
                if 600 <= x <= 780 and 550 <= y <= 590:
                    game.processar_turno(grid)

            elif evento.type == pygame.KEYDOWN:
                mover_personagem(evento.key, personagem_pos, grid)
                lin, col = personagem_pos

                # Tecla M = posicionar máquina
                if evento.key == pygame.K_m and pode_posicionar_maquina(grid, lin, col) and game.maquinas:
                    maquina = game.maquinas.pop(0)
                    for dl in range(2):
                        for dc in range(2):
                            grid[lin + dl][col + dc] = maquina

                # Tecla R = remover máquina
                elif evento.key == pygame.K_r and grid[lin][col]:
                    maquina = grid[lin][col]
                    game.maquinas.append(maquina)
                    for dl in range(2):
                        for dc in range(2):
                            if lin + dl < GRID_LINHAS and col + dc < GRID_COLUNAS and grid[lin + dl][col + dc] == maquina:
                                grid[lin + dl][col + dc] = None

        desenhar_interface(game, grid, personagem_pos)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
