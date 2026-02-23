# Numeia EA - Expert Advisor Institucional

## Visão Geral

Numeia é uma Expert Advisor (EA) de arquitetura institucional, projetada com princípios de engenharia de sistemas avançados, IA, gerenciamento de risco rigoroso e modularidade. Inspirada em práticas de fundos como Goldman Sachs, DE Shaw e Jane Street, sua operação simula um organismo vivo, com um "cérebro" (Core), "órgãos" (Agentes) e um "sistema imunológico" (Auditoria).

## Estrutura de Diretórios

Numeia/
├── Expert/
│   └── NumeiaEA.mq5                     ← Arquivo principal da EA
├── Core/
│   ├── CoreBrainManager.mqh
│   ├── ExecutionOrchestrator.mqh
│   ├── ModuleRegistry.mqh
│   ├── AuditInterface.mqh
│   └── types.mqh
├── Agents/
│   ├── TradingAgent.mqh
│   ├── RiskAgent.mqh
│   ├── PatternRecognitionAgent.mqh
│   ├── MarketAnalysisAgent.mqh
│   └── PatternModels/
│       ├── PatternBase.mqh
│       ├── PatternRegistry.mqh
│       ├── EngulfingPattern.mqh
│       └── ... (outros padrões)
├── Auditor/
│   ├── AuditManager.mqh
│   └── AuditLogger.mqh
├── Include/
│   ├── ExecutionLogic/
│   │   ├── TradeExecutor.mqh
│   │   ├── PositionManager.mqh
│   │   └── ExecutionLoopController.mqh
│   ├── DecisionEngine/
│   │   └── DecisionRouter.mqh
│   └── Analysis/
│       ├── MarketAnalyzer.mqh
│       ├── VolumeProfile.mqh
│       ├── OrderFlowAnalyzer.mqh
│       ├── WeisWaveAnalyzer.mqh
│       ├── SignalValidator.mqh
│       └── VolumeDecisionEngine.mqh
├── Utils/
│   ├── Log.mqh
│   ├── TimeUtils.mqh
│   ├── PriceUtils.mqh
│   └── IndicatorUtils.mqh
├── Config/
│   ├── GlobalConfig.mqh
│   └── RiskConfig.mqh
└── README.txt

## Componentes-Chave

### 🧠 Core (Orquestração e Gestão)
- `CoreBrainManager`: O cérebro que coordena o comportamento da EA.
- `ExecutionOrchestrator`: Define a ordem e ativação dos módulos.
- `ModuleRegistry`: Registro e ativação dos agentes em tempo real.

### 🤖 Agentes Inteligentes
- `TradingAgent`: Execução de ordens com lógica adaptativa.
- `RiskAgent`: Avaliação de risco em tempo real.
- `PatternRecognitionAgent`: Detecção de padrões gráficos e operacionais.
- `MarketAnalysisAgent`: Análise dinâmica baseada em energia, fluxo, volume e termodinâmica de mercado.

### 📊 Módulos de Análise (Include/Analysis)
- `MarketAnalyzer`: Análise técnica avançada.
- `VolumeProfile`: Análise de perfil de volume.
- `OrderFlowAnalyzer`: Análise de fluxo de ordens.
- `WeisWaveAnalyzer`: Análise de ondas de Weis.
- `SignalValidator`: Validação de sinais.
- `VolumeDecisionEngine`: Motor de decisão baseado em volume.

### ⚙️ Módulos de Execução (Include/ExecutionLogic)
- `TradeExecutor`: Execução inteligente de ordens.
- `PositionManager`: Gerenciamento dinâmico de posições.
- `ExecutionLoopController`: Controlador do loop principal.

### 🧭 Motor de Decisão (Include/DecisionEngine)
- `DecisionRouter`: Roteamento de sinais e decisões.

### 🛡 Auditoria e Compliance
- `AuditManager`: Validação das ações do sistema.
- `AuditLogger`: Logs completos e rastreáveis.

### 🔧 Utilitários
- Funções auxiliares para tempo, preço, logs e indicadores.

### ⚙ Configurações
- `GlobalConfig.mqh`: Configuração geral da EA.
- `RiskConfig.mqh`: Parâmetros e limites de risco adaptativos.

## Observações Importantes
- O `NumeiaEA.mq5` agora se encontra em: `Numeia/Expert/NumeiaEA.mq5`
- Todos os includes usam caminhos relativos corretos (`..\\`).
- Estrutura modular e expansível para novos módulos IA, indicadores ou execução.
- A pasta `Include/` agora concentra os arquivos de execução e análise de mercado.
- Recomendado utilizar MetaEditor para configurar corretamente os paths de include.

## Requisitos
- MetaTrader 5
- MQL5 (build 4150+)
- Conectividade estável com broker ECN/STP
- Ativos testados: EURUSD, GBPUSD, índices, commodities e criptos

## Próximos passos
- Testar integração dos módulos Core e Agents com execução real.
- Habilitar log completo com controle de auditoria.
- Implementar funções preditivas nos módulos de análise.

## Futuras Expansões
- Integração com agentes IA externos (ex: via API Python)
- Visualização em frontend com WebSocket + FastAPI
- Implementação de modelos de causalidade e aprendizado de máquina

## Autor
Equipe Numeia Research 