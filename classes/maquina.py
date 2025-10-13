class Maquina:
    def __init__(self, tipo, producao, custo, custo_energia=10, largura=2, altura=2, animacao=None):
        self.tipo = tipo
        self.producao = producao
        self.custo = custo
        self.custo_energia = custo_energia
        self.largura = largura
        self.altura = altura
        self.animacao = animacao if animacao else []
        self.frame_atual = 0
        self.tempo_animacao = 0
        self.pecas_para_coletar = 0


    def produzir(self):
        self.pecas_para_coletar += self.producao

    def update_animation(self, dt):
        self.tempo_animacao += dt
        if self.tempo_animacao > 0.2:  # Mude o valor para controlar a velocidade da animação
            self.tempo_animacao = 0
            self.frame_atual = (self.frame_atual + 1) % len(self.animacao)

    def get_current_frame(self):
        if self.animacao:
            return self.animacao[self.frame_atual]
        return None