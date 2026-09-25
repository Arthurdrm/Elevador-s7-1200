# Rubrica Oficial de Avaliação Prática - SENAI
## Unidade Curricular: Sistemas Lógicos Programáveis
### Desafio Industrial 3: Controle de Elevador de Carga AutoControl

---

## 1. Etapas do Desafio e Distribuição de Pontos

O instrumento avaliativo possui **10,0 pontos no total**, distribuídos em 4 etapas técnicas principais (2,5 pontos cada), com critérios de desconto por dependência de auxílio docente (Critério 5).

| Etapa | Critério Técnico Avaliado | Conceito A (2,5 pts) | Conceito B (1,8 pts) | Conceito C (1,0 pt) | Conceito D (0,0 pts) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1ª** | **Controle do elevador no pavimento inferior no qual está sendo realizada a movimentação** | Monitorou o estado atual do elevador e manteve destravada a porta do pavimento. Considerou a possibilidade do elevador subir, monitorando as duas portas, a localização da cabine no pavimento inferior e o deslocamento para o piso superior. | Não monitorou o estado atual e não manteve destravada a porta, mas considerou a subida com portas e localização monitoradas. | Monitorou estado atual e manteve destravada a porta, mas não considerou a possibilidade de subir. | Não monitorou estado, não manteve destravada a porta e não considerou a possibilidade de subir. |
| **2ª** | **Controle do elevador no pavimento superior no qual está sendo realizada a movimentação** | Monitorou o estado atual do elevador e manteve destravada a porta do pavimento. Considerou a possibilidade do elevador descer, monitorando as duas portas, a localização da cabine no pavimento superior e o deslocamento para o piso inferior. | Não monitorou o estado atual e não manteve destravada a porta, mas considerou a descida com portas e localização monitoradas. | Monitorou estado atual e manteve destravada a porta, mas não considerou a possibilidade de descer. | Não monitorou estado, não manteve destravada a porta e não considerou a possibilidade de descer. |
| **3ª** | **Controle do elevador no pavimento inferior para deslocamento ao pavimento superior (Chamada externa)** | Monitorou o estado atual das portas, deslocando a cabine do elevador para o pavimento superior, quando o botão é pressionado. Chegando ao pavimento superior, as suas portas são destrancadas. | Não monitorou o estado das portas, mas deslocou a cabine e destrancou ao chegar. (1,7 pts) | Monitorou o estado das portas, mas não deslocou a cabine. | Não monitorou o estado das portas e nem deslocou a cabine. |
| **4ª** | **Controle do elevador no pavimento superior para deslocamento ao pavimento inferior (Chamada externa)** | Monitorou o estado atual das portas, deslocando a cabine do elevador para o pavimento inferior, quando o botão é pressionado. Chegando ao pavimento inferior, as suas portas são destrancadas. | Não monitorou o estado das portas, mas deslocou a cabine e destrancou ao chegar. (1,7 pts) | Monitorou o estado das portas, mas não deslocou a cabine. | Não monitorou o estado das portas e nem deslocou a cabine. |

---

## 2. Critério 5: Autonomia do Estudante (Fator Redutor)

| Nível de Autonomia | Ação Observada pelo Docente | Impacto na Nota Final |
| :--- | :--- | :---: |
| **Autônomo (Excelente)** | Desenvolveu todas as atividades de forma autônoma e independente em relação ao docente, sem nenhuma ajuda. | **0 pontos (Sem desconto)** |
| **Pouca intervenção** | O aluno solicitou 1 vez a ajuda do docente para solucionar alguma atividade da prática. | **-0,5 pontos** |
| **Intervenção moderada** | O aluno solicitou até 2 vezes a ajuda do docente para solucionar alguma atividade. | **-1,5 pontos** |
| **Alta dependência** | O aluno solicitou mais de 2 vezes a ajuda do docente. | **-3,0 pontos** |

---

## 3. Roteiro de Testes para o Aluno Garantir Nota 10,0

Para atingir **Conceito A em todas as 4 etapas**:

1. **Teste da Situação 1:**
   - Com o elevador no 1º pavimento, pressione `Botao_desce_1` (%I0.1). O motor **não deve ligar**.
   - Verifique se a Tranca 1 está em 0 (Porta 1 livre).
   - Feche as portas e pressione `Botao_sobe_1` (%I0.0). A cabine deve subir, trancando ambas as portas durante o percurso.
   - Ao atingir o 2º pavimento, o motor desliga e a Tranca 2 destrava (%Q0.3 = 0).

2. **Teste da Situação 2:**
   - Com o elevador no 2º pavimento, pressione `Botao_sobe_2` (%I0.4). O motor **não deve ligar**.
   - Verifique se a Tranca 2 está em 0 (Porta 2 livre).
   - Feche as portas e pressione `Botao_desce_2` (%I0.5). A cabine deve descer, trancando ambas as portas durante o trajeto.
   - Ao atingir o 1º pavimento, o motor desliga e a Tranca 1 destrava (%Q0.2 = 0).

3. **Teste da Situação 3 (Chamada):**
   - Com o elevador no 1º pavimento, pressione `Botao_sobe_2` (%I0.4) no painel do 2º andar.
   - O elevador deve subir até o 2º piso e destrancar a porta do 2º andar ao nivelar.

4. **Teste da Situação 4 (Chamada):**
   - Com o elevador no 2º pavimento, pressione `Botao_desce_1` (%I0.1) no painel do 1º andar.
   - O elevador deve descer até o 1º piso e destrancar a porta do 1º andar ao nivelar.

5. **Teste de Intertravamento de Segurança (NR-12):**
   - Tente acionar qualquer subida ou descida com uma das portas abertas $\rightarrow$ O motor **não deve partir**.
   - Abra uma porta enquanto a cabine estiver em movimento $\rightarrow$ O motor **deve parar instantaneamente**.
