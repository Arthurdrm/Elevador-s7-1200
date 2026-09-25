# Manual de Operação e Configuração no Siemens TIA Portal
## Projeto: Elevador de Carga S7-1200 | Desafio Industrial SENAI

---

## 1. Criação do Projeto no TIA Portal

1. Abra o **Totally Integrated Automation Portal (TIA Portal)** (versões V15.1, V16, V17, V18 ou V19).
2. Na tela inicial (*Portal View*), clique em **Create new project**:
   - **Project name:** `Projeto_Elevador_S7_1200`
   - **Author:** `Estudante Técnico SENAI / AutoControl`
   - Clique em **Create**.
3. Clique em **Configure a device** $\rightarrow$ **Add new device**.
4. Selecione a CPU padrão utilizada nos laboratórios do SENAI:
   - **SIMATIC S7-1200** $\rightarrow$ **CPU** $\rightarrow$ **CPU 1214C DC/DC/DC**
   - Código de referência comum: `6ES7 214-1AG40-0XB0` (ou a versão de firmware instalada na sua bancada, ex: V4.4 ou V4.5).
   - Clique em **Add**.

---

## 2. Importação das Tags do CLP (PLC Tags)

Para garantir que 100% dos nomes e comentários fiquem idênticos aos da folha do desafio:

### Método A: Importando o arquivo CSV (Recomendado)
1. Na árvore de projeto à esquerda, expanda:
   `PLC_1 [CPU 1214C ...]` $\rightarrow$ `PLC tags` $\rightarrow$ **Show all tags**.
2. Na barra de ferramentas superior da tabela de tags, clique no ícone **Import** (seta apontando para dentro de uma pasta).
3. Selecione o arquivo:
   `Projeto_Elevador_s7-1200/tags/PLC_Tags_Elevador.csv`
4. O TIA Portal preencherá instantaneamente todas as 12 variáveis físicas (`%I0.0` a `%I0.7` e `%Q0.0` a `%Q0.3`) com nomes e comentários formatados.

### Método B: Importando via XML (TIA Portal Openness)
1. Se preferir XML, use o arquivo `tags/PLC_Tags_Elevador.xml` através do menu de importação Openness/XML.

---

## 3. Implementação da Lógica de Controle

Você tem duas alternativas igualmente aceitas pela banca avaliadora:

### Alternativa 1: Desenho das Redes em Linguagem Ladder (LAD)
1. Expanda `Program blocks` $\rightarrow$ abra o bloco **Main [OB1]**.
2. Certifique-se de que a linguagem do bloco está configurada como **LAD**.
3. Abra o arquivo [LADDER_DIAGRAM_GUIDE.md](file:///home/teste/Área%20de%20trabalho/projetos/Projeto_Elevador_s7-1200/docs/LADDER_DIAGRAM_GUIDE.md) e insira as Networks 1 a 6.

### Alternativa 2: Importando o Bloco SCL Estruturado
1. Na árvore do projeto, expanda `External source files`.
2. Dê um duplo clique em **Add new external source file**.
3. Selecione o arquivo:
   `src/Elevador_Controle_S7_1200.scl`
4. Clique com o botão direito no arquivo importado e selecione **Generate blocks from source**.
5. O TIA Portal criará automaticamente:
   - Bloco de Dados: `DB_Elevador`
   - Bloco de Função: `FB_Controle_Elevador`
   - Bloco Principal: `Main [OB1]`

---

## 4. Compilação e Verificação de Erros

1. Clique com o botão direito na pasta raiz do CLP (`PLC_1`).
2. Selecione **Compile** $\rightarrow$ **Hardware and software (only changes)** ou **(rebuild all)**.
3. Observe a janela inferior (*Info / Compile*):
   - **Errors: 0**
   - **Warnings: 0**

---

## 5. Simulação com o S7-PLCSIM

Caso a atividade seja realizada em laboratório de informática sem o CLP físico conectado:
1. Na barra superior do TIA Portal, clique no ícone **Start simulation** (ícone de um CLP com visor azul).
2. O **S7-PLCSIM** será carregado.
3. Na janela de download que se abre no TIA Portal:
   - **PG/PC interface type:** `PN/IE`
   - **PG/PC interface:** `PLCSIM`
   - Clique em **Start search** $\rightarrow$ selecione o CLP simulado $\rightarrow$ clique em **Load**.
4. Marque a opção **Start module** e clique em **Finish**.
5. Crie uma **SIM Table** no PLCSIM com as tags `%I0.0` a `%I0.7` e `%Q0.0` a `%Q0.3` para forçar os sinais e validar o funcionamento.
6. Em paralelo, utilize o nosso **Simulador Gráfico Executável** em Python para ver a animação visual do elevador respondendo em tempo real!
