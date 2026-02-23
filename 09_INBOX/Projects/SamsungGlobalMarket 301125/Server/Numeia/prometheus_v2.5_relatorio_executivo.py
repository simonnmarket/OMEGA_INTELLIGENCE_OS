# ==============================================================================
# PROMETHEUS V2.5: RELATÓRIO EXECUTIVO PARA CONSELHO
# Objetivo: Gerar relatório formatado para apresentação ao conselho
# Data: 26/11/2025
# ==============================================================================

import json
import os
from datetime import datetime

# Arquivo JSON gerado pelo relatório científico
JSON_REPORT_FILE = "prometheus_relatorio_cientifico_v2.5.json"
OUTPUT_FILE = "PROMETHEUS_RELATORIO_CONSELHO_V2.5.md"

def formatar_valor_monetario(valor):
    """Formata valor monetário."""
    if valor >= 0:
        return f"${valor:,.2f}"
    else:
        return f"-${abs(valor):,.2f}"

def formatar_percentual(valor):
    """Formata percentual."""
    return f"{valor:.2f}%"

def obter_status_hipotese(status):
    """Retorna emoji e texto do status da hipótese."""
    if status == "SUCESSO":
        return "✅ SUCESSO"
    else:
        return "❌ FALHA"

def obter_status_sistema(status):
    """Retorna descrição do status do sistema."""
    if status == "OPERACIONAL":
        return "🟢 OPERACIONAL - Sistema funcionando dentro dos parâmetros esperados"
    elif status == "COM_PROBLEMAS":
        return "🟡 COM PROBLEMAS - Requer atenção e ajustes"
    else:
        return "🔴 CRÍTICO - Requer intervenção imediata"

def obter_avaliacao_performance(avaliacao):
    """Retorna descrição da avaliação de performance."""
    if avaliacao == "POSITIVA":
        return "📈 POSITIVA - Resultados acima das expectativas"
    elif avaliacao == "NEGATIVA":
        return "📉 NEGATIVA - Resultados abaixo das expectativas"
    else:
        return "➡️ NEUTRA - Resultados dentro do esperado"

def obter_recomendacao_acao(recomendacao):
    """Retorna descrição da recomendação."""
    if recomendacao == "CONTINUAR":
        return "✅ CONTINUAR - Sistema pode continuar operando normalmente"
    elif recomendacao == "REVISAR_ESTRATEGIA":
        return "⚠️ REVISAR ESTRATÉGIA - Necessário revisar e ajustar estratégia de trading"
    else:
        return "🔧 AJUSTAR - Necessário ajustar parâmetros operacionais"

def gerar_relatorio_executivo():
    """Gera relatório executivo formatado para conselho."""
    
    # Verificar se o JSON existe
    if not os.path.exists(JSON_REPORT_FILE):
        print(f"❌ ERRO: Arquivo {JSON_REPORT_FILE} não encontrado.")
        print("   Execute primeiro: python prometheus_v2.5_relatorio_cientifico.py")
        return
    
    # Ler JSON
    try:
        with open(JSON_REPORT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler JSON: {e}")
        return
    
    # Extrair dados
    resumo = data.get('resumo_executivo', {})
    detalhes = data.get('detalhes_metricas', {})
    analise_ceo = data.get('analise_ceo_cientifica', {})
    
    ordens = detalhes.get('relatorio_ordens_executadas', {})
    performance = detalhes.get('metricas_performance', {})
    estrategia = detalhes.get('analise_eficacia_estrategia', {})
    validacao = detalhes.get('metricas_validacao_hipoteses', {})
    sistema = detalhes.get('sistema_saude', {})
    
    # Gerar relatório Markdown
    relatorio = f"""# 📊 RELATÓRIO EXECUTIVO - PROMETHEUS V2.5
## Sistema de Trading Autônomo - Análise de Performance

**Data do Relatório:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Período Analisado:** {data.get('periodo_analisado', 'N/A')}  
**Versão do Sistema:** Prometheus V2.5

---

## 🎯 RESUMO EXECUTIVO

### Status do Sistema
{obter_status_sistema(resumo.get('status_sistema', 'N/A'))}

### Avaliação de Performance
{obter_avaliacao_performance(resumo.get('avaliacao_performance', 'N/A'))}

### Recomendação de Ação
{obter_recomendacao_acao(resumo.get('recomendacao_acao', 'N/A'))}

---

## 📈 MÉTRICAS DE PERFORMANCE PRINCIPAIS

### Resultados Financeiros

| Métrica | Valor |
|---------|-------|
| **Lucro/Prejuízo Total** | {formatar_valor_monetario(performance.get('resultado_financeiro', {}).get('lucro_prejuizo_total', 0))} |
| **Lucro/Prejuízo Médio por Trade** | {formatar_valor_monetario(performance.get('resultado_financeiro', {}).get('lucro_prejuizo_medio_por_trade', 0))} |
| **Maior Trade Lucro** | {formatar_valor_monetario(performance.get('resultado_financeiro', {}).get('maior_trade_lucro', 0))} |
| **Maior Trade Prejuízo** | {formatar_valor_monetario(performance.get('resultado_financeiro', {}).get('maior_trade_prejuizo', 0))} |
| **Sharpe Ratio** | {performance.get('resultado_financeiro', {}).get('sharpe_ratio', 0):.4f} |
| **Maximum Drawdown** | {formatar_valor_monetario(performance.get('resultado_financeiro', {}).get('maximum_drawdown', 0))} |

### Operações

| Métrica | Valor |
|---------|-------|
| **Total de Ordens Executadas** | {ordens.get('total_ordens_executadas', 0)} |
| **Taxa de Execução de Sucesso** | {formatar_percentual(performance.get('taxa_execucao_sucesso', 0))} |
| **Frequência de Operações** | {performance.get('frequencia_operacoes', 0):.2f} ordens/hora |
| **Posições Abertas Atual** | {performance.get('exposicao_mercado', {}).get('posicoes_abertas_atual', 0)} |
| **Exposição Total ao Mercado** | {formatar_percentual(performance.get('exposicao_mercado', {}).get('exposicao_total_percent', 0))} |

---

## 🎯 VALIDAÇÃO DE HIPÓTESES ESTRATÉGICAS

| Hipótese | Critério | Status | Resultado |
|----------|----------|--------|-----------|
| **H1: Taxa de Execução** | Taxa > 80% | {obter_status_hipotese(validacao.get('H1_taxa_execucao', 'FALHA'))} | {formatar_percentual(performance.get('taxa_execucao_sucesso', 0))} |
| **H2: Lucratividade** | PnL Total ≥ 0 | {obter_status_hipotese(validacao.get('H2_lucratividade', 'FALHA'))} | {formatar_valor_monetario(performance.get('resultado_financeiro', {}).get('lucro_prejuizo_total', 0))} |
| **H3: Consistência** | Frequência > 1.0/hora | {obter_status_hipotese(validacao.get('H3_consistencia', 'FALHA'))} | {performance.get('frequencia_operacoes', 0):.2f} ordens/hora |
| **H4: Risco Controlado** | Exposição ≤ 5% | {obter_status_hipotese(validacao.get('H4_risco_controlado', 'FALHA'))} | {formatar_percentual(performance.get('exposicao_mercado', {}).get('exposicao_total_percent', 0))} |

**Resumo:** {sum(1 for v in validacao.values() if v == 'SUCESSO')} de 4 hipóteses validadas com sucesso.

---

## 📊 ANÁLISE DE EFICÁCIA DA ESTRATÉGIA

### Estratégia MA5/MA20 (Moving Averages)

| Métrica | Valor |
|---------|-------|
| **Total de Sinais BUY Gerados** | {estrategia.get('sinais_gerados_vs_executados', {}).get('total_sinais_BUY_gerados', 0)} |
| **Sinais que Viraram Ordens** | {estrategia.get('sinais_gerados_vs_executados', {}).get('sinais_BUY_que_viraram_ordens', 0)} |
| **Taxa de Conversão Sinal/Ordem** | {formatar_percentual(estrategia.get('sinais_gerados_vs_executados', {}).get('taxa_conversao_sinal_ordem', 0))} |
| **Acertos quando MA Alinhadas** | {estrategia.get('performance_condicoes_entrada', {}).get('acertos_quando_MA5_MA20_alinhadas', 0)} |
| **Erros quando MA Alinhadas** | {estrategia.get('performance_condicoes_entrada', {}).get('erros_quando_MA5_MA20_alinhadas', 0)} |
| **Eficácia da Estratégia MA** | {formatar_percentual(estrategia.get('performance_condicoes_entrada', {}).get('eficacia_estrategia_MA', 0))} |

---

## 🛡️ SAÚDE DO SISTEMA

### Conectividade MT5

| Métrica | Valor |
|---------|-------|
| **Tempo de Uptime** | {sistema.get('conectividade_mt5', {}).get('tempo_uptime', 0):.1f} horas |
| **Reconexões Necessárias** | {sistema.get('conectividade_mt5', {}).get('reconexoes_necessarias', 0)} |
| **Estabilidade de Conexão** | {sistema.get('conectividade_mt5', {}).get('estabilidade_conexao', 'N/A')} |

### Performance Técnica

| Métrica | Valor |
|---------|-------|
| **Tempo de Resposta de Análise** | {sistema.get('performance_tecnica', {}).get('tempo_resposta_analise', 0):.3f} segundos |
| **Taxa de Erros/Exceções** | {formatar_percentual(sistema.get('performance_tecnica', {}).get('taxa_erros_excecoes', 0))} |
| **Estabilidade de Execução** | {sistema.get('performance_tecnica', {}).get('estabilidade_execucao', 'N/A')} |

---

## 💼 ANÁLISE CIENTÍFICA PARA CONSELHO

### ✅ Pontos Fortes

"""
    
    # Adicionar pontos fortes
    pontos_fortes = analise_ceo.get('pontos_fortes', [])
    if pontos_fortes:
        for ponto in pontos_fortes:
            relatorio += f"- {ponto}\n"
    else:
        relatorio += "- Nenhum ponto forte crítico identificado no período analisado.\n"
    
    relatorio += "\n### ⚠️ Pontos Fracos\n\n"
    
    # Adicionar pontos fracos
    pontos_fracos = analise_ceo.get('pontos_fracos', [])
    if pontos_fracos:
        for ponto in pontos_fracos:
            relatorio += f"- {ponto}\n"
    else:
        relatorio += "- Nenhum ponto fraco crítico identificado.\n"
    
    relatorio += "\n### 🚀 Oportunidades de Otimização\n\n"
    
    # Adicionar oportunidades
    oportunidades = analise_ceo.get('oportunidades_otimizacao', [])
    if oportunidades:
        for op in oportunidades:
            relatorio += f"- {op}\n"
    else:
        relatorio += "- Nenhuma oportunidade específica identificada.\n"
    
    relatorio += "\n### ⚠️ Riscos Identificados\n\n"
    
    # Adicionar riscos
    riscos = analise_ceo.get('riscos_identificados', [])
    if riscos:
        for risco in riscos:
            relatorio += f"- {risco}\n"
    else:
        relatorio += "- Nenhum risco crítico identificado.\n"
    
    relatorio += f"""

---

## 📋 TOP 10 SÍMBOLOS POR VOLUME DE OPERAÇÕES

| Posição | Símbolo | Ordens Executadas | Lucro Total |
|---------|---------|-------------------|-------------|
"""
    
    # Ordenar símbolos por volume de operações
    ordens_por_symbol = ordens.get('ordens_por_symbol', {})
    sorted_symbols = sorted(ordens_por_symbol.items(), 
                          key=lambda x: x[1].get('executadas', 0), 
                          reverse=True)[:10]
    
    for i, (symbol, data) in enumerate(sorted_symbols, 1):
        relatorio += f"| {i} | {symbol} | {data.get('executadas', 0)} | {formatar_valor_monetario(data.get('lucro_total', 0))} |\n"
    
    relatorio += f"""

---

## 🎯 CONCLUSÕES E RECOMENDAÇÕES

### Conclusão Principal

"""
    
    # Conclusão baseada no resumo executivo
    if resumo.get('status_sistema') == 'OPERACIONAL':
        relatorio += "O sistema Prometheus V2.5 está **operando dentro dos parâmetros esperados** e todas as hipóteses estratégicas foram validadas com sucesso. O sistema demonstra lucratividade, consistência operacional e controle de risco adequado.\n"
    elif resumo.get('avaliacao_performance') == 'NEGATIVA':
        relatorio += "O sistema Prometheus V2.5 está **apresentando resultados abaixo das expectativas**. A estratégia atual não está gerando lucratividade e requer revisão imediata. Recomenda-se revisar os parâmetros de entrada, filtros de sinal e gestão de risco.\n"
    else:
        relatorio += "O sistema Prometheus V2.5 está **operando com algumas limitações**. Embora apresente consistência operacional, há necessidade de ajustes para melhorar a lucratividade e reduzir a exposição ao risco.\n"
    
    relatorio += f"""
### Recomendações Prioritárias

1. **{resumo.get('recomendacao_acao', 'AJUSTAR')}** - Baseado na análise atual do sistema.

2. **Foco em Otimização:**
   - Revisar filtros de entrada para aumentar taxa de acerto
   - Ajustar gestão de risco para reduzir exposição
   - Melhorar estabilidade de execução

3. **Monitoramento Contínuo:**
   - Acompanhar métricas de validação de hipóteses diariamente
   - Revisar estratégia quando H2 (Lucratividade) falhar
   - Implementar alertas automáticos para riscos críticos

---

## 📎 ANEXOS TÉCNICOS

- **Relatório Técnico Completo:** `{JSON_REPORT_FILE}`
- **Logs de Operação:** `prometheus_telemetry_v2.3.log`
- **Período de Análise:** {data.get('periodo_analisado', 'N/A')}

---

**Relatório Gerado Automaticamente pelo Sistema Prometheus V2.5**  
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Versão do Sistema:** Prometheus V2.5 (Relatório Científico)

---

*Este relatório foi gerado com base em dados reais coletados do sistema de trading autônomo Prometheus. Todas as métricas foram calculadas utilizando metodologia científica validada.*
"""
    
    # Salvar relatório
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f"✅ Relatório executivo gerado com sucesso!")
        print(f"   Arquivo: {OUTPUT_FILE}")
        print()
        print("="*80)
        print("RELATÓRIO EXECUTIVO PARA CONSELHO")
        print("="*80)
        print(relatorio)
        print("="*80)
    except Exception as e:
        print(f"❌ ERRO ao salvar relatório: {e}")

if __name__ == "__main__":
    gerar_relatorio_executivo()

