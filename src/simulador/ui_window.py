"""Interface Gráfica HMI / SCADA para Simulação do Elevador Siemens S7-1200.
Desenvolvida com PySide6 e componentes visuais industriais para o Desafio SENAI.
"""

import sys
import time
import math
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen, QLinearGradient, QRadialGradient, QPolygonF
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTextEdit, QFrame, QGroupBox, QSplitter, QProgressBar
)

from src.simulador.plc_s7_1200 import PLCS71200Elevador
from src.simulador.elevator_physics import ElevatorPhysics


class ElevatorGraphicWidget(QWidget):
    """Widget de renderização vetorial industrial do poço do elevador e edificação."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(460, 580)
        self.pos_percent: float = 0.0
        self.door_1_ratio: float = 0.0
        self.door_2_ratio: float = 0.0
        self.motor_sobe: bool = False
        self.motor_desce: bool = False
        self.tranca_1: bool = False
        self.tranca_2: bool = True
        self.pulley_angle: float = 0.0
        self.fc_cabine_1: bool = False
        self.fc_cabine_2: bool = True

    def update_states(self, pos_perc: float, d1_ratio: float, d2_ratio: float,
                      m_sobe: bool, m_desce: bool, t1: bool, t2: bool,
                      angle: float, fc1: bool, fc2: bool):
        self.pos_percent = pos_perc
        self.door_1_ratio = d1_ratio
        self.door_2_ratio = d2_ratio
        self.motor_sobe = m_sobe
        self.motor_desce = m_desce
        self.tranca_1 = t1
        self.tranca_2 = t2
        self.pulley_angle = angle
        self.fc_cabine_1 = fc1
        self.fc_cabine_2 = fc2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Fundo do pavilhão industrial
        painter.fillRect(0, 0, w, h, QColor(24, 27, 33))

        # Dimensões da torre/poço do elevador
        shaft_x = int(w * 0.32)
        shaft_w = int(w * 0.38)
        roof_h = 75
        floor_h = 30
        bottom_y = h - floor_h
        shaft_y = roof_h
        travel_h = bottom_y - shaft_y - 95  # altura útil de percurso da cabine

        # 1. EDIFICAÇÃO / ANDARES DA FÁBRICA DE CALÇADOS
        # Divisão entre 1º e 2º pavimento
        mid_floor_y = shaft_y + int(travel_h * 0.52)

        # Paredes laterais do prédio
        painter.setPen(Qt.NoPen)
        # 2º Pavimento (Piso superior)
        painter.setBrush(QBrush(QColor(36, 42, 52)))
        painter.drawRect(10, shaft_y, shaft_x - 10, mid_floor_y - shaft_y)
        painter.drawRect(shaft_x + shaft_w, shaft_y, w - (shaft_x + shaft_w) - 10, mid_floor_y - shaft_y)

        # 1º Pavimento (Térreo)
        painter.setBrush(QBrush(QColor(30, 35, 44)))
        painter.drawRect(10, mid_floor_y + 15, shaft_x - 10, bottom_y - mid_floor_y - 15)
        painter.drawRect(shaft_x + shaft_w, mid_floor_y + 15, w - (shaft_x + shaft_w) - 10, bottom_y - mid_floor_y - 15)

        # Lajes de concreto
        painter.setBrush(QBrush(QColor(60, 68, 80)))
        # Laje intermediária (Piso do 2º andar)
        painter.drawRect(5, mid_floor_y, shaft_x - 5, 16)
        painter.drawRect(shaft_x + shaft_w, mid_floor_y, w - (shaft_x + shaft_w) - 5, 16)
        # Laje térrea de fundação
        painter.drawRect(5, bottom_y, w - 10, floor_h)

        # Rótulos dos Pavimentos
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(QColor(160, 175, 195))
        painter.drawText(15, shaft_y + 22, "2º PAVIMENTO")
        painter.drawText(15, shaft_y + 36, "(PRODUÇÃO)")

        painter.drawText(15, mid_floor_y + 35, "1º PAVIMENTO")
        painter.drawText(15, mid_floor_y + 49, "(EXPEDIÇÃO)")

        # 2. CASA DE MÁQUINAS NO TOPO (MOTORREDUTOR & POLIA)
        painter.setBrush(QBrush(QColor(42, 50, 62)))
        painter.setPen(QPen(QColor(80, 95, 115), 2))
        painter.drawRoundedRect(shaft_x - 10, 8, shaft_w + 20, roof_h - 10, 6, 6)

        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QColor(220, 230, 245))
        painter.drawText(shaft_x, 24, "CASA DE MÁQUINAS")

        # Motorredutor
        motor_cx = shaft_x + shaft_w // 2
        motor_cy = 44
        pulley_r = 22

        # Status do Motor
        if self.motor_sobe:
            motor_halo = QColor(46, 204, 113, 100)
            status_txt = "▲ SUBINDO (HORÁRIO)"
            status_col = QColor(46, 204, 113)
        elif self.motor_desce:
            motor_halo = QColor(52, 152, 219, 100)
            status_txt = "▼ DESCENDO (ANTI-HORÁRIO)"
            status_col = QColor(52, 152, 219)
        else:
            motor_halo = QColor(0, 0, 0, 0)
            status_txt = "■ PARADO"
            status_col = QColor(140, 150, 165)

        # Halo luminoso do motor
        painter.setBrush(QBrush(motor_halo))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(motor_cx, motor_cy), pulley_r + 8, pulley_r + 8)

        # Polia de tração
        pulley_grad = QRadialGradient(motor_cx, motor_cy, pulley_r)
        pulley_grad.setColorAt(0.0, QColor(120, 130, 145))
        pulley_grad.setColorAt(0.8, QColor(70, 80, 90))
        pulley_grad.setColorAt(1.0, QColor(45, 52, 60))
        painter.setBrush(QBrush(pulley_grad))
        painter.setPen(QPen(QColor(180, 190, 205), 2))
        painter.drawEllipse(QPoint(motor_cx, motor_cy), pulley_r, pulley_r)

        # Raios giratórios da polia para indicar rotação real
        painter.setPen(QPen(QColor(230, 235, 240), 2))
        rad = math.radians(self.pulley_angle)
        dx = math.cos(rad) * (pulley_r - 3)
        dy = math.sin(rad) * (pulley_r - 3)
        painter.drawLine(motor_cx - dx, motor_cy - dy, motor_cx + dx, motor_cy + dy)
        dx2 = math.cos(rad + math.pi / 2) * (pulley_r - 3)
        dy2 = math.sin(rad + math.pi / 2) * (pulley_r - 3)
        painter.drawLine(motor_cx - dx2, motor_cy - dy2, motor_cx + dx2, motor_cy + dy2)

        # Eixo central
        painter.setBrush(QBrush(QColor(230, 126, 34)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(motor_cx, motor_cy), 5, 5)

        # Texto do status do motor
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.setPen(status_col)
        painter.drawText(shaft_x + 5, 70, status_txt)

        # 3. POÇO DO ELEVADOR (GUIAIS E ESTRUTURA METÁLICA)
        painter.setBrush(QBrush(QColor(15, 18, 22)))
        painter.setPen(QPen(QColor(50, 60, 72), 2))
        painter.drawRect(shaft_x, shaft_y, shaft_w, bottom_y - shaft_y)

        # Trilhos guias laterais em aço
        painter.setPen(QPen(QColor(85, 95, 110), 3))
        painter.drawLine(shaft_x + 6, shaft_y, shaft_x + 6, bottom_y)
        painter.drawLine(shaft_x + shaft_w - 6, shaft_y, shaft_x + shaft_w - 6, bottom_y)

        # 4. CABOS DE TRAÇÃO DE AÇO
        # Posição Y da cabine (0% = bottom_y - 95, 100% = shaft_y + 10)
        cab_h = 88
        cab_w = shaft_w - 20
        cab_x = shaft_x + 10
        y_bottom_cab = bottom_y - cab_h - 4
        y_top_cab = shaft_y + 12
        cur_cab_y = int(y_bottom_cab - (self.pos_percent / 100.0) * (y_bottom_cab - y_top_cab))

        # Cabo duplo de aço esticado da polia até o topo da cabine
        painter.setPen(QPen(QColor(190, 195, 205), 2))
        painter.drawLine(motor_cx - 4, motor_cy + pulley_r, cab_x + cab_w // 2 - 4, cur_cab_y)
        painter.drawLine(motor_cx + 4, motor_cy + pulley_r, cab_x + cab_w // 2 + 4, cur_cab_y)

        # 5. CABINE DO ELEVADOR INDUSTRIAL DE CARGA
        # Estrutura metálica externa
        cab_grad = QLinearGradient(cab_x, cur_cab_y, cab_x + cab_w, cur_cab_y)
        cab_grad.setColorAt(0.0, QColor(70, 80, 95))
        cab_grad.setColorAt(0.5, QColor(105, 118, 135))
        cab_grad.setColorAt(1.0, QColor(70, 80, 95))
        painter.setBrush(QBrush(cab_grad))
        painter.setPen(QPen(QColor(160, 175, 195), 2))
        painter.drawRoundedRect(cab_x, cur_cab_y, cab_w, cab_h, 4, 4)

        # Interior da cabine (iluminado)
        painter.setBrush(QBrush(QColor(225, 215, 180, 80)))
        painter.drawRect(cab_x + 6, cur_cab_y + 8, cab_w - 12, cab_h - 16)

        # Faixas zebradas de segurança industrial no rodapé da cabine
        stripe_h = 10
        stripe_y = cur_cab_y + cab_h - stripe_h - 2
        for s_idx in range(0, cab_w - 8, 12):
            col = QColor(241, 196, 15) if (s_idx // 12) % 2 == 0 else QColor(20, 20, 20)
            painter.fillRect(cab_x + 4 + s_idx, stripe_y, 12, stripe_h, col)

        # Carga útil na cabine: Caixas da fábrica de calçados
        box_y = cur_cab_y + cab_h - 38
        painter.setBrush(QBrush(QColor(160, 110, 60)))
        painter.setPen(QPen(QColor(110, 70, 30), 1))
        painter.drawRect(cab_x + 14, box_y, 34, 24)
        painter.drawRect(cab_x + cab_w - 48, box_y, 34, 24)
        painter.setFont(QFont("Segoe UI", 6, QFont.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(cab_x + 16, box_y + 14, "CALÇADOS")
        painter.drawText(cab_x + cab_w - 46, box_y + 14, "COURO")

        # 6. SENSORES FIM DE CURSO DE POSIÇÃO DA CABINE (NF)
        # Fim de curso 2º Pavimento (Topo) - I0.6
        fc2_y = y_top_cab + 35
        self._draw_limit_switch(
            painter, shaft_x - 14, fc2_y, 
            is_actuated=(not self.fc_cabine_2), 
            label="I0.6 FC Cabine 2 (NF)"
        )

        # Fim de curso 1º Pavimento (Fundo) - I0.2
        fc1_y = y_bottom_cab + 35
        self._draw_limit_switch(
            painter, shaft_x - 14, fc1_y, 
            is_actuated=(not self.fc_cabine_1), 
            label="I0.2 FC Cabine 1 (NF)"
        )

        # 7. PORTAS DE CORRER INDUSTRIAIS E TRANCA MAGNÉTICA
        # Porta do 2º Pavimento
        d2_y = shaft_y + 10
        d2_h = cab_h + 4
        self._draw_door_and_lock(
            painter, shaft_x, d2_y, shaft_w, d2_h, 
            self.door_2_ratio, self.tranca_2, 
            "Q0.3 Tranca 2", "I0.7 Porta 2"
        )

        # Porta do 1º Pavimento
        d1_y = bottom_y - d2_h - 2
        self._draw_door_and_lock(
            painter, shaft_x, d1_y, shaft_w, d2_h, 
            self.door_1_ratio, self.tranca_1, 
            "Q0.2 Tranca 1", "I0.3 Porta 1"
        )

    def _draw_limit_switch(self, painter: QPainter, x: int, y: int, is_actuated: bool, label: str):
        """Desenha uma chave fim de curso industrial com rolete mecânico."""
        # Corpo da chave
        painter.setBrush(QBrush(QColor(40, 48, 58)))
        painter.setPen(QPen(QColor(100, 115, 130), 1))
        painter.drawRoundedRect(x - 18, y - 10, 18, 20, 2, 2)

        # Rolete / Haste mecânica
        lever_color = QColor(231, 76, 60) if is_actuated else QColor(140, 150, 160)
        painter.setPen(QPen(lever_color, 3))
        if is_actuated:
            # Pressionado pela cabine (deletado)
            painter.drawLine(x, y, x + 8, y + 4)
            painter.setBrush(QBrush(QColor(231, 76, 60)))
            painter.drawEllipse(QPoint(x + 8, y + 4), 3, 3)
        else:
            # Em repouso
            painter.drawLine(x, y, x + 12, y)
            painter.setBrush(QBrush(QColor(180, 190, 200)))
            painter.drawEllipse(QPoint(x + 12, y), 3, 3)

        # LED indicador de contato
        led_color = QColor(46, 204, 113) if not is_actuated else QColor(231, 76, 60)
        painter.setBrush(QBrush(led_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(x - 9, y), 3, 3)

        # Texto
        painter.setFont(QFont("Segoe UI", 6))
        painter.setPen(QColor(180, 195, 210))
        painter.drawText(x - 110, y + 4, label)

    def _draw_door_and_lock(self, painter: QPainter, x: int, y: int, w: int, h: int,
                            open_ratio: float, is_locked: bool, lock_label: str, door_label: str):
        """Desenha porta industrial bi-partida e eletroímã da tranca magnética."""
        door_w = int((w // 2) * (1.0 - open_ratio))

        # Folha esquerda da porta
        p_left = QLinearGradient(x, y, x + door_w, y)
        p_left.setColorAt(0.0, QColor(90, 100, 115, 230))
        p_left.setColorAt(1.0, QColor(70, 80, 92, 230))
        painter.setBrush(QBrush(p_left))
        painter.setPen(QPen(QColor(130, 145, 165), 1))
        painter.drawRect(x, y, door_w, h)

        # Folha direita da porta
        p_right = QLinearGradient(x + w - door_w, y, x + w, y)
        p_right.setColorAt(0.0, QColor(70, 80, 92, 230))
        p_right.setColorAt(1.0, QColor(90, 100, 115, 230))
        painter.setBrush(QBrush(p_right))
        painter.drawRect(x + w - door_w, y, door_w, h)

        # Tranca Magnética (Eletroímã no batente superior direito)
        lx = x + w + 4
        ly = y + 8
        lock_color = QColor(231, 76, 60) if is_locked else QColor(46, 204, 113)
        lock_txt = "TRANCADA" if is_locked else "LIVRE"

        painter.setBrush(QBrush(QColor(35, 42, 50)))
        painter.setPen(QPen(lock_color, 2))
        painter.drawRoundedRect(lx, ly, 45, 30, 3, 3)

        painter.setBrush(QBrush(lock_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(lx + 8, ly + 15), 4, 4)

        painter.setFont(QFont("Segoe UI", 6, QFont.Bold))
        painter.setPen(lock_color)
        painter.drawText(lx + 15, ly + 14, "TRAVA")
        painter.drawText(lx + 15, ly + 24, lock_txt)

        # Etiqueta da tranca e da porta
        painter.setFont(QFont("Segoe UI", 6))
        painter.setPen(QColor(150, 165, 185))
        painter.drawText(lx + 4, ly + 40, lock_label)
        painter.drawText(lx + 4, ly + 50, door_label)


class MainWindowSimuladorElevador(QMainWindow):
    """Janela Principal com Interface de Controle, Sinótico e Monitor SCADA."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador do Elevador Industrial S7-1200 - AutoControl")
        self.resize(1200, 820)
        self.setMinimumSize(1080, 720)

        # Núcleo de simulação e CLP
        self.plc = PLCS71200Elevador()
        self.physics = ElevatorPhysics()

        # Configuração do timer de ciclo em tempo real (50ms = 20Hz)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._simulation_step)
        self.last_time = time.time()

        self._init_ui()
        self._apply_dark_theme()
        self.timer.start(50)

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # -------------------------------------------------------------
        # COLUNA ESQUERDA: Sinótico Gráfico do Prédio e Elevador
        # -------------------------------------------------------------
        left_box = QGroupBox("SINÓTICO INDUSTRIAL - EDIFICAÇÃO DE DOIS PAVIMENTOS")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(8, 12, 8, 8)

        self.graphic_widget = ElevatorGraphicWidget(self)
        left_layout.addWidget(self.graphic_widget)

        # Barra de status de posição
        pos_layout = QHBoxLayout()
        pos_lbl = QLabel("Altura da Cabine:")
        pos_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_pos_val = QLabel("0.00 m (1º Pavimento - 0.0%)")
        self.lbl_pos_val.setFont(QFont("Segoe UI", 9))
        self.lbl_pos_val.setStyleSheet("color: #00e5ff; font-weight: bold;")
        pos_layout.addWidget(pos_lbl)
        pos_layout.addWidget(self.lbl_pos_val)
        pos_layout.addStretch()
        left_layout.addLayout(pos_layout)

        main_layout.addWidget(left_box, stretch=5)

        # -------------------------------------------------------------
        # COLUNA DIREITA: Comandos, Diagnóstico e Tabela de I/O
        # -------------------------------------------------------------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 1. Painel de Botoeiras dos Andares (Controles Físicos do Aluno)
        ctrl_group = QGroupBox("PAINÉIS DE COMANDO EXTERNOS (ENTRADAS DO USUÁRIO)")
        ctrl_grid = QGridLayout(ctrl_group)
        ctrl_grid.setSpacing(8)

        # Pavimento 2
        p2_lbl = QLabel("2º PAVIMENTO:")
        p2_lbl.setStyleSheet("font-weight: bold; color: #a0c0e0;")
        self.btn_sobe_2 = QPushButton("▲ Botão Sobe 2 (%I0.4)")
        self.btn_desce_2 = QPushButton("▼ Botão Desce 2 (%I0.5)")
        self.btn_porta_2 = QPushButton("🚪 Abrir/Fechar Porta 2")

        self.btn_sobe_2.pressed.connect(lambda: self._set_button("sobe_2", True))
        self.btn_sobe_2.released.connect(lambda: self._set_button("sobe_2", False))
        self.btn_desce_2.pressed.connect(lambda: self._set_button("desce_2", True))
        self.btn_desce_2.released.connect(lambda: self._set_button("desce_2", False))
        self.btn_porta_2.clicked.connect(self._toggle_porta_2)

        ctrl_grid.addWidget(p2_lbl, 0, 0)
        ctrl_grid.addWidget(self.btn_sobe_2, 0, 1)
        ctrl_grid.addWidget(self.btn_desce_2, 0, 2)
        ctrl_grid.addWidget(self.btn_porta_2, 0, 3)

        # Pavimento 1
        p1_lbl = QLabel("1º PAVIMENTO:")
        p1_lbl.setStyleSheet("font-weight: bold; color: #a0c0e0;")
        self.btn_sobe_1 = QPushButton("▲ Botão Sobe 1 (%I0.0)")
        self.btn_desce_1 = QPushButton("▼ Botão Desce 1 (%I0.1)")
        self.btn_porta_1 = QPushButton("🚪 Abrir/Fechar Porta 1")

        self.btn_sobe_1.pressed.connect(lambda: self._set_button("sobe_1", True))
        self.btn_sobe_1.released.connect(lambda: self._set_button("sobe_1", False))
        self.btn_desce_1.pressed.connect(lambda: self._set_button("desce_1", True))
        self.btn_desce_1.released.connect(lambda: self._set_button("desce_1", False))
        self.btn_porta_1.clicked.connect(self._toggle_porta_1)

        ctrl_grid.addWidget(p1_lbl, 1, 0)
        ctrl_grid.addWidget(self.btn_sobe_1, 1, 1)
        ctrl_grid.addWidget(self.btn_desce_1, 1, 2)
        ctrl_grid.addWidget(self.btn_porta_1, 1, 3)

        right_layout.addWidget(ctrl_group)

        # 2. Painel de Diagnóstico & Intertravamentos Operacionais
        diag_group = QGroupBox("DIAGNÓSTICO OPERACIONAL & INTERTRAVAMENTOS (SCADA)")
        diag_layout = QVBoxLayout(diag_group)

        diag_grid = QGridLayout()
        diag_grid.setSpacing(6)

        self.lbl_diag_motor = QLabel("Motor / Contatores: PARADO (K1=0, K2=0)")
        self.lbl_diag_motor.setStyleSheet("color: #a0c0e0; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")
        
        self.lbl_diag_seguranca = QLabel("Segurança NR-12: OK (Portas Fechadas)")
        self.lbl_diag_seguranca.setStyleSheet("color: #2ecc71; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")

        self.lbl_diag_tranca1 = QLabel("Tranca 1: LIVRE (%Q0.2=0)")
        self.lbl_diag_tranca1.setStyleSheet("color: #2ecc71; background: #232730; padding: 4px 8px; border-radius: 4px;")

        self.lbl_diag_tranca2 = QLabel("Tranca 2: TRANCADA (%Q0.3=1)")
        self.lbl_diag_tranca2.setStyleSheet("color: #e74c3c; background: #232730; padding: 4px 8px; border-radius: 4px;")

        diag_grid.addWidget(self.lbl_diag_motor, 0, 0)
        diag_grid.addWidget(self.lbl_diag_seguranca, 0, 1)
        diag_grid.addWidget(self.lbl_diag_tranca1, 1, 0)
        diag_grid.addWidget(self.lbl_diag_tranca2, 1, 1)
        diag_layout.addLayout(diag_grid)

        reset_h = QHBoxLayout()
        self.btn_reset_pos = QPushButton("🔄 Resetar Planta para Posição Inicial (1º Pavimento)")
        self.btn_reset_pos.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; font-weight: bold; padding: 6px;")
        self.btn_reset_pos.clicked.connect(self._reset_position)
        reset_h.addWidget(self.btn_reset_pos)
        diag_layout.addLayout(reset_h)

        right_layout.addWidget(diag_group)

        # 3. Tabela de I/O em Tempo Real
        io_group = QGroupBox("TABELA DE I/O DIGITAL DO CLP SIEMENS S7-1200")
        io_layout = QVBoxLayout(io_group)

        self.io_table = QTableWidget(12, 4)
        self.io_table.setHorizontalHeaderLabels(["Endereço", "Tag TIA Portal", "Descrição", "Estado Lógico"])
        self.io_table.verticalHeader().setVisible(False)
        self.io_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.io_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.io_table.setFixedHeight(210)

        io_tags = [
            ("%I0.0", "Botao_sobe_1", "Botão NA sobe 1º andar", "0"),
            ("%I0.1", "Botao_desce_1", "Botão NA desce 1º andar", "0"),
            ("%I0.2", "Fim_de_curso_da_cabine_1", "Chave NF cabine no 1º andar", "0"),
            ("%I0.3", "Fim_de_curso_da_porta_1", "Chave NA porta 1 fechada", "1"),
            ("%I0.4", "Botao_sobe_2", "Botão NA sobe 2º andar", "0"),
            ("%I0.5", "Botao_desce_2", "Botão NA desce 2º andar", "0"),
            ("%I0.6", "Fim_de_curso_da_cabine_2", "Chave NF cabine no 2º andar", "1"),
            ("%I0.7", "Fim_de_curso_da_porta_2", "Chave NA porta 2 fechada", "1"),
            ("%Q0.0", "Motor_1_sobe", "Motor rotação horária (Subir)", "0"),
            ("%Q0.1", "Motor_1_desce", "Motor rotação anti-horária (Descer)", "0"),
            ("%Q0.2", "Tranca_magnetica_da_porta_1", "Tranca magnética porta 1 (1=Trancada)", "0"),
            ("%Q0.3", "Tranca_magnetica_da_porta_2", "Tranca magnética porta 2 (1=Trancada)", "1"),
        ]

        for row, (addr, tag, desc, val) in enumerate(io_tags):
            self.io_table.setItem(row, 0, QTableWidgetItem(addr))
            self.io_table.setItem(row, 1, QTableWidgetItem(tag))
            self.io_table.setItem(row, 2, QTableWidgetItem(desc))
            val_item = QTableWidgetItem(val)
            val_item.setTextAlignment(Qt.AlignCenter)
            self.io_table.setItem(row, 3, val_item)

        self.io_table.resizeColumnsToContents()
        io_layout.addWidget(self.io_table)
        right_layout.addWidget(io_group)

        # 4. Terminal de Log e Eventos de Varredura
        log_group = QGroupBox("TERMINAL DIAGNÓSTICO / LOG DE EVENTOS DO CLP")
        log_layout = QVBoxLayout(log_group)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setFixedHeight(120)
        self.txt_log.setFont(QFont("Consolas", 8))
        log_layout.addWidget(self.txt_log)
        right_layout.addWidget(log_group)

        main_layout.addWidget(right_panel, stretch=6)

        self._log("🚀 Simulador S7-1200 Elevador inicializado com sucesso!")
        self._log("ℹ️ Conforme a especificação SENAI: Portas fechadas e cabine inicialmente no 1º pavimento.")

    def _set_button(self, name: str, state: bool):
        if name == "sobe_1":
            self.plc.botao_sobe_1 = state
        elif name == "desce_1":
            self.plc.botao_desce_1 = state
        elif name == "sobe_2":
            self.plc.botao_sobe_2 = state
        elif name == "desce_2":
            self.plc.botao_desce_2 = state

    def _toggle_porta_1(self):
        ok, msg = self.physics.toggle_porta_1(self.plc.tranca_magnetica_da_porta_1)
        self._log(msg)

    def _toggle_porta_2(self):
        ok, msg = self.physics.toggle_porta_2(self.plc.tranca_magnetica_da_porta_2)
        self._log(msg)

    def _log(self, msg: str):
        t_str = time.strftime("%H:%M:%S")
        self.txt_log.append(f"[{t_str}] {msg}")

    def _reset_position(self):
        """Reinicializa a planta na condição padrão inicial (1º Pavimento)."""
        self.physics.pos_y_m = 0.0
        self.physics.door_1_open_ratio = 0.0
        self.physics.door_2_open_ratio = 0.0
        self.plc.stat_subindo = False
        self.plc.stat_descendo = False
        self.plc.motor_1_sobe = False
        self.plc.motor_1_desce = False
        self.plc.fim_de_curso_da_cabine_1 = False
        self.plc.fim_de_curso_da_cabine_2 = True
        self.plc.fim_de_curso_da_porta_1 = True
        self.plc.fim_de_curso_da_porta_2 = True
        self.plc.tranca_magnetica_da_porta_1 = False
        self.plc.tranca_magnetica_da_porta_2 = True
        self._log("🔄 [RESET] Elevador reinicializado na posição padrão (1º Pavimento).")

    def _simulation_step(self):
        now = time.time()
        dt = min(0.1, now - self.last_time)
        self.last_time = now

        # 1. Passo de Física
        fc1, fp1, fc2, fp2 = self.physics.step(
            dt, 
            self.plc.motor_1_sobe, 
            self.plc.motor_1_desce,
            self.plc.tranca_magnetica_da_porta_1,
            self.plc.tranca_magnetica_da_porta_2
        )

        # 2. Atualiza sensores físicos no CLP
        self.plc.fim_de_curso_da_cabine_1 = fc1
        self.plc.fim_de_curso_da_porta_1 = fp1
        self.plc.fim_de_curso_da_cabine_2 = fc2
        self.plc.fim_de_curso_da_porta_2 = fp2

        # 3. Executa Ciclo de Scan do S7-1200
        events = self.plc.scan_cycle()
        for evt in events:
            self._log(evt)

        # 4. Atualiza Sinótico Gráfico
        self.graphic_widget.update_states(
            self.physics.position_percent,
            self.physics.door_1_open_ratio,
            self.physics.door_2_open_ratio,
            self.plc.motor_1_sobe,
            self.plc.motor_1_desce,
            self.plc.tranca_magnetica_da_porta_1,
            self.plc.tranca_magnetica_da_porta_2,
            self.physics.pulley_angle_deg,
            self.plc.fim_de_curso_da_cabine_1,
            self.plc.fim_de_curso_da_cabine_2
        )

        # Atualiza texto de altura
        p_pct = self.physics.position_percent
        p_m = self.physics.pos_y_m
        if p_pct < 2.0:
            andar_txt = "1º Pavimento (Térreo)"
        elif p_pct > 98.0:
            andar_txt = "2º Pavimento (Superior)"
        else:
            andar_txt = f"Em trânsito ({p_pct:.1f}%)"
        self.lbl_pos_val.setText(f"{p_m:.2f} m - {andar_txt}")

        # 5. Atualiza Tabela de I/O
        values = [
            ("1" if self.plc.botao_sobe_1 else "0"),
            ("1" if self.plc.botao_desce_1 else "0"),
            ("1" if self.plc.fim_de_curso_da_cabine_1 else "0"),
            ("1" if self.plc.fim_de_curso_da_porta_1 else "0"),
            ("1" if self.plc.botao_sobe_2 else "0"),
            ("1" if self.plc.botao_desce_2 else "0"),
            ("1" if self.plc.fim_de_curso_da_cabine_2 else "0"),
            ("1" if self.plc.fim_de_curso_da_porta_2 else "0"),
            ("1" if self.plc.motor_1_sobe else "0"),
            ("1" if self.plc.motor_1_desce else "0"),
            ("1" if self.plc.tranca_magnetica_da_porta_1 else "0"),
            ("1" if self.plc.tranca_magnetica_da_porta_2 else "0"),
        ]

        for row, val in enumerate(values):
            item = self.io_table.item(row, 3)
            item.setText(val)
            if val == "1":
                item.setForeground(QColor(46, 204, 113))
                item.setFont(QFont("Consolas", 9, QFont.Bold))
            else:
                item.setForeground(QColor(130, 140, 155))
                item.setFont(QFont("Consolas", 9))

        # 6. Atualiza Painel de Diagnóstico Operacional (SCADA)
        if self.plc.motor_1_sobe:
            self.lbl_diag_motor.setText("Motor / Contatores: SUBINDO (K1 ATIVO %Q0.0)")
            self.lbl_diag_motor.setStyleSheet("color: #2ecc71; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")
        elif self.plc.motor_1_desce:
            self.lbl_diag_motor.setText("Motor / Contatores: DESCENDO (K2 ATIVO %Q0.1)")
            self.lbl_diag_motor.setStyleSheet("color: #e67e22; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")
        else:
            self.lbl_diag_motor.setText("Motor / Contatores: PARADO (K1=0, K2=0)")
            self.lbl_diag_motor.setStyleSheet("color: #a0c0e0; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")

        if not self.plc.stat_portas_fechadas:
            self.lbl_diag_seguranca.setText("Segurança NR-12: BLOQUEADO (Porta Aberta)")
            self.lbl_diag_seguranca.setStyleSheet("color: #e74c3c; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")
        else:
            self.lbl_diag_seguranca.setText("Segurança NR-12: PRONTO (Portas Fechadas)")
            self.lbl_diag_seguranca.setStyleSheet("color: #2ecc71; font-weight: bold; background: #232730; padding: 4px 8px; border-radius: 4px;")

        if self.plc.tranca_magnetica_da_porta_1:
            self.lbl_diag_tranca1.setText("Tranca 1: TRANCADA (%Q0.2=1)")
            self.lbl_diag_tranca1.setStyleSheet("color: #e74c3c; background: #232730; padding: 4px 8px; border-radius: 4px;")
        else:
            self.lbl_diag_tranca1.setText("Tranca 1: LIVRE / DESTRANCADA (%Q0.2=0)")
            self.lbl_diag_tranca1.setStyleSheet("color: #2ecc71; background: #232730; padding: 4px 8px; border-radius: 4px;")

        if self.plc.tranca_magnetica_da_porta_2:
            self.lbl_diag_tranca2.setText("Tranca 2: TRANCADA (%Q0.3=1)")
            self.lbl_diag_tranca2.setStyleSheet("color: #e74c3c; background: #232730; padding: 4px 8px; border-radius: 4px;")
        else:
            self.lbl_diag_tranca2.setText("Tranca 2: LIVRE / DESTRANCADA (%Q0.3=0)")
            self.lbl_diag_tranca2.setStyleSheet("color: #2ecc71; background: #232730; padding: 4px 8px; border-radius: 4px;")

    def _apply_dark_theme(self):
        qss = """
        QMainWindow {
            background-color: #1a1d24;
            color: #ecf0f1;
        }
        QGroupBox {
            font-size: 11px;
            font-weight: bold;
            color: #00e5ff;
            border: 1px solid #333d4d;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 4px;
        }
        QPushButton {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #4a5c70;
            border-radius: 4px;
            padding: 7px 12px;
            font-size: 10px;
        }
        QPushButton:hover {
            background-color: #34495e;
            border-color: #00e5ff;
        }
        QPushButton:pressed {
            background-color: #00bcd4;
            color: #111;
        }
        QTableWidget {
            background-color: #16191f;
            color: #ecf0f1;
            gridline-color: #2b3340;
            border: 1px solid #333d4d;
            border-radius: 4px;
            font-size: 10px;
        }
        QHeaderView::section {
            background-color: #222834;
            color: #9ab0c8;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #2b3340;
            font-size: 10px;
        }
        QTextEdit {
            background-color: #111317;
            color: #a8ffb2;
            border: 1px solid #333d4d;
            border-radius: 4px;
        }
        QProgressBar {
            background-color: #222834;
            border: 1px solid #3b4658;
            border-radius: 6px;
        }
        QProgressBar::chunk {
            background-color: #2ecc71;
            border-radius: 5px;
        }
        """
        self.setStyleSheet(qss)
