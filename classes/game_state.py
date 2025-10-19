import random

from classes.maquina import Maquina

class GameState:
    def __init__(self):
        self.turno = 1
        self.tempo_restante = 60
        self.dinheiro = 1000
        self.reputacao = 150
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
        self.gerar_pedido()
        print(f"Iniciando Turno {self.turno}")

    def gerar_pedido(self):
            class Pedido:
                def __init__(self, tipo, quantidade, prazo):
                    self.tipo, self.quantidade, self.prazo, self.entregue = tipo, quantidade, prazo, False
            
            # Escolhe um tipo de peça aleatório da loja
            modelo_maquina = random.choice(self.loja_maquinas)
            tipo_peca = modelo_maquina["tipo"]
            
            # Gera quantidade e prazo aleatórios
            quantidade = random.randint(5, 20)
            prazo = self.turno + random.randint(5, 10)

            self.pedidos.append(Pedido(tipo_peca, quantidade, prazo))


