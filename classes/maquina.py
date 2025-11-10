# [classes/maquina.py]

class Maquina:
    def __init__(self, tipo, producao, custo, custo_energia, largura, altura, animacao=None):
        
        # 'producao' agora pode ser um DICIONÁRIO
        # Se for um int (como nas máquinas M1 e M2), nós o convertemos para um dict
        if isinstance(producao, int):
            # Converte int para dict: {tipo_principal: producao_int}
            self.producao_map = {tipo: producao}
        else:
            # Se já for um dict (como na M3), apenas o usamos
            self.producao_map = producao # Ex: {"Motor V1": 5, "Chassi Básico": 3}
        
        self.custo, self.custo_energia = custo, custo_energia
        self.largura, self.altura = largura, altura
        
        # 'pecas_para_coletar' agora é um DICIONÁRIO
        # Inicializamos com 0 para cada tipo que a máquina pode produzir
        self.pecas_para_coletar = {}
        for item_tipo in self.producao_map:
            self.pecas_para_coletar[item_tipo] = 0
            
        # 'self.tipo' agora é o item "principal", usado para o ícone padrão
        # Pegamos o primeiro item da lista de produção
        self.tipo = list(self.producao_map.keys())[0]

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
    
    def produzir(self): 
        # Nova lógica de produção: itera sobre o mapa de produção
        for item_tipo, quantidade in self.producao_map.items():
            self.pecas_para_coletar[item_tipo] = self.pecas_para_coletar.get(item_tipo, 0) + quantidade