# Teste Completo do Sistema OpenMyMind Project 007

## Visão Geral

Este documento descreve o sistema de testes completo para o OpenMyMind Project 007, incluindo validação de todas as etapas do pipeline, sistema neural e integração geral.

## Arquivos do Sistema

### 1. `openmymind_pipeline_007.py`
- Pipeline principal completo
- Implementação neural (TCN + Cross-Attention + Meta-Learning)
- Coleta multi-fonte (Tweets, Orderbook, On-Chain, Whale Alerts)
- Validação cruzada robusta
- Persistência SQLite
- Backtest com YFinance

### 2. `test_openmymind_completo.py`
- Script de teste completo
- Validação de todas as etapas
- Relatório JSON automático
- Tratamento de erros graceful

## Como Executar o Teste

### Pré-requisitos

```bash
pip install torch pandas numpy ccxt snscrape requests sqlalchemy yfinance vectorbt
```

### Variáveis de Ambiente (Opcional)

```bash
export ETHERSCAN_API_KEY="your_key"  # Para coleta on-chain
export WHALEALERT_API_KEY="your_key"  # Para whale alerts
export ASSET_SYMBOL="BTC/USDT"
export DATA_DIR="./data"
export DB_FILE="./openmymind.db"
```

### Execução

```bash
# Executar teste completo
python Core/Backtesting/test_openmymind_completo.py

# Ou executar pipeline principal
python Core/Backtesting/openmymind_pipeline_007.py
```

## Etapas do Teste

O teste completo valida as seguintes etapas:

1. **Inicialização do Banco de Dados**
   - Criação de tabelas SQLite
   - Validação de conexão

2. **Coleta de Dados**
   - Tweets (snscrape)
   - Orderbook (CCXT)
   - On-Chain (Etherscan)
   - Whale Alerts (Whale-Alert API)

3. **Validação Cruzada**
   - Eventos validados por múltiplas fontes
   - Sistema de scoring ponderado
   - Janela temporal de 1 hora

4. **Persistência**
   - Armazenamento de sinais validados
   - Backup em arquivos JSON

5. **Backtest**
   - YFinance para preços históricos
   - VectorBT (se disponível) ou fallback Pandas
   - Métricas de performance

6. **Sistema Neural**
   - Neural Fusion Engine
   - Processamento multi-fonte
   - Risk Manager dinâmico

## Saída do Teste

### Relatório JSON

O teste gera um relatório JSON completo em:
```
data/relatorio_teste_YYYYMMDDTHHMMSS.json
```

### Estrutura do Relatório

```json
{
  "timestamp": "2025-11-17T12:00:00",
  "status": "SUCESSO|FALHA_PARCIAL|SUCESSO_COM_AVISOS",
  "detalhes": {
    "db": {"status": "OK", "arquivo": "..."},
    "tweets": {"status": "OK", "registros": 10},
    "orderbook": {"status": "OK", "coletado": true},
    "onchain": {"status": "OK", "registros": 5},
    "whale_alert": {"status": "OK", "registros": 3},
    "validacao": {"status": "OK", "eventos_validados": 2},
    "persistencia": {"status": "OK", "sinais_persistidos": 2},
    "backtest": {"status": "OK", "metricas": {...}},
    "neural": {"status": "OK", "predictions_shape": "...", "risk_params": {...}},
    "resumo": {
      "total_etapas": 9,
      "sucesso": true,
      "erros_encontrados": 0,
      "erros": []
    }
  }
}
```

## Tratamento de Erros

O sistema de teste é **graceful** - continua a execução mesmo se algumas APIs não estiverem disponíveis:

- **APIs ausentes**: Teste continua, marca como aviso
- **Dados insuficientes**: Teste continua, relata no resumo
- **Erros críticos**: Teste interrompe, gera relatório de erro

## Status de Saída

O script retorna códigos de saída padrão:

- `0`: Sucesso completo
- `1`: Falha parcial ou completa
- `130`: Interrompido pelo usuário (Ctrl+C)

## Integração com CI/CD

O teste pode ser integrado em pipelines CI/CD:

```bash
# Exemplo para GitHub Actions
python Core/Backtesting/test_openmymind_completo.py
if [ $? -eq 0 ]; then
    echo "Teste passou com sucesso"
else
    echo "Teste falhou - verificar relatório"
    exit 1
fi
```

## Notas Importantes

1. **Dados Reais**: O teste tenta coletar dados reais, mas funciona com dados simulados se APIs não estiverem disponíveis
2. **Rate Limiting**: Respeitar limites de taxa das APIs externas
3. **Segurança**: Nunca commitar credenciais - usar variáveis de ambiente
4. **Performance**: O teste completo pode levar vários minutos dependendo das APIs

## Próximos Passos

1. Executar teste completo para validação inicial
2. Revisar relatório JSON gerado
3. Ajustar configurações conforme necessário
4. Integrar em pipeline CI/CD para validação contínua

---

**Projeto:** Prometheus v3.0 - Horizonte  
**Status:** Teste de Integração  
**Versão:** 1.0

