#!/usr/bin/env python3
"""Script de Demonstração e Validação dos Testes do S7-1200 - Elevador Industrial.

Gera um relatório visual completo no terminal e captura preview do simulador gráfico.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.simulador.plc_s7_1200 import PLCS71200Elevador
from src.simulador.elevator_physics import ElevatorPhysics

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header():
    print(f"\n{CYAN}{BOLD}{'=' * 78}")
    print("  PROJETO_ELEVADOR_S7-1200 — RELATÓRIO DE TESTES TÉCNICOS & OPERAÇÃO")
    print("  Controle de Elevador Industrial (AutoControl) | Siemens S7-1200")
    print(f"{'=' * 78}{RESET}\n")

def print_step(num: int, title: str, desc: str, passed: bool, details: list[str] = None):
    status = f"{GREEN}[APROVADO]{RESET}" if passed else f"{RED}[FALHOU]{RESET}"
    print(f"{BOLD}{CYAN}Teste {num:02d}:{RESET} {BOLD}{title:<52}{RESET} {status}")
    print(f"  {YELLOW}↳ Detalhe:{RESET} {desc}")
    if details:
        for d in details:
            print(f"     {d}")
    print()

def main():
    print_header()
    time.sleep(0.1)
    passed_count = 0
    total_tests = 5

    # Teste 1: Estado Inicial e Sensores NF
    plc = PLCS71200Elevador()
    plc.fim_de_curso_da_cabine_1 = False # NF acionado = 0V
    plc.fim_de_curso_da_cabine_2 = True  # NF livre = 24V
    plc.fim_de_curso_da_porta_1 = True   # NA fechado = 24V
    plc.fim_de_curso_da_porta_2 = True   # NA fechado = 24V
    plc.scan_cycle()

    ok1 = (plc.stat_cabine_andar_1 and not plc.stat_cabine_andar_2 and 
           not plc.tranca_magnetica_da_porta_1 and plc.tranca_magnetica_da_porta_2)
    if ok1: passed_count += 1
    print_step(
        1, "Normalização dos Sensores NF e Estado Inicial",
        "Valida que sensor NF cabine 1 em 0V indica cabine presente e destranca Porta 1 (%Q0.2=0).",
        ok1, [f"Cabine 1: {plc.stat_cabine_andar_1} | Tranca 1: {plc.tranca_magnetica_da_porta_1} | Tranca 2: {plc.tranca_magnetica_da_porta_2}"]
    )

    # Teste 2: Operação no 1º Piso
    plc.botao_desce_1 = True
    plc.scan_cycle()
    plc.botao_desce_1 = False
    plc.scan_cycle()
    desce_bloqueado = (not plc.motor_1_desce and not plc.motor_1_sobe)
    
    plc.botao_sobe_1 = True
    plc.scan_cycle()
    plc.botao_sobe_1 = False
    sobe_iniciado = plc.motor_1_sobe and plc.tranca_magnetica_da_porta_1 and plc.tranca_magnetica_da_porta_2
    
    ok2 = desce_bloqueado and sobe_iniciado
    if ok2: passed_count += 1
    print_step(
        2, "Operação no 1º Piso (Bloqueio & Partida)",
        "Bloqueia descida indevida, inicia subida para 2º piso e tranca ambas as portas.",
        ok2, [f"Desce Bloqueado: {desce_bloqueado} | Sobe Ativo: {sobe_iniciado} | Trancas: Q0.2={plc.tranca_magnetica_da_porta_1}, Q0.3={plc.tranca_magnetica_da_porta_2}"]
    )

    # Teste 3: Operação no 2º Piso
    plc = PLCS71200Elevador()
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False # Cabine no 2º andar
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    plc.botao_sobe_2 = True
    plc.scan_cycle()
    plc.botao_sobe_2 = False
    plc.scan_cycle()
    sobe_bloqueado = (not plc.motor_1_sobe and not plc.motor_1_desce)

    plc.botao_desce_2 = True
    plc.scan_cycle()
    plc.botao_desce_2 = False
    desce_iniciado = plc.motor_1_desce and plc.tranca_magnetica_da_porta_1 and plc.tranca_magnetica_da_porta_2

    ok3 = sobe_bloqueado and desce_iniciado
    if ok3: passed_count += 1
    print_step(
        3, "Operação no 2º Piso (Bloqueio & Partida)",
        "Bloqueia subida indevida, inicia descida para 1º piso e tranca ambas as portas.",
        ok3, [f"Sobe Bloqueado: {sobe_bloqueado} | Desce Ativo: {desce_iniciado}"]
    )

    # Teste 4: Chamadas Externas e Destrancamento Exclusivo
    plc = PLCS71200Elevador()
    plc.fim_de_curso_da_cabine_1 = False # No 1º piso
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Chamada do 2º piso
    plc.botao_sobe_2 = True
    plc.scan_cycle()
    plc.botao_sobe_2 = False
    chamada_sobe_ok = plc.motor_1_sobe

    # Chegada ao 2º piso
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.scan_cycle()
    chegada_2_ok = (not plc.motor_1_sobe and not plc.tranca_magnetica_da_porta_2 and plc.tranca_magnetica_da_porta_1)

    ok4 = chamada_sobe_ok and chegada_2_ok
    if ok4: passed_count += 1
    print_step(
        4, "Chamada Externa & Destrancamento Exclusivo",
        "Chamada remota desloca cabine e destranca exclusivamente a porta do piso de chegada.",
        ok4, [f"Chamada Subida: {chamada_sobe_ok} | Parada e Destrancamento Piso 2: {chegada_2_ok}"]
    )

    # Teste 5: Segurança e Interrupção Imediata (NR-12)
    plc = PLCS71200Elevador()
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    plc.botao_sobe_1 = True
    plc.scan_cycle()
    plc.botao_sobe_1 = False
    plc.scan_cycle()
    em_movimento = plc.motor_1_sobe

    # Simula abertura da porta durante o deslocamento
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_porta_1 = False
    plc.scan_cycle()
    parou_emergencia = (not plc.motor_1_sobe and not plc.motor_1_desce)

    ok5 = em_movimento and parou_emergencia
    if ok5: passed_count += 1
    print_step(
        5, "Intertravamento de Segurança NR-12 (Porta Aberta)",
        "Garante parada instantânea do motor caso qualquer porta seja aberta durante o movimento.",
        ok5, [f"Em movimento: {em_movimento} | Parada Imediata: {parou_emergencia}"]
    )

    print(f"{CYAN}{BOLD}{'=' * 78}{RESET}")
    if passed_count == total_tests:
        print(f"  {GREEN}{BOLD}RESULTADO: TODOS OS {total_tests} TESTES FORAM APROVADOS COM SUCESSO! (100%){RESET}")
    else:
        print(f"  {RED}{BOLD}RESULTADO: {passed_count}/{total_tests} TESTES APROVADOS.{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 78}{RESET}\n")

    # Tenta salvar preview gráfico via offscreen
    try:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        from PySide6.QtWidgets import QApplication
        from src.simulador.ui_window import MainWindowSimuladorElevador
        app = QApplication.instance() or QApplication(sys.argv)
        win = MainWindowSimuladorElevador()
        win.resize(1180, 800)
        win.show()
        # Avança a simulação até a cabine subir um pouco para ficar bem bonita
        win.physics.pos_y_m = 2.1
        win.plc.motor_1_sobe = True
        win.plc.tranca_magnetica_da_porta_1 = True
        win.plc.tranca_magnetica_da_porta_2 = True
        win._simulation_step()
        
        pix = win.grab()
        preview_path = os.path.join(os.path.dirname(__file__), "dist", "preview_elevador.png")
        pix.save(preview_path)
        print(f"📸 {GREEN}Preview visual salvo com sucesso em:{RESET} {preview_path}\n")
    except Exception as e:
        print(f"Aviso de captura gráfica: {e}")

if __name__ == "__main__":
    main()
