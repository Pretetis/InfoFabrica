class Maquina:
    def __init__(self, tipo, producao, custo, custo_energia=10, largura=2, altura=2):
        self.tipo = tipo
        self.producao = producao
        self.custo = custo
        self.custo_energia = custo_energia
        self.largura = largura
        self.altura = altura
    def produzir(self):
        return {self.tipo: self.producao}