import random
from classes.maquina import Maquina

class GameState:
    def __init__(self):
        self.turno = 1
        self.tempo_restante = 60
        self.dinheiro = 1500
        self.reputacao = 150
        self.estoque = {}
        self.pedidos = []
        self.maquinas = []
        
        self.loja_maquinas = [
            {
                "nome": "Fábrica M1 (Motor)",
                "tipo": "Motor V1",
                "producao": 5, 
                "custo": 300, 
                "custo_energia": 10, 
                "largura": 1, "altura": 1,
                "anim_key": "M1"
            },
            {
                "nome": "Fábrica M2 (Chassi)",
                "tipo": "Chassi Básico",
                "producao": 2, 
                "custo": 500, 
                "custo_energia": 15, 
                "largura": 1, "altura": 1,
                "anim_key": "M2"
            },
            {
                "nome": "Fábrica M3",
                "tipo": "Motor V1",
                "producao": {"Motor V1": 7, "Chassi Básico": 3},
                "custo": 1500, 
                "custo_energia": 25, 
                "largura": 1, "altura": 1,
                "anim_key": "M3"
            },
        ]

        self.estado_jogo = 'JOGANDO' 

        self.owned_slots = {}

        self.loja_slots = {
            "meio": {"custo": 500}
                            }
        
        self._initialize_starting_factory()
    
    def _initialize_starting_factory(self):
        self.owned_slots[(0, 0)] = "doca"    
        self.owned_slots[(1, 0)] = "meio"     
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

    def checar_penalidades_e_gameover(self):
        print(f"Analisando penalidades do Turno {self.turno}")
        for pedido in self.pedidos:
            if not pedido.entregue and not pedido.penalizado and self.turno > pedido.prazo:
                self.reputacao -= 20
                pedido.penalizado = True
                pedido.turno_conclusao = self.turno 
                print(f"PEDIDO ATRASADO: {pedido.quantidade}x {pedido.tipo}. Reputação: -20 (Total: {self.reputacao})")

        if self.reputacao <= -20:
            self.estado_jogo = 'GAME_OVER'
            print("GAME OVER! Reputação muito baixa.")
            return True 
        
        return False 

    def avancar_turno(self):
        self.pedidos = [p for p in self.pedidos if p.turno_conclusao is None]
        # ------------------------------------------------------------
        
        self.turno += 1
        self.tempo_restante = 60
        self.gerar_pedido()
        print(f"Iniciando Turno {self.turno}")

    def gerar_pedido(self):
        class Pedido:
            def __init__(self, tipo, quantidade, prazo):
                self.tipo, self.quantidade, self.prazo = tipo, quantidade, prazo
                self.entregue = False
                self.penalizado = False
                # --- NOVO ATRIBUTO ---
                self.turno_conclusao = None 
        
        modelo_maquina = random.choice(self.loja_maquinas)
        tipo_peca = modelo_maquina["tipo"]
        quantidade = random.randint(5, 20)
        prazo = self.turno + random.randint(2, 6) 
        self.pedidos.append(Pedido(tipo_peca, quantidade, prazo))