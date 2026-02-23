# ==============================================================================
# DIRETRIZES OPERACIONAIS E ARQUITETURA AIC V1.0 (MVPO)
# Propósito: Estabelecer a arquitetura mínima viável e funcional.
# Data de Publicação: 26/11/2025
# ==============================================================================
# Este módulo armazena as regras e o foco estratégico para o Sistema Operacional V1.0.

DIRETRIZES_PRINCIPAIS = """
## 🎯 FOCO ESTRATÉGICO: EXECUÇÃO ACIMA DE COMPLEXIDADE

1.  **Status Atual:** Sistema Operacional V1.0 (MVPO - Mínimo Viável Operacional).

2.  **Objetivo Primário:** Garantir a Conexão, Análise Real e Execução.

3.  **Métrica de Sucesso:** Ordem executada e log no terminal.
"""

REGRAS_ARQUITETURA = """
## ⚙️ REGRAS ARQUITETURA V1.0 (O Esqueleto)

* **1. MetaTrader 5 (MT5):** Única fonte de dados e execução.

* **2. Conexão:** Deve ser robusta e validada a cada ciclo.

* **3. Análise (Estratégia):** Deve ser mínima e baseada em DADOS REAIS.

    * **Indicador:** Apenas Média Móvel (MA) Simples.

    * **Regra:** Tendência de Alta Confirmada (MA Rápida > MA Lenta).

    * **Ação:** Apenas BUY (Compra).

* **4. Gestão de Risco:** Mínima. Lote fixo (0.01). Não implementa Stop Loss/Take Profit automáticos no código. (Será implementado no V2.0).

* **5. Logging:** Apenas `print()` statements simples para confirmar a conexão, o sinal e a execução. Logs JSON complexos são DESATIVADOS.
"""

COMPONENTES_DESCARTADOS = """
## ❌ COMPONENTES DESATIVADOS (Complexidade V7.0)

Os seguintes componentes foram removidos do V1.0 para garantir a operação imediata:

* **1. Agente de Reforço Adaptativo (AFR/Q-table):** Removido. A inteligência será construída SOBRE dados reais do V1.0.

* **2. Indicadores Múltiplos:** Removidos (ADX, RSI, etc.). Foco apenas no MA Crossover.

* **3. Dados Simulados (np.random):** Estritamente Proibido. Todas as decisões devem vir de `mt5.copy_rates_from_pos()`.

* **4. Camadas de Abstração Desnecessárias:** O fluxo de execução foi simplificado ao máximo (`ciclo_operacional` -> `analise_simples` -> `executar_ordem_simples`).
"""

PLANO_EVOLUCAO = """
## 🚀 PRÓXIMOS PASSOS (Caminho para o V2.0)

A evolução será feita de forma iterativa, aprimorando o sistema V1.0 que já está OPERANDO.

1.  **V1.1 (Survival Risk):** Adicionar Stop Loss (SL) e Take Profit (TP) fixos em pips na função `executar_ordem_simples`.

2.  **V1.2 (Monitoramento):** Implementar um mecanismo simples para fechar posições (saída por SL/TP).

3.  **V2.0 (Telemetria):** Reintroduzir um sistema de logging estruturado (JSON), mas de forma *separada* e *não-bloqueante*, para coletar dados de performance REAIS para o AFR (o cérebro V7.0) no futuro.
"""

if __name__ == "__main__":
    print("==================================================")
    print("DIRETRIZES OPERACIONAIS AIC V1.0")
    print("==================================================")
    print(DIRETRIZES_PRINCIPAIS)
    print(REGRAS_ARQUITETURA)
    print(COMPONENTES_DESCARTADOS)
    print(PLANO_EVOLUCAO)
    print("\n--- FIM DAS DIRETRIZES ---")

