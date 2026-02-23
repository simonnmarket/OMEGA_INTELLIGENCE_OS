#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE RELATÓRIO DE SOLICITAÇÃO: VALIDAÇÃO PÓS-DEPLOYMENT PROMETHEUS v4.2

Este script gera um documento de solicitação para validar a transição do Prometheus v4.0 para o v4.2.
"""

import os
from datetime import datetime

# --- CONTEÚDO DO RELATÓRIO (TEMPLATE) ---
report_content = f"""# RELATÓRIO DE SOLICITAÇÃO: VALIDAÇÃO PÓS-DEPLOYMENT PROMETHEUS v4.2

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S CET')}  
**Para:** Comitê de Inteligência Artificial (AIC)  
**De:** Conselho de Tecnologia (Engenharia Sênior)  
**Status:** 🟡 **AGUARDANDO PREENCHIMENTO**  
**Missão:** Validar a transição do v4.0 para o v4.2 e garantir a excelência operacional.

---

## 🎯 **1. Resumo Executivo da Transição**

A transição do Prometheus v4.0 para o v4.2 introduziu um módulo de Gestão de Risco Dinâmico, mudando a arquitetura de execução de volume fixo para volume baseado em porcentagem de risco e Stop Loss/Take Profit baseados em ATR. Este relatório tem como objetivo validar se essa transição foi executada com sucesso e se o novo sistema é mais seguro e eficaz.

---

## 🔧 **2. Validação do Processo de Transição**

**INSTRUÇÕES:** Forneça evidências (logs, capturas de tela, descrições) para cada item abaixo.

### 2.1. Desligamento do Sistema v4.0

- [ ] **Desligamento Graceful:** O sistema v4.0 foi desligado sem erros? Forneça o último log do console.

- [ ] **Backup de Dados:** Os arquivos de log (`prometheus_master_log.jsonl`) e heartbeat foram arquivados?

- [ ] **Limpeza de Ambiente:** O processo `python prometheus_master_control_v4.1.py` foi finalizado?

### 2.2. Implantação do Sistema v4.2

- [ ] **Código Fonte:** O arquivo `prometheus_master_control_v4.2.py` foi salvo com o código completo?

- [ ] **Configurações:** Os novos dicionários `RISK_CONFIG` e `DISCOVERY_CONFIG` foram revisados e estão corretos?

- [ ] **Dependências:** Todas as dependências Python necessárias estão instaladas?

---

## 🧠 **3. Validação Técnica do Sistema v4.2**

**INSTRUÇÕES:** Verifique os logs do console e do arquivo `prometheus_master_log.jsonl` para validar cada módulo.

### 3.1. Inicialização e Conexão

- [ ] **MT5:** A conexão com o MetaTrader 5 foi estabelecida com sucesso no início?

- [ ] **Logger:** O sistema de logging estruturado em JSON foi inicializado corretamente?

- [ ] **Watchdog:** A thread do watchdog foi iniciada e está ativa?

### 3.2. Módulo de Descoberta (Discovery Engine)

- [ ] **Execução do Discovery:** O modo `discovery` foi executado sem erros?

- [ ] **Geração de `TRADEABLE_ASSETS.json`:** O arquivo foi gerado? Ele contém os campos `symbol`, `score`, `trades`, `profit_factor`?

- [ ] **Filtragem de Ativos:** O sistema filtrou ativos com base em `max_spread_points` e `min_tick_volume`?

---

## 🛡️ **4. Validação da Lógica de Gestão de Risco (CRÍTICO)**

Esta é a área mais importante da validação. Forneça logs detalhados ou evidências concretas.

### 4.1. Cálculo de Volume da Posição (`calculate_position_size`)

- [ ] **Lógica de Risco:** O volume está sendo calculado como `1% do capital`? Verifique o log `"event": "POSITION_SIZE_CALCULATED"` e confirme o cálculo.

- [ ] **Ajuste de Lote:** O volume calculado está sendo ajustado para o `volume_min` do símbolo?

- [ ] **Exemplo:** Para um capital de $10.000 e um SL de 50 pontos no EURUSD (valor do ponto = $0.0001), o volume calculado deve ser 2.0 lotes. O sistema executou com esse volume?

### 4.2. Verificação de Risco Global (`check_global_risk`)

- [ ] **Drawdown Diário:** O sistema está calculando o drawdown diário corretamente?

- [ ] **Limite de Risco:** O sistema já parou a operação por atingir o `max_daily_drawdown_percent`? Se sim, forneça o log `"event": "RISK_LIMIT_HIT"`.

- [ ] **Posições Abertas:** O sistema está respeitando o `max_open_positions`?

### 4.3. SL/TP Dinâmicos (Baseados em ATR)

- [ ] **Cálculo de ATR:** O Average True Range (ATR) está sendo calculado corretamente para cada ativo?

- [ ] **Aplicação no Sinal:** O SL está sendo definido como `entry_price - 2 * ATR` e o TP como `entry_price + 4 * ATR`?

- [ ] **Comparação:** Compare um sinal do v4.0 (SL/TP fixos) com um sinal do v4.2 (SL/TP dinâmicos) para o mesmo ativo. Os valores são diferentes e fazem sentido?

---

## 📈 **5. Validação de Performance e Estabilidade**

### 5.1. Desempenho

- [ ] **Uso de CPU/Memória:** O uso de recursos do sistema v4.2 é comparável ao do v4.0? Houve algum aumento significativo?

- [ ] **Tempo de Ciclo:** O tempo de cada ciclo de produção (incluindo cálculos de risco) está dentro do esperado (< 30 segundos)?

### 5.2. Estabilidade

- [ ] **Crashes/Freezes:** O sistema travou, congelou ou apresentou algum `FATAL_ERROR` nas últimas 24 horas?

- [ ] **Watchdog:** O watchdog reiniciou o sistema em algum momento? Se sim, forneça o log `"event": "WATCHDOG_CRITICAL"`.

---

## 📊 **6. Comparação de Resultados (v4.0 vs v4.2)**

### 6.1. Descoberta de Ativos

- [ ] **Ranking de Ativos:** O ranking de ativos no `TRADEABLE_ASSETS.json` mudou significativamente entre as versões? Se sim, por quê? (A nova lógica de score é mais robusta?)

### 6.2. Geração de Sinais e Execução

- [ ] **Volume de Ordens:** Ordens estão sendo executadas com volumes diferentes? O volume está mais conservador ou agressivo?

- [ ] **SL/TP:** Os Stop Losses e Take Profits estão mais distantes ou próximos da entrada em comparação com os fixos de 50/100 pontos?

- [ ] **Frequência:** A frequência de sinais gerados aumentou ou diminuiu?

---

## 📋 **7. Logs e Observabilidade**

- [ ] **Novos Eventos:** Os novos eventos de log (`POSITION_SIZE_CALCULATED`, `RISK_LIMIT_HIT`, `ATR_BASED_SL_TP`) estão aparecendo corretamente no `prometheus_master_log.jsonl`?

- [ ] **Parseabilidade:** Os logs continuam sendo gerados em formato JSON válido e podem ser facilmente analisados?

---

## 🏆 **8. Veredito Final e Próximos Passos**

### 8.1. Veredito da Transição (AIC)

Marque apenas uma opção:

- [ ] **SUCESSO TOTAL:** O v4.2 é superior em todos os aspectos (segurança, performance, lógica) e está pronto para substituir o v4.0 permanentemente.

- [ ] **SUCESSO PARCIAL:** O v4.2 é funcional, mas apresenta problemas em áreas específicas (detalhe quais). Correções são necessárias antes da substituição total.

- [ ] **FALHA:** A transição introduziu problemas críticos que tornam o v4.2 inoperável. É recomendado um rollback para o v4.0.

### 8.2. Recomendações do AIC

Com base no veredito acima, quais são as próximas ações?

- [ ] **Prosseguir com v4.2:** Manter o sistema v4.2 em produção.

- [ ] **Corrigir e Testar:** Corrigir os problemas identificados e re-executar a validação.

- [ ] **Rollback para v4.0:** Desligar o v4.2 e reativar o sistema v4.0, documentando os motivos da falha.

---

## 📎 **Entrega do Relatório**

**Ação do AIC:** Preencha este relatório com o máximo de detalhes e evidências possíveis. Salve o arquivo preenchido como `V4_2_DEPLOYMENT_REPORT_COMPLETED.md` e envie-o ao Conselho de Tecnologia para análise final.

---

**ASSINATURA:**  
Relatório Solicitado por Engenharia Sênior  
Timestamp: {datetime.now().isoformat()}
"""

# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    output_filename = "V4_2_DEPLOYMENT_REPORT_REQUEST.md"
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print("="*80)
        print(f"✅ RELATÓRIO DE SOLICITAÇÃO GERADO COM SUCESSO!")
        print(f"📁 Arquivo salvo como: {output_filename}")
        print("📋 Preencha o documento com as evidências da transição v4.0 -> v4.2.")
        print("="*80)
        
    except Exception as e:
        print(f"❌ ERRO AO GERAR O ARQUIVO DE RELATÓRIO: {e}")

