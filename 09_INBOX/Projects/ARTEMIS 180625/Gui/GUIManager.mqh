//+------------------------------------------------------------------+
//| GUIManager.mqh - Interface Gráfica Avançada                      |
//| Sistema de Trading Quântico - Artemis                            |
//+------------------------------------------------------------------+

#ifndef GUIMANAGER_MQH
#define GUIMANAGER_MQH

#include <ChartObjects\ChartObject.mqh>
#include "..\Utils\Logger.mqh"

// Estrutura para métricas
struct GUIMetrics {
   double sharpe;
   double sortino;
   double calmar;
   double drawdown;
   double winRate;
   int totalTrades;
   double totalPnL;
};

class CGUIManager {
private:
   long m_chart_id;
   int m_subwin;
   CLogger* m_logger;
   
   // Painéis
   CChartObjectRectLabel* m_mainPanel;
   CChartObjectRectLabel* m_metricsPanel;
   CChartObjectRectLabel* m_controlPanel;
   
   // Labels
   CChartObjectLabel* m_statusLabel;
   CChartObjectLabel* m_sharpeLabel;
   CChartObjectLabel* m_sortinoLabel;
   CChartObjectLabel* m_calmarLabel;
   CChartObjectLabel* m_drawdownLabel;
   CChartObjectLabel* m_winRateLabel;
   CChartObjectLabel* m_tradesLabel;
   CChartObjectLabel* m_pnlLabel;
   
   // Botões
   CChartObjectButton* m_settingsButton;
   CChartObjectButton* m_backtestButton;
   CChartObjectButton* m_riskButton;
   CChartObjectButton* m_agentsButton;
   CChartObjectButton* m_quantumButton;
   
   // Inputs
   CChartObjectEdit* m_riskInput;
   CChartObjectEdit* m_lotInput;
   
   // Métricas
   GUIMetrics m_metrics;
   
   // Cores
   color m_bgColor;
   color m_textColor;
   color m_buttonColor;
   color m_panelColor;
   
public:
   CGUIManager(CLogger* logger = NULL) {
      m_chart_id = 0;
      m_subwin = 0;
      m_logger = logger;
      
      // Inicializar cores
      m_bgColor = clrNavy;
      m_textColor = clrWhite;
      m_buttonColor = clrDodgerBlue;
      m_panelColor = clrDarkSlateGray;
      
      // Inicializar métricas
      m_metrics.sharpe = 0.0;
      m_metrics.sortino = 0.0;
      m_metrics.calmar = 0.0;
      m_metrics.drawdown = 0.0;
      m_metrics.winRate = 0.0;
      m_metrics.totalTrades = 0;
      m_metrics.totalPnL = 0.0;
   }
   
   ~CGUIManager() {
      DeleteAll();
   }
   
   bool Create() {
      // Criar painéis
      m_mainPanel = new CChartObjectRectLabel();
      m_metricsPanel = new CChartObjectRectLabel();
      m_controlPanel = new CChartObjectRectLabel();
      
      if(!m_mainPanel.Create(m_chart_id, "MainPanel", m_subwin, 10, 10, 200, 300)) return false;
      if(!m_metricsPanel.Create(m_chart_id, "MetricsPanel", m_subwin, 20, 20, 180, 200)) return false;
      if(!m_controlPanel.Create(m_chart_id, "ControlPanel", m_subwin, 20, 230, 180, 70)) return false;
      
      // Criar labels
      m_statusLabel = new CChartObjectLabel();
      m_sharpeLabel = new CChartObjectLabel();
      m_sortinoLabel = new CChartObjectLabel();
      m_calmarLabel = new CChartObjectLabel();
      m_drawdownLabel = new CChartObjectLabel();
      m_winRateLabel = new CChartObjectLabel();
      m_tradesLabel = new CChartObjectLabel();
      m_pnlLabel = new CChartObjectLabel();
      
      if(!CreateLabels()) return false;
      
      // Criar botões
      m_settingsButton = new CChartObjectButton();
      m_backtestButton = new CChartObjectButton();
      m_riskButton = new CChartObjectButton();
      m_agentsButton = new CChartObjectButton();
      m_quantumButton = new CChartObjectButton();
      
      if(!CreateButtons()) return false;
      
      // Criar inputs
      m_riskInput = new CChartObjectEdit();
      m_lotInput = new CChartObjectEdit();
      
      if(!CreateInputs()) return false;
      
      return true;
   }
   
   void Update() {
      UpdateMetrics();
      UpdateLabels();
   }
   
   void SetMetrics(GUIMetrics &metrics) {
      m_metrics = metrics;
   }
   
private:
   bool CreateLabels() {
      if(!m_statusLabel.Create(m_chart_id, "StatusLabel", m_subwin, 30, 30)) return false;
      if(!m_sharpeLabel.Create(m_chart_id, "SharpeLabel", m_subwin, 30, 50)) return false;
      if(!m_sortinoLabel.Create(m_chart_id, "SortinoLabel", m_subwin, 30, 70)) return false;
      if(!m_calmarLabel.Create(m_chart_id, "CalmarLabel", m_subwin, 30, 90)) return false;
      if(!m_drawdownLabel.Create(m_chart_id, "DrawdownLabel", m_subwin, 30, 110)) return false;
      if(!m_winRateLabel.Create(m_chart_id, "WinRateLabel", m_subwin, 30, 130)) return false;
      if(!m_tradesLabel.Create(m_chart_id, "TradesLabel", m_subwin, 30, 150)) return false;
      if(!m_pnlLabel.Create(m_chart_id, "PnLLabel", m_subwin, 30, 170)) return false;
      
      return true;
   }
   
   bool CreateButtons() {
      if(!m_settingsButton.Create(m_chart_id, "SettingsButton", m_subwin, 30, 240, 40, 20)) return false;
      if(!m_backtestButton.Create(m_chart_id, "BacktestButton", m_subwin, 80, 240, 40, 20)) return false;
      if(!m_riskButton.Create(m_chart_id, "RiskButton", m_subwin, 130, 240, 40, 20)) return false;
      if(!m_agentsButton.Create(m_chart_id, "AgentsButton", m_subwin, 30, 270, 40, 20)) return false;
      if(!m_quantumButton.Create(m_chart_id, "QuantumButton", m_subwin, 80, 270, 40, 20)) return false;
      
      return true;
   }
   
   bool CreateInputs() {
      if(!m_riskInput.Create(m_chart_id, "RiskInput", m_subwin, 130, 270, 40, 20)) return false;
      if(!m_lotInput.Create(m_chart_id, "LotInput", m_subwin, 180, 270, 40, 20)) return false;
      
      return true;
   }
   
   void UpdateMetrics() {
      // Atualizar métricas aqui
   }
   
   void UpdateLabels() {
      m_statusLabel.SetText("Status: Running");
      m_sharpeLabel.SetText("Sharpe: " + DoubleToString(m_metrics.sharpe, 2));
      m_sortinoLabel.SetText("Sortino: " + DoubleToString(m_metrics.sortino, 2));
      m_calmarLabel.SetText("Calmar: " + DoubleToString(m_metrics.calmar, 2));
      m_drawdownLabel.SetText("DD: " + DoubleToString(m_metrics.drawdown, 2) + "%");
      m_winRateLabel.SetText("Win Rate: " + DoubleToString(m_metrics.winRate, 2) + "%");
      m_tradesLabel.SetText("Trades: " + IntegerToString(m_metrics.totalTrades));
      m_pnlLabel.SetText("P&L: " + DoubleToString(m_metrics.totalPnL, 2));
   }
   
   void DeleteAll() {
      if(m_mainPanel != NULL) delete m_mainPanel;
      if(m_metricsPanel != NULL) delete m_metricsPanel;
      if(m_controlPanel != NULL) delete m_controlPanel;
      if(m_statusLabel != NULL) delete m_statusLabel;
      if(m_sharpeLabel != NULL) delete m_sharpeLabel;
      if(m_sortinoLabel != NULL) delete m_sortinoLabel;
      if(m_calmarLabel != NULL) delete m_calmarLabel;
      if(m_drawdownLabel != NULL) delete m_drawdownLabel;
      if(m_winRateLabel != NULL) delete m_winRateLabel;
      if(m_tradesLabel != NULL) delete m_tradesLabel;
      if(m_pnlLabel != NULL) delete m_pnlLabel;
      if(m_settingsButton != NULL) delete m_settingsButton;
      if(m_backtestButton != NULL) delete m_backtestButton;
      if(m_riskButton != NULL) delete m_riskButton;
      if(m_agentsButton != NULL) delete m_agentsButton;
      if(m_quantumButton != NULL) delete m_quantumButton;
      if(m_riskInput != NULL) delete m_riskInput;
      if(m_lotInput != NULL) delete m_lotInput;
   }
};

#endif