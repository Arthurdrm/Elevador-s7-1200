# Memorial Descritivo e Especificação Técnica
## Projeto: Controle de Elevador de Carga Industrial (Siemens S7-1200)
### Empresa: AutoControl | Unidade Fabril: Calçados | Unidade Curricular: Sistemas Lógicos Programáveis (SENAI)

---

## 1. Visão Geral da Planta

A empresa de calçados possui um parque fabril estruturado em uma edificação de **dois pavimentos**:
- **1º Pavimento (Térreo):** Área de expedição, recebimento e estocagem de couro e solados.
- **2º Pavimento (Superior):** Linha de montagem, pesponto e acabamento dos calçados.

Para melhorar a logística interna e o fluxo de matérias-primas pesadas, foi instalado um **elevador de carga** tracionado por cabo de aço e motorredutor elétrico trifásico acionado por contatoras reversoras controladas por um **CLP Siemens SIMATIC S7-1200**.

---

## 2. Descrição Mecânica e Eletroeletrônica

1. **Sistema de Tração:**
   - Motor elétrico acoplado a um redutor mecânico de rosca sem-fim.
   - Cabo de aço de alta resistência conectado ao cabeçote superior da cabine.
   - **Sentido Horário:** Deslocamento ascendente (Subir).
   - **Sentido Anti-horário:** Deslocamento descendente (Descer).

2. **Sensores de Posição da Cabine (Fim de Curso):**
   - Instalados estrategicamente no poço do elevador para detectar nivelamento exato nos pisos.
   - **Tipo Elétrico:** Chaves eletromecânicas com **contato normalmente fechado (NF / N.C.)**.
   - *Fundamento de Segurança NR-12:* Chaves NF garantem princípio de segurança intrínseca (*fail-safe*); caso um condutor se rompa, o sistema detecta ausência de sinal imediatamente.
   - **Comportamento elétrico:**
     - Cabine ausente do andar: Contato fechado $\rightarrow$ Nível lógico `%I = 1` (24 Vcc).
     - Cabine atuando no andar: Mecanismo mecânico abre o contato $\rightarrow$ Nível lógico `%I = 0` (0 Vcc).

3. **Monitoramento e Travamento de Portas:**
   - **Fins de curso de porta:** Chaves eletromecânicas com **contato normalmente aberto (NA / N.O.)**.
     - Porta aberta: Contato aberto $\rightarrow$ Nível lógico `%I = 0` (0 Vcc).
     - Porta fechada e travada no batente: Contato fecha $\rightarrow$ Nível lógico `%I = 1` (24 Vcc).
   - **Trancas Magnéticas (Eletroímãs de Segurança):**
     - Impede abertura indevida das portas dos pavimentos quando a cabine não estiver posicionada e parada no respectivo piso.
     - Sinal ativo `%Q = 1`: Eletroímã energizado (Porta Trancada).
     - Sinal inativo `%Q = 0`: Eletroímã desenergizado (Porta Destrancada para carga/descarga).

4. **Painéis de Comando Externos:**
   - Instalados ao lado das portas em ambos os pavimentos.
   - Contêm botões de impulso com contatos NA:
     - Pavimento 1: `Botao_sobe_1` (%I0.0) e `Botao_desce_1` (%I0.1).
     - Pavimento 2: `Botao_sobe_2` (%I0.4) e `Botao_desce_2` (%I0.5).

---

## 3. Mapeamento Completo de Entradas e Saídas (Tabela de I/O SENAI)

### Entradas Digitais (Digital Inputs - %I)

| Endereço | Tag TIA Portal | Tipo Elétrico | Descrição Funcional |
| :--- | :--- | :--- | :--- |
| `%I0.0` | `Botao_sobe_1` | Pulso N.O. (NA) | Botão no painel de comando do 1º pavimento para subir a cabine |
| `%I0.1` | `Botao_desce_1` | Pulso N.O. (NA) | Botão no painel de comando do 1º pavimento para descer/chamar a cabine |
| `%I0.2` | `Fim_de_curso_da_cabine_1` | Fim de curso N.C. (NF) | Monitora cabine nivelada no 1º pavimento (Abre ao acionar) |
| `%I0.3` | `Fim_de_curso_da_porta_1` | Fim de curso N.O. (NA) | Monitora fechamento da porta do 1º pavimento (Fecha com porta fechada) |
| `%I0.4` | `Botao_sobe_2` | Pulso N.O. (NA) | Botão no painel de comando do 2º pavimento para subir/chamar a cabine |
| `%I0.5` | `Botao_desce_2` | Pulso N.O. (NA) | Botão no painel de comando do 2º pavimento para descer a cabine |
| `%I0.6` | `Fim_de_curso_da_cabine_2` | Fim de curso N.C. (NF) | Monitora cabine nivelada no 2º pavimento (Abre ao acionar) |
| `%I0.7` | `Fim_de_curso_da_porta_2` | Fim de curso N.O. (NA) | Monitora fechamento da porta do 2º pavimento (Fecha com porta fechada) |

### Saídas Digitais (Digital Outputs - %Q)

| Endereço | Tag TIA Portal | Tipo de Carga | Descrição Funcional |
| :--- | :--- | :--- | :--- |
| `%Q0.0` | `Motor_1_sobe` | Bobina Contatora K1 | Aciona motor no sentido horário para subir a cabine |
| `%Q0.1` | `Motor_1_desce` | Bobina Contatora K2 | Aciona motor no sentido anti-horário para descer a cabine |
| `%Q0.2` | `Tranca_magnetica_da_porta_1`| Eletroímã 24Vcc | Tranca magnética da porta do 1º pavimento (1 = Trancada) |
| `%Q0.3` | `Tranca_magnetica_da_porta_2`| Eletroímã 24Vcc | Tranca magnética da porta do 2º pavimento (1 = Trancada) |

---

## 4. Requisitos de Operação e Segurança Industrial (NR-12)

1. **Condição Mandatória de Movimentação:**
   - O motor de tração (%Q0.0 ou %Q0.1) **SOMENTE** pode ser acionado se ambas as portas estiverem devidamente fechadas:
     $$\text{Condição de Portas Seguras} = (\%I0.3 = 1) \land (\%I0.7 = 1)$$
   - Caso qualquer porta se abra durante o deslocamento, o motor deve desligar instantaneamente.

2. **Intertravamento Cruzado dos Contatores do Motor:**
   - `%Q0.0` e `%Q0.1` jamais podem ser ativados simultaneamente sob hipótese alguma. Deve haver intertravamento lógico no programa e intertravamento elétrico por contatos auxiliares NF nos contatores de potência.

3. **Lógica de Bloqueio e Destravamento das Trancas Magnéticas:**
   - **Durante deslocamento da cabine:** As duas trancas devem permanecer trancadas (`%Q0.2 = 1` e `%Q0.3 = 1`).
   - **Cabine parada no 1º Andar:** Porta 1 destrancada (`%Q0.2 = 0`), Porta 2 trancada (`%Q0.3 = 1`).
   - **Cabine parada no 2º Andar:** Porta 2 destrancada (`%Q0.3 = 0`), Porta 1 trancada (`%Q0.2 = 1`).

4. **Matriz dos 4 Modos Operacionais:**
   - **Modo 1 (Comando no 1º Piso):** Elevador parado no piso 1. Ao apertar `Botao_desce_1`, nada acontece. Porta 1 permanece destrancada. Ao fechar portas e apertar `Botao_sobe_1`, o elevador sobe para o 2º andar.
   - **Modo 2 (Comando no 2º Piso):** Elevador parado no piso 2. Ao apertar `Botao_sobe_2`, nada acontece. Porta 2 permanece destrancada. Ao fechar portas e apertar `Botao_desce_2`, o elevador desce para o 1º andar.
   - **Modo 3 (Chamada Externa para o 2º Piso):** Elevador no piso 1. Chamada realizada no piso 2 via `Botao_sobe_2`. Elevador sobe e, ao atingir o piso 2, a porta 2 é destrancada.
   - **Modo 4 (Chamada Externa para o 1º Piso):** Elevador no piso 2. Chamada realizada no piso 1 via `Botao_desce_1`. Elevador desce e, ao atingir o piso 1, a porta 1 é destrancada.
