"""Testes de Operação e Segurança Funcional do Elevador Siemens S7-1200."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.simulador.plc_s7_1200 import PLCS71200Elevador

def test_operacao_primeiro_piso_bloqueio_e_subida():
    plc = PLCS71200Elevador()
    # Elevador posicionado no 1º pavimento (chave NF abre -> False)
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Porta do andar atual deve permanecer destrancada
    assert plc.tranca_magnetica_da_porta_1 is False

    # Ao pressionar botão desce, o motor não se movimenta
    plc.botao_desce_1 = True
    plc.scan_cycle()
    plc.botao_desce_1 = False
    plc.scan_cycle()
    assert plc.motor_1_desce is False
    assert plc.motor_1_sobe is False

    # Ao pressionar botão sobe, o motor de subida é acionado
    plc.botao_sobe_1 = True
    plc.scan_cycle()
    plc.botao_sobe_1 = False
    plc.scan_cycle()
    assert plc.motor_1_sobe is True
    # Ambas as portas devem estar trancadas em trânsito
    assert plc.tranca_magnetica_da_porta_1 is True
    assert plc.tranca_magnetica_da_porta_2 is True

def test_operacao_segundo_piso_bloqueio_e_descida():
    plc = PLCS71200Elevador()
    # Elevador posicionado no 2º pavimento (chave NF abre -> False)
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Porta do 2º piso fica destrancada
    assert plc.tranca_magnetica_da_porta_2 is False

    # Ao pressionar botão sobe, motor não se movimenta
    plc.botao_sobe_2 = True
    plc.scan_cycle()
    plc.botao_sobe_2 = False
    plc.scan_cycle()
    assert plc.motor_1_sobe is False
    assert plc.motor_1_desce is False

    # Ao pressionar botão desce, motor de descida é acionado
    plc.botao_desce_2 = True
    plc.scan_cycle()
    plc.botao_desce_2 = False
    plc.scan_cycle()
    assert plc.motor_1_desce is True
    assert plc.tranca_magnetica_da_porta_1 is True
    assert plc.tranca_magnetica_da_porta_2 is True

def test_chamada_externa_para_segundo_piso():
    plc = PLCS71200Elevador()
    # Elevador no 1º piso
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Chamada realizada no painel do 2º pavimento (Botao_sobe_2)
    plc.botao_sobe_2 = True
    plc.scan_cycle()
    plc.botao_sobe_2 = False
    plc.scan_cycle()

    # Elevador deve iniciar subida
    assert plc.motor_1_sobe is True

    # Chegada e nivelamento no 2º pavimento
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.scan_cycle()

    # Motor desliga e porta do 2º andar é destrancada
    assert plc.motor_1_sobe is False
    assert plc.tranca_magnetica_da_porta_2 is False
    assert plc.tranca_magnetica_da_porta_1 is True

def test_chamada_externa_para_primeiro_piso():
    plc = PLCS71200Elevador()
    # Elevador no 2º piso
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Chamada realizada no painel do 1º pavimento (Botao_desce_1)
    plc.botao_desce_1 = True
    plc.scan_cycle()
    plc.botao_desce_1 = False
    plc.scan_cycle()

    # Elevador deve iniciar descida
    assert plc.motor_1_desce is True

    # Chegada e nivelamento no 1º pavimento
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.scan_cycle()

    # Motor desliga e porta do 1º andar é destrancada
    assert plc.motor_1_desce is False
    assert plc.tranca_magnetica_da_porta_1 is False
    assert plc.tranca_magnetica_da_porta_2 is True

def test_seguranca_parada_imediata_abertura_porta():
    plc = PLCS71200Elevador()
    # Elevador partindo do 1º piso
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Inicia subida
    plc.botao_sobe_1 = True
    plc.scan_cycle()
    plc.botao_sobe_1 = False
    plc.scan_cycle()
    assert plc.motor_1_sobe is True

    # Em meio ao percurso, uma porta é aberta (%I0.3 = False)
    plc.fim_de_curso_da_cabine_1 = True # Já saiu do 1º andar
    plc.fim_de_curso_da_porta_1 = False
    plc.scan_cycle()

    # Motor deve PARAR IMEDIATAMENTE (NR-12)
    assert plc.motor_1_sobe is False
    assert plc.motor_1_desce is False
