"""Testes Unitários da Lógica de Controle do Elevador Siemens S7-1200."""

import pytest
from src.simulador.plc_s7_1200 import PLCS71200Elevador

def test_initial_state():
    plc = PLCS71200Elevador()
    # Inicialmente: elevador no 1º piso (FC1 atuado -> %I0.2 = False pois é NF)
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    
    plc.scan_cycle()
    assert plc.stat_cabine_andar_1 is True
    assert plc.stat_cabine_andar_2 is False
    assert plc.motor_1_sobe is False
    assert plc.motor_1_desce is False
    # Porta 1 destrancada, Porta 2 trancada
    assert plc.tranca_magnetica_da_porta_1 is False
    assert plc.tranca_magnetica_da_porta_2 is True

def test_subir_partida_e_trancas():
    plc = PLCS71200Elevador()
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True

    # Pulso no botão sobe 1
    plc.botao_sobe_1 = True
    plc.scan_cycle()
    plc.botao_sobe_1 = False

    # Deve iniciar subida
    assert plc.motor_1_sobe is True
    assert plc.motor_1_desce is False
    # Em trânsito: ambas as trancas magnéticas devem estar ativas (portas trancadas)
    assert plc.tranca_magnetica_da_porta_1 is True
    assert plc.tranca_magnetica_da_porta_2 is True

def test_seguranca_portas_abertas():
    plc = PLCS71200Elevador()
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    # Porta 1 aberta (%I0.3 = False)
    plc.fim_de_curso_da_porta_1 = False
    plc.fim_de_curso_da_porta_2 = True

    # Tenta subir
    plc.botao_sobe_1 = True
    plc.scan_cycle()

    # Motor não pode ligar!
    assert plc.motor_1_sobe is False
    assert plc.motor_1_desce is False

def test_intertravamento_motor():
    plc = PLCS71200Elevador()
    plc.stat_subindo = True
    plc.stat_descendo = True
    plc.scan_cycle()
    # Pelo intertravamento cruzado, não podem estar ambos ligados
    assert not (plc.motor_1_sobe and plc.motor_1_desce)
