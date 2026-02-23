# Robô Multiativos para MetaTrader 5

Este é um Expert Advisor (EA) desenvolvido para operar múltiplos ativos simultaneamente no MetaTrader 5.

## Características

- Operação em múltiplos ativos simultaneamente
- Estratégia baseada em Médias Móveis e RSI
- Gerenciamento de risco com Stop Loss e Take Profit
- Interface configurável para diferentes ativos

## Parâmetros de Configuração

### Configurações Gerais
- `Symbols`: Lista de símbolos para trading (ex: "EURUSD,GBPUSD,USDJPY")
- `LotSize`: Tamanho do lote para operações
- `StopLoss`: Stop Loss em pontos
- `TakeProfit`: Take Profit em pontos

### Configurações dos Indicadores
- `MA_Fast_Period`: Período da Média Móvel Rápida
- `MA_Slow_Period`: Período da Média Móvel Lenta
- `RSI_Period`: Período do RSI
- `RSI_UpperLevel`: Nível Superior do RSI
- `RSI_LowerLevel`: Nível Inferior do RSI

## Estratégia de Trading

O robô utiliza uma combinação de:
1. Cruzamento de Médias Móveis
2. Níveis de RSI para confirmação
3. Stop Loss e Take Profit para gerenciamento de risco

### Sinais de Compra
- MA Rápida cruza acima da MA Lenta
- RSI abaixo do nível inferior

### Sinais de Venda
- MA Rápida cruza abaixo da MA Lenta
- RSI acima do nível superior

## Instalação

1. Copie o arquivo `MultiAssetTrader.mq5` para a pasta `MQL5/Experts` do seu MetaTrader 5
2. Compile o EA no MetaEditor
3. Anexe o EA a um gráfico
4. Configure os parâmetros conforme sua preferência

## Aviso de Risco

Trading envolve risco. Este EA é fornecido apenas para fins educacionais. Use por sua conta e risco. 