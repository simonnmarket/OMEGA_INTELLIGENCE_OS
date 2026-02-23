//+------------------------------------------------------------------+
//| AgentBase.mqh - Classe base abstrata                              |
//| Define a interface comum para todos os tipos de agentes            |
//+------------------------------------------------------------------+

class AgentBase {
protected:
   string m_name;           // Nome do agente
   double m_confidence;     // Confiança na análise (0.0 a 1.0)

public:
   // Construtor abstrato
   AgentBase(string name) : m_name(name), m_confidence(0.0) {}

   virtual ~AgentBase() {}

   // Método principal – retorna sinal: +1 (compra), -1 (venda), 0 (neutro)
   virtual int Analyze(string symbol) {
      return 0;
   }

   // Retorna nome do agente
   string Name() const { return m_name; }

   // Retorna confiança da análise
   double Confidence() const { return m_confidence; }
};