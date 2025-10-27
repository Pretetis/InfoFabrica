import random
from classes.maquina import Maquina

class GameState:
    def __init__(self):
        self.turno = 1
        self.tempo_restante = 60
        self.dinheiro = 100000
        self.reputacao = 150
        self.estoque = {}
        self.pedidos = []
        self.maquinas = []
        self.loja_maquinas = [
            {"tipo": "Motor V1", "producao": 5, "custo": 300, "custo_energia": 10, "largura": 1, "altura": 1},
            {"tipo": "Chassi Básico", "producao": 2, "custo": 500, "custo_energia": 15, "largura": 1, "altura": 1},
        ]
        self.estado_jogo = 'JOGANDO'

        # --- NOVA LÓGICA DE SLOTS DA FÁBRICA ---
        # Dicionário para armazenar os slots comprados no formato (linha, col): "tipo_do_slot"
        self.owned_slots = {}
        
        # Loja de slots que podem ser comprados
        self.loja_slots = {
            "superior": {"custo": 500},
            "baixo": {"custo": 500},
            "esquerda": {"custo": 500},
            "direita": {"custo": 500},
            "doca": {"custo": 1200},
        }
        
        self._initialize_starting_factory()

    def _initialize_starting_factory(self):
        # O jogador começa no slot (0, 0) do grid infinito com o tipo "meio"
        # self.owned_slots[(0, 0)] = "meio" # Original
        
        # --- NOVO (Request 2) ---
        self.owned_slots[(0, 0)] = "doca"    # Slot de Doca
        self.owned_slots[(1, 0)] = "meio"     # Slot Meio (Abaixo da doca)
        self.owned_slots[(1, 1)] = "meio"     # Slot Meio (Abaixo do (0,0))
        self.owned_slots[(0, 1)] = "meio"     # Slot Meio (À direita do (0,0))
        # -------------------------


    def expandir_fabrica(self, slot_row, slot_col, slot_type):
        if slot_type not in self.loja_slots:
            print(f"Tipo de slot '{slot_type}' inválido.")
            return False

        custo = self.loja_slots[slot_type]["custo"]
        if (slot_row, slot_col) in self.owned_slots:
            print("Slot já comprado.")
            return False

        if self.dinheiro < custo:
            print("Dinheiro insuficiente.")
            return False

        # Verifica se o slot a ser comprado é adjacente a um já possuído
        adjacente = False
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # Cima, Baixo, Esquerda, Direita
            if (slot_row + dr, slot_col + dc) in self.owned_slots:
                adjacente = True
                break
        
        if adjacente:
            self.dinheiro -= custo
            self.owned_slots[(slot_row, slot_col)] = slot_type
            print(f"Slot '{slot_type}' comprado em ({slot_row}, {slot_col})!")
            return True
        
        print("A expansão deve ser adjacente a um slot existente.")
        return False

    def produzir_nas_maquinas(self, grid):
        # --- MODIFICADO (Request 1) ---
        # A lógica de produção foi movida para a classe Caminhao
        # para garantir que só ocorra quando o turno avançar.
        # Esta função ainda é chamada pelo caminhão, está correto.
        print("Produzindo em todas as máquinas...")
        for (r, c), maquinas_na_celula in grid.items():
            for maquina in maquinas_na_celula:
                 if isinstance(maquina, Maquina):
                    # --- CORREÇÃO: REVERTIDO PARA A LÓGICA ORIGINAL ---
                    # A produção agora fica "na máquina" esperando o jogador pegar.
                    maquina.produzir()


    def avancar_turno(self):
        self.turno += 1
        self.tempo_restante = 60
        self.gerar_pedido()
        print(f"Iniciando Turno {self.turno}")

    def gerar_pedido(self):
        class Pedido:
            def __init__(self, tipo, quantidade, prazo):
                self.tipo, self.quantidade, self.prazo, self.entregue = tipo, quantidade, prazo, False
        
        modelo_maquina = random.choice(self.loja_maquinas)
        tipo_peca = modelo_maquina["tipo"]
        quantidade = random.randint(5, 20)
        prazo = self.turno + random.randint(5, 10)
        self.pedidos.append(Pedido(tipo_peca, quantidade, prazo))