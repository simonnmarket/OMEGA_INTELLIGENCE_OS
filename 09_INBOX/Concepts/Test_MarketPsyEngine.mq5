//+------------------------------------------------------------------+
//| Test_MarketPsyEngine.mq5                                        |
//| Expert Advisor de Teste para MarketPsyEngine                    |
//| Propósito: Validar compilação do motor de sentimento            |
//+------------------------------------------------------------------+
#property copyright "Prometheus Trading Systems"
#property version   "1.00"
#property strict

// Incluir o motor de sentimento
#include <MarketPsyEngine.mqh>

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("=== TEST MARKETPSYENGINE ===");
    Print("Iniciando teste de compilação do MarketPsyEngine...");
    
    // Criar instância do motor
    MarketPsyEngine_ProductionReady* engine = new MarketPsyEngine_ProductionReady();
    
    if(engine != NULL)
    {
        Print("✓ MarketPsyEngine instanciado com sucesso!");
        Print("✓ Status: ", engine.GetProductionStatus());
        
        delete engine;
        Print("✓ Teste concluído com sucesso!");
        Print("=== COMPILAÇÃO VALIDADA ===");
    }
    else
    {
        Print("✗ ERRO: Falha ao instanciar MarketPsyEngine!");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("Test_MarketPsyEngine finalizado. Motivo: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Não faz nada - apenas teste de compilação
}
//+------------------------------------------------------------------+

