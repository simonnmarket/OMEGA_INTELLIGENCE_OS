# 🥈 PROMETHEUS SILVER - SISTEMA ESPECIALIZADO EM PRATA (XAG)

**Versão:** 2.3 (Sistema Isolado)  
**Data:** 26 de Novembro de 2025  
**Status:** ✅ **SISTEMA ISOLADO E INDEPENDENTE**

---

## 🎯 OBJETIVO

Sistema de trading autônomo **especializado exclusivamente em prata (XAG)**, isolado do sistema principal Prometheus para evitar conflitos e permitir evolução independente.

---

## 📊 SÍMBOLOS OPERADOS

O Sistema Silver opera **APENAS** com os seguintes símbolos:

- **XAGUSD** (Prata/USD)
- **XAGAUD** (Prata/AUD)
- **XAGEUR** (Prata/EUR)
- **XAGGBP** (Prata/GBP)

---

## 🔑 CARACTERÍSTICAS DO SISTEMA

### Configuração Específica

- **Magic Number:** `99992` (diferente do sistema principal `99991`)
- **Log File:** `prometheus_silver_telemetry.log` (isolado)
- **Símbolos:** Hardcoded (não depende de arquivos externos)
- **Estratégia:** MA20 > MA50 (BUY apenas)

### Gestão de Risco

- **Stop Loss:** 20 pips
- **Take Profit Parcial:** 40 pips (fecha 50% do volume)
- **Take Profit Final:** 80 pips
- **Break-Even:** Ativado em 15 pips de lucro
- **Trailing Stop:** 20 pips de distância (após BE)
- **Volume:** 0.02 lotes (permite fechamento parcial de 0.01)

---

## 📁 ESTRUTURA DE ARQUIVOS

```
Prometheus_Silver/
├── prometheus_silver_v2.3.py          # Sistema principal
├── analise_performance_silver.py      # Análise de performance
├── verificar_horario_trading_xag.py   # Verificador de horário
├── EXECUTAR_SILVER.bat                # Atalho Windows
├── EXECUTAR_SILVER.ps1                # Script PowerShell
├── COMANDOS_POWERSHELL_SILVER.txt     # Comandos prontos
├── README_SISTEMA_SILVER.md           # Esta documentação
└── prometheus_silver_telemetry.log    # Log de operações (gerado automaticamente)
```

---

## 🚀 COMO EXECUTAR

### Método 1: PowerShell (Recomendado)

```powershell
cd "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia\Prometheus_Silver"
python prometheus_silver_v2.3.py
```

### Método 2: Atalho Windows

Duplo clique em: `EXECUTAR_SILVER.bat`

### Método 3: Script PowerShell

```powershell
cd "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia\Prometheus_Silver"
.\EXECUTAR_SILVER.ps1
```

---

## 📊 ANÁLISE DE PERFORMANCE

Para analisar a performance do Sistema Silver:

```powershell
cd "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia\Prometheus_Silver"
python analise_performance_silver.py
```

---

## ⏰ HORÁRIOS DE TRADING (Berlim - CET)

### Melhores Janelas para Prata:

1. **09:00-12:00 CET** ⭐ EXCELENTE
   - Abertura de Londres
   - Maior mercado físico de prata

2. **14:00-17:00 CET** ⭐⭐ IDEAL
   - Sobreposição Londres-NY
   - Maior volume e movimentos limpos

3. **17:00-19:00 CET** ⭐ BOM
   - Continuação NY
   - Ainda muito bom

### Evitar:

- **23:00-09:00 CET** ❌ EVITAR
  - Sessão Asiática
  - Baixa liquidez

### Verificar Horário Antes de Executar:

```powershell
python verificar_horario_trading_xag.py
```

---

## 🔒 ISOLAMENTO DO SISTEMA PRINCIPAL

### Diferenças que Garantem Isolamento:

| Característica | Sistema Principal | Sistema Silver |
|----------------|-------------------|----------------|
| **Magic Number** | 99991 | 99992 |
| **Log File** | prometheus_telemetry_v2.3.log | prometheus_silver_telemetry.log |
| **Símbolos** | Todos do Market Watch | Apenas 4 XAG |
| **Configuração** | Arquivo externo | Hardcoded |
| **Pasta** | Numeia/ | Numeia/Prometheus_Silver/ |

### Por que está isolado?

1. **Magic Number diferente:** Ordens não se misturam
2. **Log separado:** Análises independentes
3. **Pasta separada:** Arquivos não conflitam
4. **Configuração hardcoded:** Não depende de arquivos externos

---

## 📈 ESTRATÉGIA

### Sinal de Entrada (BUY)

- **Condição:** MA20 > MA50
- **Timeframe:** M15
- **Ação:** Apenas BUY (compras)

### Saída

1. **TP Parcial:** 40 pips (fecha 50%)
2. **Break-Even:** 15 pips (move SL para entrada)
3. **Trailing Stop:** 20 pips (após BE)
4. **TP Final:** 80 pips
5. **Reversão de Sinal:** Fecha se MA20 < MA50

---

## 🛡️ TRATAMENTO DE ERROS

### Erro 10018 (Mercado Fechado)

O sistema detecta e trata automaticamente:
- Verifica se mercado está aberto antes de executar
- Se receber erro 10018, registra e pula o símbolo
- Continua rodando e tenta novamente no próximo ciclo

---

## 📋 CHECKLIST ANTES DE EXECUTAR

- [ ] MetaTrader 5 está aberto e conectado
- [ ] Símbolos XAG estão no Market Watch
- [ ] Verificar horário de trading (09:00-12:00 ou 14:00-17:00 CET)
- [ ] Conta tem fundos suficientes
- [ ] Trading está habilitado na conta

---

## 🔧 DEPENDÊNCIAS

```bash
pip install MetaTrader5 numpy
```

---

## 📝 LOGS E TELEMETRIA

### Arquivo de Log

- **Nome:** `prometheus_silver_telemetry.log`
- **Formato:** JSON Lines
- **Localização:** Mesma pasta do script

### Eventos Registrados

- `system_init` - Inicialização
- `system_connected` - Conexão MT5
- `discovery_complete` - Validação de símbolos
- `signal_detected` - Sinal BUY detectado
- `position_opened` - Ordem executada
- `position_closed` - Posição fechada
- `position_partially_closed` - Fechamento parcial
- `risk_management` - BE/TS ativados
- `error_opening` - Falha na execução

---

## 🎯 PRÓXIMOS PASSOS

1. **Monitorar Performance:** Executar análise diariamente
2. **Ajustar Parâmetros:** Se necessário, editar `RISK_CONFIG` no código
3. **Manter Isolado:** Não misturar com sistema principal

---

## ⚠️ IMPORTANTE

- **NÃO modificar o Magic Number** (99992) - isso quebraria o isolamento
- **NÃO copiar arquivos** entre sistemas - cada um tem sua configuração
- **NÃO executar ambos simultaneamente** - pode causar conflitos de recursos

---

**Sistema desenvolvido para operação especializada em Prata (XAG)**  
**Isolado e independente do sistema principal Prometheus**

