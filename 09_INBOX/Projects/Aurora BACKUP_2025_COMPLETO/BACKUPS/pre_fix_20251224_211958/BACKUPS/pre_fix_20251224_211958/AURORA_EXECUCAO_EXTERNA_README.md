# AURORA v5.1 - GUIA DE EXECUÇÃO EXTERNA

## 📋 VISÃO GERAL

Este documento descreve como executar o sistema Aurora **fora do Cursor**, de forma independente, com integração ao MetaTrader 5 para visualização de ordens em tempo real.

---

## 🎯 OBJETIVOS

1. ✅ Executar sistema Aurora externamente (processo Python independente)
2. ✅ Visualizar ordens sendo abertas no MetaTrader 5 em tempo real
3. ✅ Gerar logs e relatórios externos
4. ✅ Manter sistema rodando em background se necessário

---

## 🚀 EXECUÇÃO RÁPIDA

### Windows (PowerShell)

```powershell
cd C:\Users\Lenovo\Projects\Aurora
.\executar_aurora_externo.ps1 alpha
```

### Windows (CMD/Batch)

```cmd
cd C:\Users\Lenovo\Projects\Aurora
executar_aurora_externo.bat alpha
```

### Python Direto

```bash
cd C:\Users\Lenovo\Projects\Aurora
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py alpha
```

---

## 📊 FASES DE EXECUÇÃO

### FASE α (30 minutos) - Teste Científico

**Objetivo:** Validar hipótese científica de MA crossover em crypto

**Comando:**
```bash
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py alpha
```

**O que faz:**
- Testa estratégia MA(10/50) crossover em 5 criptomoedas
- Valida edge estatístico (Sharpe, Win Rate, Retorno)
- Gera relatório científico completo

**Resultado esperado:**
- Arquivo JSON: `aurora_aic_results_YYYYMMDD_HHMMSS.json`
- Relatório texto: `aurora_aic_report_YYYYMMDD_HHMMSS.txt`

---

### FASE β (24 horas) - Validação de Infraestrutura

**Objetivo:** Validar sistema Aurora completo (240 módulos) por 24h

**Comando:**
```bash
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py beta
```

**⚠️ ATENÇÃO:** Esta fase requer confirmação manual (24h é longo)

**O que faz:**
- Executa sistema completo por 24 horas
- Valida todos os 240 módulos operacionais
- Testa coleta de dados, comunicação de agentes, uptime
- Monitora erros críticos

**Resultado esperado:**
- Validação completa da infraestrutura
- Relatório de uptime e performance

---

### FASE γ (2-4 semanas) - Evolução Avançada

**Objetivo:** Evoluir Aurora com conceitos avançados (após α + β)

**Comando:**
```bash
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py gamma
```

**O que faz:**
- Gera roadmap de evolução
- Planeja implementação de:
  - Temporal Fusion Transformer (ML avançado)
  - Quantum Blockchain Audit (segurança)
  - Tier-1 Risk Management (governança)
  - Realtime Institutional Dashboard (monitoramento)

**Resultado esperado:**
- Roadmap completo de evolução
- Plano de implementação sem regressão

---

## 🔧 CONFIGURAÇÃO

### 1. Dependências Python

Instalar dependências necessárias:

```bash
pip install yfinance pandas numpy aiohttp
```

Ou usar o requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. MetaTrader 5

**Pré-requisitos:**
- MetaTrader 5 instalado
- Conta DEMO configurada
- MT5 rodando e conectado

**Integração:**
- O sistema Aurora enviará ordens via API MT5
- Ordens aparecerão automaticamente no terminal MT5
- Visualização em tempo real garantida

### 3. Execução em Background (Opcional)

**Windows (PowerShell):**

```powershell
Start-Process powershell -ArgumentList "-File", "executar_aurora_externo.ps1", "alpha" -WindowStyle Hidden
```

**Windows (CMD):**

```cmd
start /B executar_aurora_externo.bat alpha
```

---

## 📁 ESTRUTURA DE ARQUIVOS

```
Aurora/
├── AURORA_FINAL_EXECUCAO_AIC_V5.1.py    # Script principal
├── executar_aurora_externo.bat           # Execução Windows CMD
├── executar_aurora_externo.ps1           # Execução Windows PowerShell
├── aurora_aic_results_*.json              # Resultados JSON (gerado)
├── aurora_aic_report_*.txt               # Relatórios texto (gerado)
└── logs/                                  # Logs do sistema (se configurado)
```

---

## 📊 MONITORAMENTO

### Visualização no MT5

1. Abra MetaTrader 5
2. Conecte à conta DEMO
3. Abra a aba "Trade" ou "Terminal"
4. Ordens do Aurora aparecerão automaticamente

### Logs e Relatórios

**Relatórios gerados:**
- `aurora_aic_results_*.json` - Dados completos em JSON
- `aurora_aic_report_*.txt` - Relatório legível em texto

**Conteúdo dos relatórios:**
- Resultados de cada fase
- Métricas de performance
- Decisões finais
- Próximos passos recomendados

---

## ⚙️ PARÂMETROS DE EXECUÇÃO

### Argumentos do Script

```bash
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py [FASE] [OPÇÕES]
```

**Fases disponíveis:**
- `alpha` - Teste científico (30min)
- `beta` - Validação infraestrutura (24h)
- `gamma` - Evolução avançada (após α+β)
- `all` - Todas as fases sequencialmente

**Ajuda:**
```bash
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py --help
```

---

## 🔍 TROUBLESHOOTING

### Erro: "Python não encontrado"

**Solução:**
- Instalar Python 3.8+ do site oficial
- Adicionar Python ao PATH do sistema
- Verificar: `python --version`

### Erro: "ModuleNotFoundError: yfinance"

**Solução:**
```bash
pip install yfinance pandas numpy aiohttp
```

### Ordens não aparecem no MT5

**Verificar:**
1. MT5 está rodando e conectado?
2. Conta DEMO está ativa?
3. API MT5 está configurada corretamente?
4. Verificar logs do sistema Aurora

### Sistema não executa externamente

**Verificar:**
1. Está executando fora do Cursor?
2. Terminal/PowerShell tem permissões?
3. Diretório do projeto está correto?

---

## ✅ CHECKLIST PRÉ-EXECUÇÃO

Antes de executar, verificar:

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (yfinance, pandas, numpy, aiohttp)
- [ ] MetaTrader 5 instalado e rodando
- [ ] Conta DEMO configurada no MT5
- [ ] Executando fora do Cursor (terminal/PowerShell)
- [ ] Diretório do projeto correto

---

## 📞 SUPORTE

**Problemas técnicos:**
- Verificar logs gerados
- Consultar documentação técnica
- Revisar código do script principal

**Dúvidas sobre execução:**
- Consultar este README
- Verificar comentários no código
- Analisar relatórios gerados

---

## 🎯 PRÓXIMOS PASSOS

Após execução bem-sucedida:

1. **FASE α aprovada:**
   - Prosseguir para FASE β (validação 24h)
   - Ou analisar resultados e ajustar hipótese

2. **FASE β aprovada:**
   - Prosseguir para FASE γ (evolução avançada)
   - Ou otimizar infraestrutura se necessário

3. **FASE γ concluída:**
   - Implementar roadmap de evolução
   - Manter sistema 100% operacional
   - Zero regressão garantida

---

**Última atualização:** 2025-12-20  
**Versão:** 5.1  
**Status:** ✅ Pronto para execução externa

