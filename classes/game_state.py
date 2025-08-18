import random
from classes.pedido import Pedido
from classes.maquina import Maquina

class GameState:
    def __init__(self):
        self.turno = 1
        self.tempo_turno = 60
        self.tempo_restante = self.tempo_turno
        self.dinheiro = 500
        self.estoque = {}
        self.maquinas = []
        self.pedidos = []
        self.reputacao = 100
        self.game_over = False

        self.loja_maquinas = [
            {"tipo": "pecaA", "custo": 200, "producao": 2, "custo_energia": 10, "largura": 2, "altura": 2},
            {"tipo": "pecaB", "custo": 400, "producao": 3, "custo_energia": 20, "largura": 3, "altura": 2},
            {"tipo": "pecaC", "custo": 600, "producao": 5, "custo_energia": 35, "largura": 2, "altura": 3}
        ]

    def comprar_maquina(self):
        maquina = Maquina("pecaA", 2, 200)
        if self.dinheiro >= maquina.custo:
            self.maquinas.append(maquina)
            self.dinheiro -= maquina.custo

    def gerar_pedido(self):
        tipo = "pecaA"
        quantidade = random.randint(3, 6)
        prazo = random.randint(2, 4)
        self.pedidos.append(Pedido(tipo, quantidade, prazo))

    def comprar_maquina_loja(self, modelo):
        if len(self.maquinas) >= 4:
            return
        if self.dinheiro >= modelo["custo"]:
            self.maquinas.append(Maquina(
                modelo["tipo"], 
                modelo["producao"], 
                modelo["custo"],  
                modelo["custo_energia"],
                modelo["largura"],
                modelo["altura"]
            ))
            self.dinheiro -= modelo["custo"]

    def processar_turno(self, grid):
        custo_total_energia = 0
        maquinas_contadas = set()
        for i, linha in enumerate(grid):
            for j, maquina in enumerate(linha):
                if maquina and maquina not in maquinas_contadas:
                    maquinas_contadas.add(maquina)
                    tipo = maquina.tipo
                    if tipo not in self.estoque:
                        self.estoque[tipo] = 0
                    self.estoque[tipo] += maquina.producao
                    custo_total_energia += maquina.custo_energia

        # Atualiza pedidos, tenta entregar, e aplica reputação
        for pedido in self.pedidos:
            if not pedido.entregue:
                pedido.atualizar()
                if pedido.tentar_entrega(self.estoque):
                    self.dinheiro += pedido.quantidade * 15

        # Aplica penalidade para pedidos que venceram e não foram entregues
        pedidos_a_remover = []
        for pedido in self.pedidos:
            if pedido.entregue:
                pedidos_a_remover.append(pedido)  # Remove entregues
            elif pedido.prazo <= 0 and not pedido.entregue:
                if self.reputacao >= -100:
                    self.reputacao -= 10  # Penalidade de reputação
                pedidos_a_remover.append(pedido)

        # Remove pedidos finalizados (entregues ou vencidos)
        for pedido in pedidos_a_remover:
            self.pedidos.remove(pedido)

        self.dinheiro -= custo_total_energia
        if self.dinheiro <= -100:
            self.game_over = True

        self.tempo_restante = self.tempo_turno
        self.turno += 1

        if len(self.pedidos) < 3:
            self.gerar_pedido()
