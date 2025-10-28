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
        self.estado_jogo = 'JOGANDO' # 'JOGANDO', 'CAMINHAO_PARTINDO', 'GAME_OVER'

        self.owned_slots = {}
        
        self.loja_slots = {
            "superior": {"custo": 500},
            "baixo": {"custo": 500},
            "esquerda": {"custo": 500},
            "direita": {"custo": 500},
        }
        
        self._initialize_starting_factory()

    def _initialize_starting_factory(self):
        self.owned_slots[(1, 0)] = "doca"    
        self.owned_slots[(0, 0)] = "meio"     
        self.owned_slots[(0, 1)] = "meio"     
        self.owned_slots[(1, 1)] = "meio"     



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

        adjacente = False
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: 
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
        print("Produzindo em todas as máquinas...")
        for (r, c), maquinas_na_celula in grid.items():
            for maquina in maquinas_na_celula:
                 if isinstance(maquina, Maquina):
                    maquina.produzir()

    # --- NOVO MÉTODO ---
    def checar_penalidades_e_gameover(self):
        """Verifica pedidos atrasados, aplica penalidades e checa condição de Game Over."""
        print(f"Analisando penalidades do Turno {self.turno}")

        # 1. Checar pedidos atrasados (antes de incrementar o turno)
        for pedido in self.pedidos:
            # Se o pedido não foi entregue, não foi penalizado, e o prazo estourou
            if not pedido.entregue and not pedido.penalizado and self.turno > pedido.prazo:
                self.reputacao -= 20
                pedido.penalizado = True # Marca para não penalizar de novo
                print(f"PEDIDO ATRASADO: {pedido.quantidade}x {pedido.tipo}. Reputação: -20 (Total: {self.reputacao})")

        # 2. Checar condição de GAME OVER
        if self.reputacao <= -20:
            self.estado_jogo = 'GAME_OVER'
            print("GAME OVER! Reputação muito baixa.")
            return True # Retorna True se o jogo acabou
        
        return False # Retorna False se o jogo continua


    # --- MÉTODO MODIFICADO (LÓGICA DE PENALIDADE REMOVIDA DAQUI) ---
    def avancar_turno(self):
        """Apenas avança o turno e gera novos pedidos."""
        # A lógica de penalidade e game over foi movida para 'checar_penalidades_e_gameover'
        
        self.turno += 1
        self.tempo_restante = 60
        self.gerar_pedido()
        print(f"Iniciando Turno {self.turno}")

    def gerar_pedido(self):
        class Pedido:
            def __init__(self, tipo, quantidade, prazo):
                self.tipo, self.quantidade, self.prazo = tipo, quantidade, prazo
                self.entregue = False
                self.penalizado = False # <-- Mantém o rastreador de penalidade
        
        modelo_maquina = random.choice(self.loja_maquinas)
        tipo_peca = modelo_maquina["tipo"]
        quantidade = random.randint(5, 20)
        prazo = self.turno + random.randint(5, 10) # Prazo é o NÚMERO do turno final
        self.pedidos.append(Pedido(tipo_peca, quantidade, prazo))