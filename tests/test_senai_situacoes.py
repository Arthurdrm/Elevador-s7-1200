"""Testes de Validação das 4 Situações do Desafio Industrial SENAI 3."""

import pytest
from src.simulador.plc_s7_1200 import PLCS71200Elevador

def test_situacao_1_elevador_primeiro_piso():
    plc = PLCS71200Elevador()
    # Elevador no 1º pavimento
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Porta fica destrancada
    assert plc.tranca_magnetica_da_porta_1 is False

    # Ao pressionar botão desce, o mesmo não se movimenta
    plc.botao_desce_1 = True
    plc.scan_cycle()
    plc.botao_desce_1 = False
    plc.scan_cycle()
    assert plc.motor_1_desce is False
    assert plc.motor_1_sobe is False

    # Ao pressionar botão sobe, ele sobe
    plc.botao_sobe_1 = True
    plc.scan_cycle()
    plc.botao_sobe_1 = False
    plc.scan_cycle()
    assert plc.motor_1_sobe is True
    assert plc.situacao_1_cumprida is True

def test_situacao_2_elevador_segundo_piso():
    plc = PLCS71200Elevador()
    # Elevador no 2º pavimento
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Porta do 2º piso fica destrancada
    assert plc.tranca_magnetica_da_porta_2 is False

    # Ao pressionar botão sobe, não se movimenta
    plc.botao_sobe_2 = True
    plc.scan_cycle()
    plc.botao_sobe_2 = False
    plc.scan_cycle()
    assert plc.motor_1_sobe is False
    assert plc.motor_1_desce is False

    # Ao pressionar botão desce, ele desce
    plc.botao_desce_2 = True
    plc.scan_cycle()
    plc.botao_desce_2 = False
    plc.scan_cycle()
    assert plc.motor_1_desce is True
    assert plc.situacao_2_cumprida is True

def test_situacao_3_chamada_no_segundo_piso():
    plc = PLCS71200Elevador()
    # Elevador no 1º piso
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Chamada realizada no 2º pavimento (Botao_sobe_2)
    plc.botao_sobe_2 = True
    plc.scan_cycle()
    plc.botao_sobe_2 = False
    plc.scan_cycle()

    # Elevador deve iniciar subida
    assert plc.motor_1_sobe is True
    assert plc.situacao_3_cumprida is True

    # Chegada ao 2º pavimento
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.scan_cycle()

    # Motor desliga e porta 2 é destrancada
    assert plc.motor_1_sobe is False
    assert plc.tranca_magnetica_da_porta_2 is False

def test_situacao_4_chamada_no_primeiro_piso():
    plc = PLCS71200Elevador()
    # Elevador no 2º piso
    plc.fim_de_curso_da_cabine_1 = True
    plc.fim_de_curso_da_cabine_2 = False
    plc.fim_de_curso_da_porta_1 = True
    plc.fim_de_curso_da_porta_2 = True
    plc.scan_cycle()

    # Chamada realizada no 1º pavimento (Botao_desce_1)
    plc.botao_desce_1 = True
    plc.scan_cycle()
    plc.botao_desce_1 = False
    plc.scan_cycle()

    # Elevador deve iniciar descida
    assert plc.motor_1_desce is True
    assert plc.situacao_4_cumprida is True

    # Chegada ao 1º pavimento
    plc.fim_de_curso_da_cabine_1 = False
    plc.fim_de_curso_da_cabine_2 = True
    plc.scan_cycle()

    # Motor desliga e porta 1 é destrancada
    assert plc.motor_1_desce is False
    assert plc.tranca_magnetica_da_porta_1 is False

def test_rubrica_pontuacao_maxima_10():
    plc = PLCS71200Elevador()
    assert plc.calcular_nota_senai() == 0.0

    plc.situacao_1_cumprida = True
    assert plc.calcular_nota_senai() == 2.5

    plc.situacao_2_cumprida = True
    assert plc.calcular_nota_senai() == 5.0

    plc.situacao_3_cumprida = True
    assert plc.calcular_nota_senai() == 7.5

    plc.situacao_4_cumprida = True
    assert plc.calcular_nota_senai() == 10.0
