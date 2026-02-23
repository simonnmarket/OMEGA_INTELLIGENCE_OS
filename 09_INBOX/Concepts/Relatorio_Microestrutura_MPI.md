# RELATÓRIO COMPLETO -- MAPEAMENTO DE BASES EXISTENTES PARA DESENVOLVIMENTO DO ÍNDICE DE PRESSÃO DE MERCADO (MPI)

## 1. Objetivo do Relatório

Documentar todas as tecnologias, pesquisas, ferramentas e modelos
existentes que podem servir como base para o desenvolvimento do **Market
Pressure Index (MPI)** -- um indicador unificado de pressão e risco de
mercado baseado em microestrutura, volume, liquidez, regime e fluxo
institucional.

------------------------------------------------------------------------

## 2. Tecnologias, Conceitos e Pesquisas Existentes

### 2.1 MIDAS Technical Analysis

Método baseado em curvas de volume cumulativo que modelam suportes e
resistências dinâmicas. - Pode ser adaptado para estrutura do MPI como
contexto dinâmico. - Base científica bem documentada.

### 2.2 Order Flow & Limit Order Book Resiliency

Estudos que mostram como: - desequilíbrios no book, - profundidade, - e
agressão vs. passividade\
preveem movimentos futuros. Base para medir "pressão" real
institucional.

### 2.3 Bayesian Change-Point -- Modelos de mudança de regime

Modelos para detectar transições de regime em: - volatilidade, -
fluxo, - liquidez. Crucial para calibrar limites do MPI dinamicamente
("mudança de maré").

### 2.4 Modelos de Liquidez e Volatilidade Microestrutural

Relacionam liquidez com: - risco, - probabilidade de ruptura, -
comportamento do spread, - velocidade do preço.

### 2.5 Ferramentas práticas no mercado

-   Bookmap\
-   Sierra Chart\
-   ATAS\
-   ExoCharts\
-   NinjaTrader Order Flow+

Estas ferramentas inspiram o modelo visual do MPI: - heatmaps, -
clusters, - footprint, - absorção, - volume profile.

------------------------------------------------------------------------

## 3. Componentes Técnicos Aproveitáveis

### 3.1 Delta de agressão

-   Delta por nível
-   Delta cumulativo
-   Imbalance

### 3.2 Liquidez passiva

-   Depth imbalance
-   Gaps de liquidez
-   Mapa de liquidez futura

### 3.3 Volume Profile / Market Profile

-   HVN
-   LVN
-   POC shifts

### 3.4 Volatilidade & Velocidade

-   ticks/ms
-   magnitude do candle

### 3.5 Regime do mercado

-   Detecção de regime dinâmico
-   Ajuste automático de thresholds

------------------------------------------------------------------------

## 4. Proposta Final de Adaptação -- Market Pressure Index (MPI)

### Estrutura (pontuação 0--100)

-   0--30: Verde (Pressão baixa)\
-   30--60: Amarelo (Atenção)\
-   60--80: Laranja (Alerta)\
-   80--100: Vermelho (Risco extremo)

### Fórmula Base

MPI =\
w1 \* Delta Score +\
w2 \* Liquidity Score +\
w3 \* Volume Profile Score +\
w4 \* Price Velocity Score +\
w5 \* Regime Score

Pesos ajustáveis e calibráveis.

------------------------------------------------------------------------

## 5. Aplicações

-   Qualquer ativo ou derivativo\
-   Dashboard institucional\
-   Análise profissional\
-   Sistemas quant\
-   Alertas de risco (tsunami detect system)

------------------------------------------------------------------------

## 6. Conclusão

A construção do MPI utiliza: - microestrutura,\
- matemática aplicada,\
- engenharia,\
- física de fluxo,\
- ferramentas existentes,\
- pesquisas robustas.

Este documento é a **versão oficial da fase de mapeamento** do projeto.
