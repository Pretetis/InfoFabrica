class Maquina:
    # (Sem alterações)
    def __init__(self, tipo, producao, custo, custo_energia, largura, altura, animacao=None):
        self.tipo, self.producao, self.custo, self.custo_energia = tipo, producao, custo, custo_energia
        self.largura, self.altura = largura, altura
        self.pecas_para_coletar = 0
        self.pos_lin, self.pos_col = -1, -1
        self.animation_frames = animacao
        self.current_frame_index, self.animation_timer, self.animation_speed = 0, 0, 0.15
    def update_animation(self, dt):
        if not self.animation_frames: return
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
    def get_current_frame(self):
        return self.animation_frames[self.current_frame_index] if self.animation_frames else None
    def produzir(self): self.pecas_para_coletar += self.producao