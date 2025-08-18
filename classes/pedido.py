class Pedido:
    def __init__(self, tipo, quantidade, prazo):
        self.tipo = tipo
        self.quantidade = quantidade
        self.prazo = prazo
        self.entregue = False

    def atualizar(self):
        if self.prazo > 0:
            self.prazo -= 1

    def tentar_entrega(self, estoque):
        if estoque.get(self.tipo, 0) >= self.quantidade:
            estoque[self.tipo] -= self.quantidade
            self.entregue = True
            return True
        return False
