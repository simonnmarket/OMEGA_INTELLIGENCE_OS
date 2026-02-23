# OpenMyMind Project 007
## Pipeline Único Completo com Neural Fusion e Monitoramento Avançado

**Projeto:** Prometheus: Horizonte  
**Versão:** 1.0  
**Data:** 17 de Novembro de 2025  
**Status:** Ativo - Exploração Científica

---

## Visão Geral

O OpenMyMind Project 007 é um pipeline completo de coleta, validação cruzada e análise multi-fonte para detecção de eventos de "whale" (grandes transações) em criptomoedas. O projeto integra:

- **Coleta Multi-Fonte:** Tweets, Orderbook, On-Chain, Whale Alerts
- **Validação Cruzada Robusta:** Mínimo 2 fontes independentes para validação
- **Persistência:** SQLite para armazenamento estruturado
- **Backtest:** YFinance com fallback Pandas
- **Neural Fusion Engine:** TCN + Cross-Attention + Meta-Learning
- **Gestão Dinâmica de Risco:** Rede neural para cálculo adaptativo de parâmetros

---

## Arquitetura Neural

### 1. Temporal Convolutional Network (TCN)
- Processamento de séries temporais multi-fonte
- Dilatação exponencial para capturar dependências de longo prazo
- Dropout para regularização

### 2. Cross-Attention Fusion
- Fusão multi-modal de features
- Self-attention + Cross-attention
- Normalização por camadas (LayerNorm)

### 3. Meta-Learning Module
- Adaptação rápida a novos padrões
- Módulo de meta-aprendizado para fine-tuning

### 4. Risk Manager
- Estimativa dinâmica de:
  - Tamanho máximo de posição
  - Stop-loss adaptativo
  - Take-profit adaptativo

---

## Instalação

### Dependências Principais

```bash
pip install torch pandas numpy ccxt snscrape requests sqlalchemy yfinance vectorbt
```

### Variáveis de Ambiente

```bash
export ETHERSCAN_API_KEY="your_key"
export WHALEALERT_API_KEY="your_key"
export INFURA_KEY="your_key"
export ASSET_SYMBOL="BTC/USDT"
export SAMPLE_INTERVAL_SEC=60
export DATA_DIR="./data"
export DB_FILE="./openmymind.db"
```

---

## Uso

### Execução Completa (Ciclo Único)

```bash
python openmymind_pipeline_007.py
```

### Execução em Loop Contínuo

```bash
python openmymind_pipeline_007.py loop
```

### Comandos Individuais

```bash
# Inicializar banco de dados
python openmymind_pipeline_007.py --init-db

# Coletar tweets
python openmymind_pipeline_007.py --collect-tweets

# Coletar orderbook
python openmymind_pipeline_007.py --collect-orderbook

# Coletar dados on-chain
python openmymind_pipeline_007.py --collect-onchain

# Coletar whale alerts
python openmymind_pipeline_007.py --collect-whalealert

# Validar cruzadamente
python openmymind_pipeline_007.py --cross-validate

# Persistir sinais
python openmymind_pipeline_007.py --persist-signals

# Executar backtest
python openmymind_pipeline_007.py --run-backtest
```

---

## Fluxo de Dados

1. **Coleta Multi-Fonte:**
   - Tweets: snscrape (público)
   - Orderbook: CCXT (Binance)
   - On-Chain: Etherscan API
   - Whale Alerts: Whale-Alert API

2. **Validação Cruzada:**
   - Eventos on-chain grandes (>50 BTC)
   - Correspondência temporal (janela de 1 hora)
   - Mínimo 2 fontes independentes

3. **Persistência:**
   - SQLite para sinais validados
   - Arquivos Parquet para dados brutos
   - JSON para relatórios de ciclo

4. **Backtest:**
   - YFinance para preços históricos
   - VectorBT (se disponível) ou fallback Pandas
   - Equity curve e métricas de performance

---

## Estrutura de Dados

### Sinais Validados

```json
{
  "ts": "2025-11-17T12:00:00",
  "onchain": {...},
  "matched_whalealerts": [...],
  "matched_tweets": [...],
  "matched_orderbook": {...},
  "sources": ["onchain", "whale_alert"],
  "score": 1.4
}
```

### Banco de Dados

- **tabela `signals`**: Sinais validados persistidos
- **tabela `documents`**: Documentos coletados (tweets, etc.)

---

## Notas Importantes

1. **Dados Públicos:** Utiliza apenas APIs públicas e legais
2. **Rate Limiting:** Implementar rate limiting adequado para APIs externas
3. **Segurança:** Não armazenar credenciais no código - usar variáveis de ambiente
4. **Escalabilidade:** Para produção, considerar migração para PostgreSQL/InfluxDB

---

## Integração com Prometheus: Horizonte

Este projeto faz parte da estratégia "Prometheus: Horizonte" - uma exploração científica massiva para encontrar qualquer instância onde a hipótese "existe edge" possa ser validada.

O pipeline OpenMyMind 007 testa a hipótese específica:
> **"Grandes transações on-chain (whales) precedem movimentos significativos de preço quando validadas por múltiplas fontes independentes"**

---

## Próximos Passos

1. Treinar modelo neural com dados históricos
2. Implementar fine-tuning contínuo
3. Integrar com sistema de execução
4. Monitoramento em tempo real

---

## Contato

Projeto: Prometheus v3.0 - Horizonte  
Diretiva: Exploração Científica  
Status: Ativo

