███████╗███╗   ██╗██╗   ██╗███████╗██╗███████╗ █████╗ 
██╔════╝████╗  ██║██║   ██║██╔════╝██║╚══███╔╝██╔══██╗
█████╗  ██╔██╗ ██║██║   ██║█████╗  ██║  ███╔╝ ███████║
██╔══╝  ██║╚██╗██║██║   ██║██╔══╝  ██║ ███╔╝  ██╔══██║
███████╗██║ ╚████║╚██████╔╝██║     ██║███████╗██║  ██║
╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝

Projeto:           Numeia EA – Expert Advisor Institucional
Plataforma:        MetaTrader 5
Organização:       Sky Lab | AI & Institutional Systems
Última atualização: [Atualizado com estrutura Expert/]

──────────────────────────────────────────────────────────────
📁 Estrutura de Diretórios Atualizada
──────────────────────────────────────────────────────────────
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
│   ├── PositionManager.mqh
│   └── ExecutionLoopController.mqh
├── Auditor/
│   ├── AuditManager.mqh
│   └── AuditLogger.mqh
├── Include/
│   ├── ExecutionLogic/
│   │   └── TradeExecutor.mqh
│   ├── Analysis/
│   │   ├── MarketAnalyzer.mqh
│   │   ├── VolumeProfile.mqh
│   │   ├── OrderFlowAnalyzer.mqh
│   │   ├── WeisWaveAnalyzer.mqh
│   │   ├── SignalValidator.mqh
│   │   └── VolumeDecisionEngine.mqh
├── Utils/
│   ├── Log.mqh
│   ├── TimeUtils.mqh
│   ├── PriceUtils.mqh
│   └── IndicatorUtils.mqh
├── Config/
│   ├── GlobalConfig.mqh
│   └── RiskConfig.mqh
└── README.txt                            ← Este documento

──────────────────────────────────────────────────────────────
📌 Observações Importantes
──────────────────────────────────────────────────────────────
• O `NumeiaEA.mq5` agora se encontra em: `Numeia/Expert/NumeiaEA.mq5`
• Todos os includes usam caminhos relativos corretos (`..\\`).
• Estrutura modular e expansível para novos módulos IA, indicadores ou execução.
• A pasta `Include/` agora concentra os arquivos de execução e análise de mercado.
• Recomendado utilizar MetaEditor para configurar corretamente os paths de include.

──────────────────────────────────────────────────────────────
🧠 Módulo Central (CORE)
──────────────────────────────────────────────────────────────
• CoreBrainManager: controla fluxo de decisão e execução.
• ExecutionOrchestrator: organiza a ordem dos módulos.
• ModuleRegistry: controla os módulos ativos.
• AuditInterface: canal de comunicação com a auditoria.
• types.mqh: definições centrais de tipos e estruturas.

──────────────────────────────────────────────────────────────
📌 Próximos passos:
• Testar integração dos módulos Core e Agents com execução real.
• Habilitar log completo com controle de auditoria.
• Implementar funções preditivas nos módulos de análise.

──────────────────────────────────────────────────────────────

Sky Lab – Transformando Análise Quantitativa em Inteligência Estratégica
