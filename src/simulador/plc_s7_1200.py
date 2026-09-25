"""Emulador do Ciclo de Varredura (Scan Cycle) do CLP Siemens S7-1200.
Implementa a lógica fiel do bloco FB_Controle_Elevador.scl para o Desafio Industrial SENAI.
"""

from typing import List

class PLCS71200Elevador:
    def __init__(self):
        # 1. ENTRADAS DIGITAIS (%I0.0 a %I0.7)
        self.botao_sobe_1: bool = False             # %I0.0 (NA) - Botão sobe painel 1º pavimento
        self.botao_desce_1: bool = False            # %I0.1 (NA) - Botão desce painel 1º pavimento
        self.fim_de_curso_da_cabine_1: bool = False # %I0.2 (NF) - Posição cabine 1º pavimento (Abre contato quando cabine presente = False)
        self.fim_de_curso_da_porta_1: bool = True   # %I0.3 (NA) - Posição porta 1 (Fecha contato quando porta fecha = True)
        
        self.botao_sobe_2: bool = False             # %I0.4 (NA) - Botão sobe painel 2º pavimento
        self.botao_desce_2: bool = False            # %I0.5 (NA) - Botão desce painel 2º pavimento
        self.fim_de_curso_da_cabine_2: bool = True  # %I0.6 (NF) - Posição cabine 2º pavimento (Fechado em repouso = True)
        self.fim_de_curso_da_porta_2: bool = True   # %I0.7 (NA) - Posição porta 2 (Fecha contato quando porta fecha = True)

        # 2. SAÍDAS DIGITAIS (%Q0.0 a %Q0.3)
        self.motor_1_sobe: bool = False             # %Q0.0 - Motor sentido horário (Subir)
        self.motor_1_desce: bool = False            # %Q0.1 - Motor sentido anti-horário (Descer)
        self.tranca_magnetica_da_porta_1: bool = False # %Q0.2 - Tranca magnética porta 1 (1=Trancada)
        self.tranca_magnetica_da_porta_2: bool = True  # %Q0.3 - Tranca magnética porta 2 (1=Trancada)

        # 3. VARIÁVEIS INTERNAS DE ESTADO (STAT / DB)
        self.stat_cabine_andar_1: bool = True
        self.stat_cabine_andar_2: bool = False
        self.stat_portas_fechadas: bool = True
        self.stat_subindo: bool = False
        self.stat_descendo: bool = False

        # Memórias anteriores para detecção de pulso (One-shot / R_TRIG)
        self._prev_sobe_1: bool = False
        self._prev_desce_1: bool = False
        self._prev_sobe_2: bool = False
        self._prev_desce_2: bool = False
        self._prev_cabine_1: bool = False
        self._prev_cabine_2: bool = False

        # Estatísticas e Métricas de Avaliação
        self.situacao_1_cumprida: bool = False
        self.situacao_2_cumprida: bool = False
        self.situacao_3_cumprida: bool = False
        self.situacao_4_cumprida: bool = False
        self.seguranca_portas_testada: bool = False

    def scan_cycle(self) -> List[str]:
        """Executa 1 ciclo de scan do CLP Siemens idêntico ao OB1 / FB_Controle_Elevador."""
        events: List[str] = []

        # 1. NORMALIZAÇÃO FÍSICA DOS SENSORES
        # Contato NF (Normalmente Fechado): quando a cabine chega, o atuador abre o contato (0V = False)
        self.stat_cabine_andar_1 = not self.fim_de_curso_da_cabine_1
        self.stat_cabine_andar_2 = not self.fim_de_curso_da_cabine_2

        # Contato NA (Normalmente Aberto): quando a porta fecha, fecha o contato (24V = True)
        self.stat_portas_fechadas = self.fim_de_curso_da_porta_1 and self.fim_de_curso_da_porta_2

        # 2. DETECÇÃO DE BORDAS DOS BOTÕES
        pulso_sobe_1 = self.botao_sobe_1 and not self._prev_sobe_1
        pulso_desce_1 = self.botao_desce_1 and not self._prev_desce_1
        pulso_sobe_2 = self.botao_sobe_2 and not self._prev_sobe_2
        pulso_desce_2 = self.botao_desce_2 and not self._prev_desce_2

        self._prev_sobe_1 = self.botao_sobe_1
        self._prev_desce_1 = self.botao_desce_1
        self._prev_sobe_2 = self.botao_sobe_2
        self._prev_desce_2 = self.botao_desce_2

        # 3. VERIFICAÇÃO DAS 4 SITUAÇÕES DO INSTRUMENTO DE AVALIAÇÃO SENAI

        # --- SITUAÇÃO 1: Elevador no 1º pavimento e comando no 1º pavimento ---
        if self.stat_cabine_andar_1:
            if pulso_desce_1:
                events.append("⚠️ [SITUAÇÃO 1 VALIDADA] Botão Desce 1 pressionado com elevador já no 1º piso: motor não aciona!")
                self.situacao_1_cumprida = True
            
            if pulso_sobe_1:
                if not self.stat_portas_fechadas:
                    events.append("⛔ [SEGURANÇA BLOQUEADA] Comando de subida rejeitado: portas abertas!")
                    self.seguranca_portas_testada = True
                elif not self.stat_descendo:
                    self.stat_subindo = True
                    events.append("🟢 [SITUAÇÃO 1 VALIDADA] Botão Sobe 1 pressionado no 1º piso: elevador iniciando subida para o 2º piso!")
                    self.situacao_1_cumprida = True

        # --- SITUAÇÃO 2: Elevador no 2º pavimento e comando no 2º pavimento ---
        if self.stat_cabine_andar_2:
            if pulso_sobe_2:
                events.append("⚠️ [SITUAÇÃO 2 VALIDADA] Botão Sobe 2 pressionado com elevador já no 2º piso: motor não aciona!")
                self.situacao_2_cumprida = True
            
            if pulso_desce_2:
                if not self.stat_portas_fechadas:
                    events.append("⛔ [SEGURANÇA BLOQUEADA] Comando de descida rejeitado: portas abertas!")
                    self.seguranca_portas_testada = True
                elif not self.stat_subindo:
                    self.stat_descendo = True
                    events.append("🟢 [SITUAÇÃO 2 VALIDADA] Botão Desce 2 pressionado no 2º piso: elevador iniciando descida para o 1º piso!")
                    self.situacao_2_cumprida = True

        # --- SITUAÇÃO 3: Elevador no 1º pavimento e chamada feita no 2º pavimento ---
        if self.stat_cabine_andar_1 and pulso_sobe_2:
            if not self.stat_portas_fechadas:
                events.append("⛔ [SEGURANÇA BLOQUEADA] Chamada do 2º piso rejeitada: portas abertas!")
                self.seguranca_portas_testada = True
            elif not self.stat_descendo:
                self.stat_subindo = True
                events.append("🚀 [SITUAÇÃO 3 VALIDADA] Chamada do 2º pavimento (Botão Sobe 2): elevador subindo!")
                self.situacao_3_cumprida = True

        # --- SITUAÇÃO 4: Elevador no 2º pavimento e chamada feita no 1º pavimento ---
        if self.stat_cabine_andar_2 and pulso_desce_1:
            if not self.stat_portas_fechadas:
                events.append("⛔ [SEGURANÇA BLOQUEADA] Chamada do 1º piso rejeitada: portas abertas!")
                self.seguranca_portas_testada = True
            elif not self.stat_subindo:
                self.stat_descendo = True
                events.append("🚀 [SITUAÇÃO 4 VALIDADA] Chamada do 1º pavimento (Botão Desce 1): elevador descendo!")
                self.situacao_4_cumprida = True

        # 4. RETENÇÃO (SELO) E CONDIÇÕES DE PARADA DO MOTOR
        if self.stat_subindo:
            # Para se portas abrirem ou atingir o 2º andar
            if not self.stat_portas_fechadas:
                self.stat_subindo = False
                events.append("🛑 [INTERRUPÇÃO DE SEGURANÇA] Subida interrompida: porta aberta durante o trajeto!")
                self.seguranca_portas_testada = True
            elif self.stat_cabine_andar_2:
                self.stat_subindo = False
                events.append("🎯 [CHEGADA] Elevador atingiu o 2º pavimento! Motor desligado.")
                if self.situacao_1_cumprida or self.situacao_3_cumprida:
                    events.append("🔓 [TRANCA] Destrancando porta do 2º pavimento (%Q0.3=0). Porta 1 permanece trancada.")

        if self.stat_descendo:
            # Para se portas abrirem ou atingir o 1º andar
            if not self.stat_portas_fechadas:
                self.stat_descendo = False
                events.append("🛑 [INTERRUPÇÃO DE SEGURANÇA] Descida interrompida: porta aberta durante o trajeto!")
                self.seguranca_portas_testada = True
            elif self.stat_cabine_andar_1:
                self.stat_descendo = False
                events.append("🎯 [CHEGADA] Elevador atingiu o 1º pavimento! Motor desligado.")
                if self.situacao_2_cumprida or self.situacao_4_cumprida:
                    events.append("🔓 [TRANCA] Destrancando porta do 1º pavimento (%Q0.2=0). Porta 2 permanece trancada.")

        # Atribuição às saídas físicas do motor com intertravamento
        self.motor_1_sobe = self.stat_subindo and not self.stat_descendo
        self.motor_1_desce = self.stat_descendo and not self.stat_subindo

        # 5. CONTROLE DAS TRANCAS MAGNÉTICAS (%Q0.2 e %Q0.3)
        # Regras SENAI:
        # - Em movimento: as duas trancadas (%Q0.2=1, %Q0.3=1)
        # - Parado no 1º andar: porta 1 destrancada (%Q0.2=0), porta 2 trancada (%Q0.3=1)
        # - Parado no 2º andar: porta 2 destrancada (%Q0.3=0), porta 1 trancada (%Q0.2=1)
        if self.motor_1_sobe or self.motor_1_desce:
            self.tranca_magnetica_da_porta_1 = True
            self.tranca_magnetica_da_porta_2 = True
        else:
            self.tranca_magnetica_da_porta_1 = not self.stat_cabine_andar_1
            self.tranca_magnetica_da_porta_2 = not self.stat_cabine_andar_2

        # Detecção de transição de chegada para logs
        if self.stat_cabine_andar_1 and not self._prev_cabine_1:
            events.append("📍 [SENSOR FIM DE CURSO] Cabine acionou Fim_de_curso_da_cabine_1 (%I0.2 abriu)")
        if self.stat_cabine_andar_2 and not self._prev_cabine_2:
            events.append("📍 [SENSOR FIM DE CURSO] Cabine acionou Fim_de_curso_da_cabine_2 (%I0.6 abriu)")

        self._prev_cabine_1 = self.stat_cabine_andar_1
        self._prev_cabine_2 = self.stat_cabine_andar_2

        return events

    def calcular_nota_senai(self) -> float:
        """Calcula a nota de 0 a 10 baseada na rubrica oficial do instrumento SENAI (Páginas 6 e 7)."""
        nota = 0.0
        # Critério 1: Controle no 1º pavimento (2.5 pontos)
        if self.situacao_1_cumprida:
            nota += 2.5
        # Critério 2: Controle no 2º pavimento (2.5 pontos)
        if self.situacao_2_cumprida:
            nota += 2.5
        # Critério 3: Deslocamento inferior -> superior e destravamento (2.5 pontos)
        if self.situacao_3_cumprida:
            nota += 2.5
        # Critério 4: Deslocamento superior -> inferior e destravamento (2.5 pontos)
        if self.situacao_4_cumprida:
            nota += 2.5
        return min(10.0, nota)
