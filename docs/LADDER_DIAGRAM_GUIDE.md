# Guia Passo a Passo de Implementação em Linguagem Ladder (LAD) - S7-1200
## Instrumento de Avaliação Prática SENAI - Desafio Industrial 3

Este guia foi elaborado para que os estudantes e instrutores do SENAI possam desenhar e implementar o programa diretamente no editor **LAD (Ladder)** do Siemens TIA Portal (v15, v16, v17, v18 ou v19).

---

## 1. Tabela de Variáveis e Mapeamento de Símbolos

Antes de inserir as redes, assegure-se de que a **Tabela Padrão de Variáveis (Default PLC Tag Table)** contenha as seguintes tags:

| Nome da Tag | Endereço | Tipo | Contato Elétrico Físico |
| :--- | :--- | :--- | :--- |
| `Botao_sobe_1` | `%I0.0` | BOOL | NA (Normalmente Aberto) |
| `Botao_desce_1` | `%I0.1` | BOOL | NA (Normalmente Aberto) |
| `Fim_de_curso_da_cabine_1` | `%I0.2` | BOOL | NF (Normalmente Fechado) |
| `Fim_de_curso_da_porta_1` | `%I0.3` | BOOL | NA (Normalmente Aberto) |
| `Botao_sobe_2` | `%I0.4` | BOOL | NA (Normalmente Aberto) |
| `Botao_desce_2` | `%I0.5` | BOOL | NA (Normalmente Aberto) |
| `Fim_de_curso_da_cabine_2` | `%I0.6` | BOOL | NF (Normalmente Fechado) |
| `Fim_de_curso_da_porta_2` | `%I0.7` | BOOL | NA (Normalmente Aberto) |
| `Motor_1_sobe` | `%Q0.0` | BOOL | Bobina de saída do contator K1 |
| `Motor_1_desce` | `%Q0.1` | BOOL | Bobina de saída do contator K2 |
| `Tranca_magnetica_da_porta_1` | `%Q0.2` | BOOL | Bobina do eletroímã do 1º andar |
| `Tranca_magnetica_da_porta_2` | `%Q0.3` | BOOL | Bobina do eletroímã do 2º andar |

### Tags de Memória Auxiliares (Bit Memory)
| Nome da Tag | Endereço | Tipo | Função |
| :--- | :--- | :--- | :--- |
| `Cabine_Andar_1` | `%M0.0` | BOOL | Sinaliza cabine presente no 1º pavimento |
| `Cabine_Andar_2` | `%M0.1` | BOOL | Sinaliza cabine presente no 2º pavimento |
| `Portas_Fechadas` | `%M0.2` | BOOL | Condição segura de ambas as portas fechadas |

---

## 2. Redes Ladder (Networks) para o Bloco `Main [OB1]`

### Rede 1: Decodificação dos Sensores de Posição da Cabine (Fins de Curso NF)
> **Fundamento Pedagógico SENAI:** O fim de curso no hardware é **NF**. Quando a cabine chega ao andar e aperta a chave, o contato mecânico abre, gerando `0V` na entrada do CLP (`%I = 0`). Portanto, no Ladder, usamos um contato normalmente fechado `|/|` para energizar a bobina quando o sinal elétrico for zero!

```text
// Network 1: Detecção da Cabine no 1º Pavimento
   "Fim_de_curso_da_cabine_1"           "Cabine_Andar_1"
              %I0.2                          %M0.0
---------------|/|----------------------------( )------

// Network 2: Detecção da Cabine no 2º Pavimento
   "Fim_de_curso_da_cabine_2"           "Cabine_Andar_2"
              %I0.6                          %M0.1
---------------|/|----------------------------( )------
```

---

### Rede 2: Condição Geral de Segurança das Portas (Intertravamento Mandatório)
> Ambas as portas devem estar totalmente fechadas para habilitar qualquer acionamento dos motores.

```text
// Network 3: Monitoramento de Segurança das Portas
 "Fim_de_curso_da_porta_1"   "Fim_de_curso_da_porta_2"    "Portas_Fechadas"
           %I0.3                       %I0.7                    %M0.2
------------| |-------------------------| |----------------------( )------
```

---

### Rede 3: Comando de Subida da Cabine com Circuito de Retenção (Selo)
> Permite a subida se:
> 1. Pressionado `Botao_sobe_1` (%I0.0) OU `Botao_sobe_2` (%I0.4).
> 2. Cabine estiver no 1º pavimento (`Cabine_Andar_1` = %M0.0).
> 3. Ambas as portas estiverem fechadas (`Portas_Fechadas` = %M0.2).
> 4. Motor de descida estiver desligado (`Motor_1_desce` = %Q0.1).
> 5. A subida é desarmada assim que a cabine atingir o 2º pavimento (`Cabine_Andar_2` = %M0.1) ou se alguma porta for aberta.

```text
// Network 4: Lógica de Subida do Motor (Sentido Horário)
   "Cabine_Andar_1"   "Portas_Fechadas"   "Motor_1_desce"   "Cabine_Andar_2"   "Motor_1_sobe"
        %M0.0              %M0.2               %Q0.1             %M0.1             %Q0.0
----+----| |----------------| |-----------------|/|---------------|/|--------------( )---
    |
    |  "Botao_sobe_1"
    |       %I0.0
    +----| |----+
    |           |
    |  "Botao_sobe_2"
    |       %I0.4
    +----| |----+
    |           |
    |  "Motor_1_sobe" (Selo)
    |       %Q0.0
    +----| |----+
```

---

### Rede 4: Comando de Descida da Cabine com Circuito de Retenção (Selo)
> Permite a descida se:
> 1. Pressionado `Botao_desce_1` (%I0.1) OU `Botao_desce_2` (%I0.5).
> 2. Cabine estiver no 2º pavimento (`Cabine_Andar_2` = %M0.1).
> 3. Ambas as portas estiverem fechadas (`Portas_Fechadas` = %M0.2).
> 4. Motor de subida estiver desligado (`Motor_1_sobe` = %Q0.0).
> 5. A descida é desarmada assim que a cabine atingir o 1º pavimento (`Cabine_Andar_1` = %M0.0) ou se alguma porta for aberta.

```text
// Network 5: Lógica de Descida do Motor (Sentido Anti-horário)
   "Cabine_Andar_2"   "Portas_Fechadas"   "Motor_1_sobe"    "Cabine_Andar_1"   "Motor_1_desce"
        %M0.1              %M0.2               %Q0.0             %M0.0             %Q0.1
----+----| |----------------| |-----------------|/|---------------|/|--------------( )---
    |
    |  "Botao_desce_1"
    |       %I0.1
    +----| |----+
    |           |
    |  "Botao_desce_2"
    |       %I0.5
    +----| |----+
    |           |
    |  "Motor_1_desce" (Selo)
    |       %Q0.1
    +----| |----+
```

---

### Rede 5: Tranca Magnética da Porta do 1º Pavimento (%Q0.2)
> Requisito do Escopo:
> - Enquanto o motor estiver deslocando a cabine, as duas portas devem permanecer trancadas.
> - O destravamento só ocorre se a cabine estiver parada no andar.
> - Logo, a Tranca 1 (%Q0.2) fica **energizada (trancada)** se:
>   - O motor estiver subindo (`Motor_1_sobe` = %Q0.0), OU
>   - O motor estiver descendo (`Motor_1_desce` = %Q0.1), OU
>   - A cabine NÃO estiver no 1º pavimento (está no 2º andar ou em trânsito).

```text
// Network 6: Controle da Tranca Magnética 1
                                                     "Tranca_magnetica_da_porta_1"
   "Motor_1_sobe"                                                %Q0.2
----+----| |----+-------------------------------------------------( )-----
    |           |
    |  "Motor_1_desce"
    +----| |----+
    |           |
    |  "Cabine_Andar_1"
    +----|/|----+
```

---

### Rede 6: Tranca Magnética da Porta do 2º Pavimento (%Q0.3)
> A Tranca 2 (%Q0.3) fica **energizada (trancada)** se:
> - O motor estiver subindo (`Motor_1_sobe` = %Q0.0), OU
> - O motor estiver descendo (`Motor_1_desce` = %Q0.1), OU
> - A cabine NÃO estiver no 2º pavimento (está no 1º andar ou em trânsito).

```text
// Network 7: Controle da Tranca Magnética 2
                                                     "Tranca_magnetica_da_porta_2"
   "Motor_1_sobe"                                                %Q0.3
----+----| |----+-------------------------------------------------( )-----
    |           |
    |  "Motor_1_desce"
    +----| |----+
    |           |
    |  "Cabine_Andar_2"
    +----|/|----+
```

---

## 3. Checklist de Validação em Bancada Didática

Ao montar esse diagrama no TIA Portal e transferir para a bancada física:
1. Verifique se com a cabine no chão, a entrada `%I0.2` está em nível lógico `0` e o bit `%M0.0` está em `1`.
2. Verifique se com as portas fechadas as entradas `%I0.3` e `%I0.7` estão em `1`.
3. Pressione `Botao_desce_1` (%I0.1) $\rightarrow$ Motor **não liga** (Situação 1 atendida).
4. Pressione `Botao_sobe_1` (%I0.0) $\rightarrow$ Motor sobe, Tranca 1 aciona e desliga ao atingir o 2º andar (Situação 1 e 3 atendidas).
5. No 2º andar, pressione `Botao_sobe_2` (%I0.4) $\rightarrow$ Motor **não liga** (Situação 2 atendida).
6. No 1º andar, pressione `Botao_desce_1` (%I0.1) $\rightarrow$ Motor desce e destranca porta 1 ao nivelar (Situação 4 atendida).
