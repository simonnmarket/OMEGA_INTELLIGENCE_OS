# ==============================================================================
# DIRETRIZES OPERACIONAIS E ARQUITETURA AIC V1.1 (Survival Risk)
# Propósito: Estabelecer a arquitetura mínima viável e funcional com Gestão de Risco.
# Data de Publicação: 26/11/2025
# ==============================================================================

# Este módulo armazena as regras e o foco estratégico para o Sistema Operacional V1.1.

DIRETRIZES_PRINCIPAIS = """
## 🎯 FOCO ESTRATÉGICO: EXECUÇÃO ACIMA DE COMPLEXIDADE

1.  **Status Atual:** Sistema Operacional V1.1 (Survival Risk).

2.  **Objetivo Primário:** Proteger o capital adicionando Stop Loss (SL) e Take Profit (TP) à execução.

3.  **Métrica de Sucesso:** Ordem executada com sucesso E com SL/TP válidos (a ser confirmado no log).
"""

REGRAS_ARQUITETURA = """
## ⚙️ REGRAS ARQUITETURA V1.1 (O Esqueleto Protegido)

* **1. MetaTrader 5 (MT5):** Única fonte de dados e execução.

* **2. Conexão:** Deve ser robusta e validada a cada ciclo.

* **3. Análise (Estratégia):** MANTER a estratégia mínima do V1.0.

    * **Indicador:** Apenas Média Móvel (MA) Simples.

    * **Regra:** Tendência de Alta Confirmada (MA Rápida > MA Lenta).

    * **Ação:** Apenas BUY (Compra).

* **4. Gestão de Risco (NOVO):** Lote fixo (0.01). **Implementar SL e TP fixos em pips** na função de envio de ordem.

* **5. Logging:** Apenas `print()` statements simples para confirmar a conexão, o sinal e a execução, incluindo os valores de SL e TP definidos.
"""

COMPONENTES_DESCARTADOS = """
## ❌ COMPONENTES DESATIVADOS (Complexidade V7.0)

Os seguintes componentes continuam removidos para manter o foco na operação mínima:

* **1. Agente de Reforço Adaptativo (AFR/Q-table):** Removido. A inteligência será construída SOBRE dados reais do V1.1.

* **2. Indicadores Múltiplos:** Removidos (ADX, RSI, etc.). Foco apenas no MA Crossover.

* **3. Dados Simulados (np.random):** Estritamente Proibido. Todas as decisões devem vir de `mt5.copy_rates_from_pos()`.

* **4. Camadas de Abstração Desnecessárias:** O fluxo de execução é o mais simples possível.
"""

PLANO_EVOLUCAO = """
## 🚀 PRÓXIMOS PASSOS (Caminho para o V2.0)

A evolução será feita de forma iterativa, aprimorando o sistema V1.1 que agora está com Gestão de Risco:

1.  **V1.1 (Survival Risk):** CONCLUÍDO (Próxima etapa: Implementação no código).

2.  **V1.2 (Monitoramento):** Implementar um mecanismo simples para fechar posições (saída por SL/TP).

3.  **V2.0 (Telemetria):** Reintroduzir um sistema de logging estruturado (JSON), mas de forma *separada* e *não-bloqueante*, para coletar dados de performance REAIS para o AFR (o cérebro V7.0) no futuro.
"""

if __name__ == "__main__":
    print("==================================================")
    print("DIRETRIZES OPERACIONAIS AIC V1.1 (Survival Risk)")
    print("==================================================")
    print("Fase V1.0 CONCLUÍDA. Métrica de Execução Atingida.")
    print(DIRETRIZES_PRINCIPAIS)
    print(REGRAS_ARQUITETURA)
    print(COMPONENTES_DESCARTADOS)
    print(PLANO_EVOLUCAO)
    print("\n--- FIM DAS DIRETRIZES ---")

