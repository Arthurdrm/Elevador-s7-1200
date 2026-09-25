"""Modelo Físico e Cinemático do Elevador Industrial de Carga.
Simula movimento da cabine, tração por cabo, abertura de portas e acionamento de fins de curso.
"""

import math
from typing import Tuple

class ElevatorPhysics:
    def __init__(self):
        # Dimensões e cinemática
        self.course_height_m: float = 4.5       # Distância entre o 1º e 2º pavimento (metros)
        self.speed_mps: float = 0.8             # Velocidade nominal do elevador (m/s)
        self.pos_y_m: float = 0.0               # Posição atual da cabine em metros (0.0 = Andar 1, 4.5 = Andar 2)
        
        # Dinâmica das portas (0.0 = Totalmente fechada, 1.0 = Totalmente aberta)
        self.door_1_open_ratio: float = 0.0     # Porta do 1º pavimento
        self.door_2_open_ratio: float = 0.0     # Porta do 2º pavimento
        self.door_speed: float = 0.8            # Velocidade de abertura/fechamento (por segundo)
        self.door_1_target_open: bool = False   # Solicitação de abertura porta 1
        self.door_2_target_open: bool = False   # Solicitação de abertura porta 2

        # Rotação da polia do guincho/motorredutor (graus)
        self.pulley_angle_deg: float = 0.0
        self.pulley_diameter_m: float = 0.4     # Diâmetro da polia tracionadora

        # Tolerância mecânica de acionamento do fim de curso (em metros)
        self.sensor_margin_m: float = 0.08

    @property
    def position_percent(self) -> float:
        """Retorna a posição da cabine em percentual (0.0% a 100.0%)."""
        return max(0.0, min(100.0, (self.pos_y_m / self.course_height_m) * 100.0))

    def step(self, dt: float, motor_sobe: bool, motor_desce: bool, 
             tranca_1: bool, tranca_2: bool) -> Tuple[bool, bool, bool, bool]:
        """Avança a simulação física por um intervalo de tempo dt.
        
        Retorna os estados físicos elétricos das 4 chaves para alimentar o CLP:
        - fim_de_curso_cabine_1 (NF: False quando cabine aciona a chave, True em repouso)
        - fim_de_curso_porta_1  (NA: True quando porta fechada, False quando aberta)
        - fim_de_curso_cabine_2 (NF: False quando cabine aciona a chave, True em repouso)
        - fim_de_curso_porta_2  (NA: True quando porta fechada, False quando aberta)
        """
        # 1. MOVIMENTAÇÃO DA CABINE POR TRAÇÃO A CABO
        if motor_sobe and not motor_desce:
            self.pos_y_m += self.speed_mps * dt
            if self.pos_y_m > self.course_height_m:
                self.pos_y_m = self.course_height_m
            # Rotação horária da polia (+)
            rot_delta = (self.speed_mps * dt / (math.pi * self.pulley_diameter_m)) * 360.0
            self.pulley_angle_deg = (self.pulley_angle_deg + rot_delta) % 360.0

        elif motor_desce and not motor_sobe:
            self.pos_y_m -= self.speed_mps * dt
            if self.pos_y_m < 0.0:
                self.pos_y_m = 0.0
            # Rotação anti-horária da polia (-)
            rot_delta = (self.speed_mps * dt / (math.pi * self.pulley_diameter_m)) * 360.0
            self.pulley_angle_deg = (self.pulley_angle_deg - rot_delta) % 360.0

        # 2. DINÂMICA DAS PORTAS (Respeitando as Trancas Magnéticas)
        # Se a tranca magnética estiver energizada (trancada), a porta não pode abrir
        if tranca_1:
            self.door_1_target_open = False  # Força travamento
        if tranca_2:
            self.door_2_target_open = False  # Força travamento

        # Animação suave da porta 1
        if self.door_1_target_open and not tranca_1:
            self.door_1_open_ratio = min(1.0, self.door_1_open_ratio + self.door_speed * dt)
        else:
            self.door_1_open_ratio = max(0.0, self.door_1_open_ratio - self.door_speed * dt)

        # Animação suave da porta 2
        if self.door_2_target_open and not tranca_2:
            self.door_2_open_ratio = min(1.0, self.door_2_open_ratio + self.door_speed * dt)
        else:
            self.door_2_open_ratio = max(0.0, self.door_2_open_ratio - self.door_speed * dt)

        # 3. LEITURA DOS SENSORES FÍSICOS REAIS
        # Fim de curso da cabine 1 (NF): acionado quando no 1º pavimento (pos_y <= margin)
        # Em repouso (cabine ausente) = True. Quando acionado pela cabine = False.
        cabine_no_1 = self.pos_y_m <= self.sensor_margin_m
        fc_cabine_1 = not cabine_no_1

        # Fim de curso da cabine 2 (NF): acionado quando no 2º pavimento (pos_y >= course - margin)
        cabine_no_2 = self.pos_y_m >= (self.course_height_m - self.sensor_margin_m)
        fc_cabine_2 = not cabine_no_2

        # Fim de curso das portas (NA): acionado quando a porta fecha completamente (ratio < 0.05)
        # Aberta = False (0V). Fechada = True (24V).
        fc_porta_1 = self.door_1_open_ratio < 0.05
        fc_porta_2 = self.door_2_open_ratio < 0.05

        return fc_cabine_1, fc_porta_1, fc_cabine_2, fc_porta_2

    def toggle_porta_1(self, tranca_1: bool) -> Tuple[bool, str]:
        """Tenta abrir/fechar a porta do 1º andar respeitando a tranca magnética."""
        if not self.door_1_target_open:
            # Deseja abrir
            if tranca_1:
                return False, "❌ Tranca magnética ativada! Impossível abrir a porta 1."
            self.door_1_target_open = True
            return True, "🚪 Abrindo porta do 1º pavimento."
        else:
            # Deseja fechar
            self.door_1_target_open = False
            return True, "🚪 Fechando porta do 1º pavimento."

    def toggle_porta_2(self, tranca_2: bool) -> Tuple[bool, str]:
        """Tenta abrir/fechar a porta do 2º andar respeitando a tranca magnética."""
        if not self.door_2_target_open:
            # Deseja abrir
            if tranca_2:
                return False, "❌ Tranca magnética ativada! Impossível abrir a porta 2."
            self.door_2_target_open = True
            return True, "🚪 Abrindo porta do 2º pavimento."
        else:
            # Deseja fechar
            self.door_2_target_open = False
            return True, "🚪 Fechando porta do 2º pavimento."
