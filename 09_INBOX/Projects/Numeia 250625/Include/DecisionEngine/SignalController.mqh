//+------------------------------------------------------------------+
//| SignalController.mqh - Central Estratégica de Decisão            |
//| Projeto: EA Numeia - DecisionEngine                              |
//| Função: Unifica sinais de diversos módulos (ex: SKYINTEL,        |
//| técnicos, volume, price action) para gerar uma decisão ponderada |
//+------------------------------------------------------------------+

#include <Utils/Log.mqh>

// Forward declaration
ENUM_SIGNAL_TYPE EvaluateSkyIntelSignal(string symbol);

// Enum para decisão consolidada
enum STRATEGIC_DECISION
{
   STRATEGIC_IGNORE = 0,
   STRATEGIC_BUY = 1,
   STRATEGIC_SELL = 2
};

// Sinal estratégico genérico
struct StrategicSignal
{
   string source;
   ENUM_SIGNAL_TYPE intelSignal;
   double confidence;
   string persona;
};

namespace SignalController
{
    input double SkyIntelWeight = 0.75; // Peso da inteligência estratégica
    input double OtherSignalsWeight = 0.25;

    // Ponto de entrada da decisão consolidada
    STRATEGIC_DECISION ConsolidatedDecision(string symbol)
    {
        StrategicSignal sIntel = GetSkyIntelSignal(symbol);
        double combinedScore = 0;

        if (sIntel.intelSignal == SIGNAL_SPIKE_LONG)
            combinedScore += 1.0 * SkyIntelWeight;

        else if (sIntel.intelSignal == SIGNAL_SPIKE_SHORT)
            combinedScore -= 1.0 * SkyIntelWeight;

        // [FUTURE] Integração com outros módulos técnicos aqui:
        // combinedScore += TécnicoVolume(symbol) * OtherSignalsWeight;
        // combinedScore += PadrãoCandles(symbol) * OtherSignalsWeight;

        AuditLog("SignalController", symbol,
                 StringFormat("Sinal SKYINTEL: %s | Persona: %s | Score: %.2f",
                              EnumToString(sIntel.intelSignal), sIntel.persona, combinedScore));

        if (combinedScore >= 0.6)
            return STRATEGIC_BUY;
        else if (combinedScore <= -0.6)
            return STRATEGIC_SELL;
        else
            return STRATEGIC_IGNORE;
    }

    // Consulta o SKYINTEL e encapsula em sinal estratégico
    StrategicSignal GetSkyIntelSignal(string symbol)
    {
        ENUM_SIGNAL_TYPE intel = EvaluateSkyIntelSignal(symbol);

        StrategicSignal sig;
        sig.source = "SKYINTEL";
        sig.intelSignal = intel;
        sig.confidence = 0.8;

        // Nome da persona extraído via SkyIntel (simulado)
        sig.persona = "AnonymousWhale";

        return sig;
    }
} 