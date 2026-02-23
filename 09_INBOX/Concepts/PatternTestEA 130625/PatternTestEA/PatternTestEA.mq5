//+------------------------------------------------------------------+
//| PatternTestEA.mq5 - EA de Teste de Padrões                       |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>
#include "Modules\Patterns.mqh"
#include "Modules\AgentInterface.mqh"
#include "Modules\PatternDetector\PatternDetector.mqh"

CTrade trade;  // Objeto para envio de ordens

//+------------------------------------------------------------------+
//| Função principal OnTick                                          |
//+------------------------------------------------------------------+
void OnTick()
{
    PatternInfo pattern;

    // Detectar padrão (usamos a função fictícia DetectSamplePattern)
    if (DetectSamplePattern(pattern))
    {
        string msg = StringFormat("PADRÃO DETECTADO: %s | Preço: %.5f", pattern.name, pattern.entryPrice);
        iaAGENT_SendMessage("TESTE", msg);

        // Verificar se já temos posições abertas
        if (PositionsTotal() == 0)
        {
            double lotSize = 0.1;  // Lote fixo para testes

            // Enviar ordem de COMPRA com base no padrão
            bool ok = trade.Buy(lotSize, _Symbol, pattern.entryPrice, pattern.stopLoss, pattern.takeProfit, "Teste Padrão");
            if (ok)
                iaAGENT_SendMessage("ORDEM", "Ordem enviada com sucesso.");
            else
                iaAGENT_SendMessage("ERRO", "Falha ao enviar ordem: " + trade.ResultRetcodeDescription());
        }
    }
}
