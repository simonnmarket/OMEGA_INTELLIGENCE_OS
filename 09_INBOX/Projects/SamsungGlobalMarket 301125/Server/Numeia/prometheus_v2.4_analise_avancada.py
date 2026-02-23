# ==============================================================================
# PROMETHEUS V2.4: OTIMIZADOR E ANÁLISE AVANÇADA DE PERFORMANCE
# Objetivo: Analisar o arquivo de log JSON (V2.3) para calcular MÉTRICAS AVANÇADAS.
# Data: 26/11/2025
# ==============================================================================

import json
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
import re
import sys
import os

# Tentar importar MetaTrader5 para acesso direto ao histórico
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 não disponível. Análise será baseada apenas em logs JSON.")

# Nome do arquivo de log gerado pelo Prometheus V2.3 (ou a versão mais recente)
LOG_FILE_NAME = "prometheus_telemetry_v2.3.log"

# Taxa de Retorno Livre de Risco (Risk-Free Rate) - Usamos 0.01% para simplificar o Sharpe Ratio
RISK_FREE_RATE = 0.0001 

# Thresholds para classificação do Sharpe Ratio
SHARPE_THRESHOLDS = {
    "EXCELENTE": 1.0,
    "BOM": 0.5
}

# Flag para usar dados MOCK (para demonstração)
# Altere para True para usar dados MOCK mesmo se o arquivo de log existir
USE_MOCK_DATA = False

# ==============================================================================
# DADOS MOCK PARA DEMONSTRAÇÃO
# ==============================================================================

MOCK_LOG_CONTENT = """
{"timestamp":"2025-11-25T01:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1001,"entry_price":1.08500,"volume":0.02}}
{"timestamp":"2025-11-25T01:05:00","event":"risk_management","data":{"ticket":1001,"symbol":"EURUSD","action":"BREAK_EVEN_SET"}}
{"timestamp":"2025-11-25T01:10:00","event":"position_partially_closed","data":{"ticket":1001,"symbol":"EURUSD","pnl_realized":40.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T01:15:00","event":"risk_management","data":{"ticket":1001,"symbol":"EURUSD","action":"TRAILING_STOP_MOVE"}}
{"timestamp":"2025-11-25T01:20:00","event":"position_closed","data":{"ticket":1001,"symbol":"EURUSD","pnl":10.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T02:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1002,"entry_price":1.26500,"volume":0.02}}
{"timestamp":"2025-11-25T02:05:00","event":"position_closed","data":{"ticket":1002,"symbol":"GBPUSD","pnl":-35.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T03:00:00","event":"position_opened","data":{"symbol":"XAUUSD","ticket":1003,"entry_price":2650.00,"volume":0.02}}
{"timestamp":"2025-11-25T03:05:00","event":"position_partially_closed","data":{"ticket":1003,"symbol":"XAUUSD","pnl_realized":20.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T03:10:00","event":"position_closed","data":{"ticket":1003,"symbol":"XAUUSD","pnl":-45.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T04:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1004,"entry_price":1.08600,"volume":0.02}}
{"timestamp":"2025-11-25T04:05:00","event":"risk_management","data":{"ticket":1004,"symbol":"EURUSD","action":"BREAK_EVEN_SET"}}
{"timestamp":"2025-11-25T04:10:00","event":"position_closed","data":{"ticket":1004,"symbol":"EURUSD","pnl":20.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T05:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1005,"entry_price":1.26600,"volume":0.02}}
{"timestamp":"2025-11-25T05:05:00","event":"position_partially_closed","data":{"ticket":1005,"symbol":"GBPUSD","pnl_realized":50.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T05:10:00","event":"position_closed","data":{"ticket":1005,"symbol":"GBPUSD","pnl":30.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T06:00:00","event":"position_opened","data":{"symbol":"USDJPY","ticket":1006,"entry_price":150.00,"volume":0.02}}
{"timestamp":"2025-11-25T06:05:00","event":"position_partially_closed","data":{"ticket":1006,"symbol":"USDJPY","pnl_realized":30.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T06:10:00","event":"position_closed","data":{"ticket":1006,"symbol":"USDJPY","pnl":10.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T07:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1007,"entry_price":1.08700,"volume":0.02}}
{"timestamp":"2025-11-25T07:05:00","event":"position_closed","data":{"ticket":1007,"symbol":"EURUSD","pnl":-30.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T08:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1008,"entry_price":1.26700,"volume":0.02}}
{"timestamp":"2025-11-25T08:05:00","event":"risk_management","data":{"ticket":1008,"symbol":"GBPUSD","action":"BREAK_EVEN_SET"}}
{"timestamp":"2025-11-25T08:10:00","event":"position_closed","data":{"ticket":1008,"symbol":"GBPUSD","pnl":5.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T09:00:00","event":"position_opened","data":{"symbol":"USDJPY","ticket":1009,"entry_price":151.00,"volume":0.02}}
{"timestamp":"2025-11-25T09:05:00","event":"position_partially_closed","data":{"ticket":1009,"symbol":"USDJPY","pnl_realized":45.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T09:10:00","event":"position_closed","data":{"ticket":1009,"symbol":"USDJPY","pnl":20.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T10:00:00","event":"position_opened","data":{"symbol":"XAUUSD","ticket":1010,"entry_price":2651.00,"volume":0.02}}
{"timestamp":"2025-11-25T10:05:00","event":"position_closed","data":{"ticket":1010,"symbol":"XAUUSD","pnl":-50.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T11:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1011,"entry_price":1.08800,"volume":0.02}}
{"timestamp":"2025-11-25T11:05:00","event":"position_partially_closed","data":{"ticket":1011,"symbol":"EURUSD","pnl_realized":50.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T11:10:00","event":"risk_management","data":{"ticket":1011,"symbol":"EURUSD","action":"BREAK_EVEN_SET"}}
{"timestamp":"2025-11-25T11:15:00","event":"position_closed","data":{"ticket":1011,"symbol":"EURUSD","pnl":5.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T12:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1012,"entry_price":1.26800,"volume":0.02}}
{"timestamp":"2025-11-25T12:05:00","event":"position_closed","data":{"ticket":1012,"symbol":"GBPUSD","pnl":-45.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T13:00:00","event":"position_opened","data":{"symbol":"USDJPY","ticket":1013,"entry_price":152.00,"volume":0.02}}
{"timestamp":"2025-11-25T13:05:00","event":"position_closed","data":{"ticket":1013,"symbol":"USDJPY","pnl":30.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T14:00:00","event":"position_opened","data":{"symbol":"XAGUSD","ticket":1014,"entry_price":30.00,"volume":0.02}}
{"timestamp":"2025-11-25T14:05:00","event":"position_partially_closed","data":{"ticket":1014,"symbol":"XAGUSD","pnl_realized":25.25,"volume_closed":0.01}}
{"timestamp":"2025-11-25T14:10:00","event":"position_closed","data":{"ticket":1014,"symbol":"XAGUSD","pnl":25.25,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T15:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1015,"entry_price":1.08900,"volume":0.02}}
{"timestamp":"2025-11-25T15:05:00","event":"position_closed","data":{"ticket":1015,"symbol":"EURUSD","pnl":-30.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T16:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1016,"entry_price":1.26900,"volume":0.02}}
{"timestamp":"2025-11-25T16:05:00","event":"position_closed","data":{"ticket":1016,"symbol":"GBPUSD","pnl":50.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T17:00:00","event":"position_opened","data":{"symbol":"USDJPY","ticket":1017,"entry_price":153.00,"volume":0.02}}
{"timestamp":"2025-11-25T17:05:00","event":"position_partially_closed","data":{"ticket":1017,"symbol":"USDJPY","pnl_realized":15.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T17:10:00","event":"position_closed","data":{"ticket":1017,"symbol":"USDJPY","pnl":-5.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T18:00:00","event":"position_opened","data":{"symbol":"XAUUSD","ticket":1018,"entry_price":2652.00,"volume":0.02}}
{"timestamp":"2025-11-25T18:05:00","event":"position_partially_closed","data":{"ticket":1018,"symbol":"XAUUSD","pnl_realized":20.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T18:10:00","event":"position_closed","data":{"ticket":1018,"symbol":"XAUUSD","pnl":-40.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T19:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1019,"entry_price":1.09000,"volume":0.02}}
{"timestamp":"2025-11-25T19:05:00","event":"position_partially_closed","data":{"ticket":1019,"symbol":"EURUSD","pnl_realized":30.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T19:10:00","event":"position_closed","data":{"ticket":1019,"symbol":"EURUSD","pnl":10.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T20:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1020,"entry_price":1.27000,"volume":0.02}}
{"timestamp":"2025-11-25T20:05:00","event":"position_closed","data":{"ticket":1020,"symbol":"GBPUSD","pnl":40.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T21:00:00","event":"position_opened","data":{"symbol":"USDJPY","ticket":1021,"entry_price":154.00,"volume":0.02}}
{"timestamp":"2025-11-25T21:05:00","event":"position_closed","data":{"ticket":1021,"symbol":"USDJPY","pnl":-20.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T22:00:00","event":"position_opened","data":{"symbol":"XAUUSD","ticket":1022,"entry_price":2653.00,"volume":0.02}}
{"timestamp":"2025-11-25T22:05:00","event":"position_closed","data":{"ticket":1022,"symbol":"XAUUSD","pnl":60.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-25T23:00:00","event":"position_opened","data":{"symbol":"EURUSD","ticket":1023,"entry_price":1.09100,"volume":0.02}}
{"timestamp":"2025-11-25T23:05:00","event":"position_partially_closed","data":{"ticket":1023,"symbol":"EURUSD","pnl_realized":50.00,"volume_closed":0.01}}
{"timestamp":"2025-11-25T23:10:00","event":"position_closed","data":{"ticket":1023,"symbol":"EURUSD","pnl":5.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-26T00:00:00","event":"position_opened","data":{"symbol":"GBPUSD","ticket":1024,"entry_price":1.27100,"volume":0.02}}
{"timestamp":"2025-11-26T00:05:00","event":"position_closed","data":{"ticket":1024,"symbol":"GBPUSD","pnl":40.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
{"timestamp":"2025-11-26T01:00:00","event":"position_opened","data":{"symbol":"XAGUSD","ticket":1025,"entry_price":30.10,"volume":0.02}}
{"timestamp":"2025-11-26T01:05:00","event":"position_partially_closed","data":{"ticket":1025,"symbol":"XAGUSD","pnl_realized":25.25,"volume_closed":0.01}}
{"timestamp":"2025-11-26T01:10:00","event":"position_closed","data":{"ticket":1025,"symbol":"XAGUSD","pnl":5.00,"reason":"SIGNAL_REVERSAL_FINAL"}}
"""

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def formatar_valor_monetario(valor):
    """Formata um valor float para a string monetária ($X,XXX.XX)."""
    if valor is None:
        return "$0.00"
    return f"${valor:,.2f}"

def obter_status_sharpe(sharpe_ratio):
    """Determina o status visual do Sharpe Ratio."""
    if sharpe_ratio is None:
        return "N/A"
    if sharpe_ratio >= SHARPE_THRESHOLDS["EXCELENTE"]:
        return "✅ (Excelente: > 1.0)"
    elif sharpe_ratio >= SHARPE_THRESHOLDS["BOM"]:
        return "⚠️ (Bom: > 0.5)"
    else:
        return "❌ (Baixo: < 0.5)"

# ==============================================================================
# FUNÇÕES DE CÁLCULO
# ==============================================================================

def calcular_drawdown(pnl_history):
    """
    Calcula o Maximum Drawdown (MDD) a partir do histórico de PnL.
    MDD = Maior diferença entre um pico (max_peak) e o valor atual da equity.
    """
    if not pnl_history or len(pnl_history) == 0:
        return 0.0

    pnl_array = np.array(pnl_history, dtype=float)
    equity_curve = np.cumsum(pnl_array)
    max_peak = equity_curve[0]
    max_drawdown = 0.0

    for equity in equity_curve:
        if equity > max_peak:
            max_peak = equity
        drawdown_atual = max_peak - equity
        if drawdown_atual > max_drawdown:
            max_drawdown = drawdown_atual

    return max_drawdown

def calcular_sharpe_ratio(pnl_history, risk_free_rate=RISK_FREE_RATE):
    """
    Calcula o Sharpe Ratio: (Retorno Médio - Taxa Livre de Risco) / Desvio Padrão.
    """
    if not pnl_history or len(pnl_history) < 2:
        return None

    pnl_array = np.array(pnl_history, dtype=float)
    std_dev = np.std(pnl_array, ddof=1)  # Desvio padrão amostral

    if std_dev == 0:
        return None

    avg_return = np.mean(pnl_array)
    sharpe_ratio = (avg_return - risk_free_rate) / std_dev

    return sharpe_ratio

# ==============================================================================
# PROCESSAMENTO DE LOGS
# ==============================================================================

def ler_log_e_extrair_dados(filename_or_content, is_content=False):
    """
    Lê o arquivo JSON Lines ou processa conteúdo fornecido.
    Extrai e estrutura os dados de trades e gestão de risco.
    """
    trades = {}
    risk_metrics = defaultdict(int)
    pnl_history = []
    
    try:
        if is_content:
            lines = filename_or_content.strip().split('\n')
        else:
            with open(filename_or_content, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        for line in lines:
            if not line.strip():
                continue
                
            try:
                # Tenta extrair JSON da linha (pode ter texto antes/depois)
                match = re.search(r'\{.*\}', line)
                if not match:
                    continue
                    
                entry = json.loads(match.group(0))
                
                # Suporta tanto formato do V2.3 (com 'timestamp' e 'data') quanto formato direto
                if 'timestamp' in entry and 'data' in entry:
                    event = entry.get('event')
                    data = entry.get('data', {})
                else:
                    # Formato direto (sem aninhamento)
                    event = entry.get('event')
                    data = entry
                
                ticket = data.get('ticket') or data.get('trade_id')
                symbol = data.get('symbol')

                if event == 'position_opened':
                    if ticket:
                        trades[ticket] = {
                            'symbol': symbol or 'UNKNOWN',
                            'entry_price': data.get('entry_price'),
                            'pnl': 0.0,
                            'closed': False,
                            'is_parcial': False,
                            'parcial_pnl': 0.0,
                            'volume_original': data.get('volume'),
                            'close_reason': 'N/A',
                            'close_price': None
                        }

                elif event == 'position_partially_closed':
                    if ticket in trades:
                        trades[ticket]['is_parcial'] = True
                        parcial_pnl = data.get('pnl_realized', data.get('pnl', 0.0))
                        trades[ticket]['parcial_pnl'] += float(parcial_pnl)
                        pnl_history.append(float(parcial_pnl))
                        risk_metrics['parcial_closed_count'] += 1

                elif event == 'position_closed':
                    if ticket in trades:
                        trades[ticket]['closed'] = True
                        final_pnl = data.get('pnl', data.get('final_pnl', 0.0))
                        total_pnl = trades[ticket]['parcial_pnl'] + float(final_pnl)
                        trades[ticket]['pnl'] = total_pnl
                        trades[ticket]['close_reason'] = data.get('reason', 'UNKNOWN')
                        trades[ticket]['close_price'] = data.get('close_price')
                        
                        if not trades[ticket]['is_parcial']:
                            pnl_history.append(float(total_pnl))
                        else:
                            pnl_history.append(float(final_pnl))
                            
                        if total_pnl > 0:
                            risk_metrics['closed_win'] += 1
                            risk_metrics['closed_win_pnl'] += total_pnl
                        else:
                            risk_metrics['closed_loss'] += 1
                            risk_metrics['closed_loss_pnl'] += abs(total_pnl)
                            
                        reason = data.get('reason', '')
                        if 'REVERSAL' in reason.upper() or 'REVERSAL' in trades[ticket]['close_reason'].upper():
                            risk_metrics['closed_by_reversal'] += 1

                elif event == 'risk_management':
                    action = data.get('action') or data.get('type', '')
                    ticket_risk = data.get('ticket') or data.get('trade_id')
                    
                    if 'BREAK_EVEN' in action.upper() or 'BE_MOVED' in action.upper():
                        risk_metrics['break_even_hit'] += 1
                    elif 'TRAILING_STOP' in action.upper() or 'TS_MOVED' in action.upper():
                        risk_metrics['trailing_stop_moves'] += 1
                        
            except json.JSONDecodeError:
                continue
            except Exception as e:
                continue
                
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de log '{filename_or_content}' não encontrado.")
        print(f"   Execute o Prometheus V2.3 primeiro para gerar dados.")
        return None, None, None
    except Exception as e:
        print(f"❌ ERRO ao processar o log: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

    return trades, risk_metrics, pnl_history

# ==============================================================================
# FUNÇÃO PARA LER HISTÓRICO DIRETO DO MT5
# ==============================================================================

def ler_historico_mt5(magic_number=99991, days_back=7):
    """
    Lê histórico de deals diretamente do MT5 para complementar análise.
    Retorna dados estruturados de trades do Prometheus.
    """
    if not MT5_AVAILABLE:
        return None, None
    
    try:
        if not mt5.initialize():
            return None, None
        
        account_info = mt5.account_info()
        if not account_info:
            mt5.shutdown()
            return None, None
        
        # Buscar deals das últimas N dias
        date_from = datetime.now() - timedelta(days=days_back)
        date_to = datetime.now()
        
        deals = mt5.history_deals_get(date_from, date_to)
        if not deals:
            mt5.shutdown()
            return None, None
        
        # Filtrar apenas deals do Prometheus (Magic Number)
        prometheus_deals = [d for d in deals if getattr(d, 'magic', 0) == magic_number]
        
        if not prometheus_deals:
            mt5.shutdown()
            return None, None
        
        # Estruturar dados de trades do MT5
        mt5_trades = {}
        mt5_pnl_history = []
        
        # Agrupar deals por ticket/posição
        deals_por_ticket = defaultdict(list)
        for deal in prometheus_deals:
            ticket = getattr(deal, 'position_id', getattr(deal, 'ticket', 0))
            deals_por_ticket[ticket].append(deal)
        
        # Processar cada grupo de deals (pode ter fechamento parcial)
        for ticket, deal_list in deals_por_ticket.items():
            # Ordenar por tempo
            deal_list.sort(key=lambda d: getattr(d, 'time', 0))
            
            # Calcular PnL total
            total_pnl = sum(getattr(d, 'profit', 0) for d in deal_list)
            
            # Primeiro deal tem informações do símbolo
            first_deal = deal_list[0]
            symbol = getattr(first_deal, 'symbol', 'UNKNOWN')
            
            # Verificar se houve fechamento parcial (múltiplos deals com mesmo ticket)
            is_parcial = len(deal_list) > 2  # Mais de 2 deals = provavelmente parcial + final
            
            # Separar PnL parcial do final
            parcial_pnl = 0.0
            final_pnl = total_pnl
            
            if is_parcial and len(deal_list) >= 2:
                # Assumir que deals intermediários são parciais
                parcial_pnl = sum(getattr(d, 'profit', 0) for d in deal_list[:-1])
                final_pnl = getattr(deal_list[-1], 'profit', 0)
            
            mt5_trades[ticket] = {
                'symbol': symbol,
                'pnl': total_pnl,
                'closed': True,  # Se está no histórico, foi fechado
                'is_parcial': is_parcial,
                'parcial_pnl': parcial_pnl,
                'close_reason': 'MT5_HISTORY',
                'source': 'MT5_DIRECT'
            }
            
            # Adicionar ao histórico de PnL
            if is_parcial:
                mt5_pnl_history.append(parcial_pnl)
                mt5_pnl_history.append(final_pnl)
            else:
                mt5_pnl_history.append(total_pnl)
        
        mt5.shutdown()
        return mt5_trades, mt5_pnl_history
        
    except Exception as e:
        print(f"⚠️ Erro ao ler histórico do MT5: {e}")
        if MT5_AVAILABLE:
            try:
                mt5.shutdown()
            except:
                pass
        return None, None

# ==============================================================================
# FUNÇÃO PRINCIPAL DE RELATÓRIO
# ==============================================================================

def gerar_relatorio_performance(trades, risk_metrics, pnl_history, mt5_trades=None, mt5_pnl_history=None):
    """
    Calcula as métricas de trading, incluindo Sharpe Ratio, Expectativa e Drawdown.
    Combina dados de logs JSON com histórico direto do MT5 se disponível.
    """
    
    # Combinar trades de logs e MT5
    if mt5_trades:
        # Mesclar trades do MT5 (prioridade para dados do MT5 se houver conflito)
        for ticket, mt5_trade in mt5_trades.items():
            if ticket not in trades:
                trades[ticket] = mt5_trade
            else:
                # Se já existe, usar dados do MT5 se for mais completo
                if mt5_trade.get('closed', False) and not trades[ticket].get('closed', False):
                    trades[ticket].update(mt5_trade)
        
        # Combinar histórico de PnL
        if mt5_pnl_history:
            pnl_history.extend(mt5_pnl_history)
    
    closed_trades = [t for t in trades.values() if t['closed']]

    if not closed_trades:
        print("⚠️ Nenhum trade fechado encontrado para análise.")
        print("   O sistema pode estar rodando, mas ainda não fechou nenhuma posição.")
        print("   Aguarde alguns ciclos e execute a análise novamente.")
        return

    total_trades_closed = len(closed_trades)
    
    # --- 1. Métricas Financeiras ---
    total_pnl = sum(t['pnl'] for t in closed_trades)
    winning_trades = sum(1 for t in closed_trades if t['pnl'] > 0)
    losing_trades = total_trades_closed - winning_trades
    
    gross_profit = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
    gross_loss = sum(abs(t['pnl']) for t in closed_trades if t['pnl'] < 0)
    
    avg_win = gross_profit / winning_trades if winning_trades > 0 else 0
    avg_loss = gross_loss / losing_trades if losing_trades > 0 else 0

    # --- 2. Cálculos de Performance Avançados ---
    win_rate = (winning_trades / total_trades_closed) * 100 if total_trades_closed > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    mdd = calcular_drawdown(pnl_history)
    
    # Expectativa (Average Profit per Trade)
    expectancy = (total_pnl / total_trades_closed) if total_trades_closed > 0 else 0
    
    # Sharpe Ratio
    sharpe_ratio = calcular_sharpe_ratio([t['pnl'] for t in closed_trades])
    
    # Win/Loss Ratio
    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
    
    # --- 3. Análise por Símbolo e Fechamento Parcial ---
    symbol_analysis = defaultdict(lambda: {
        'trades': 0,
        'pnl': 0.0,
        'wins': 0,
        'losses': 0,
        'parcial_closed': 0,
        'avg_pnl': 0.0
    })
    
    for t in closed_trades:
        symbol = t.get('symbol', 'UNKNOWN')
        symbol_analysis[symbol]['trades'] += 1
        symbol_analysis[symbol]['pnl'] += t['pnl']
        if t['pnl'] > 0:
            symbol_analysis[symbol]['wins'] += 1
        else:
            symbol_analysis[symbol]['losses'] += 1
        if t.get('is_parcial', False):
            symbol_analysis[symbol]['parcial_closed'] += 1
    
    # Calcular média de PnL por símbolo
    for symbol in symbol_analysis:
        if symbol_analysis[symbol]['trades'] > 0:
            symbol_analysis[symbol]['avg_pnl'] = symbol_analysis[symbol]['pnl'] / symbol_analysis[symbol]['trades']

    # --- IMPRESSÃO DO RELATÓRIO ---
    
    print("\n" + "="*80)
    print(f"{'PROMETHEUS V2.4: RELATÓRIO DE PERFORMANCE AVANÇADA':^80}")
    print(f"{'Análise de Logs da V2.3 (Escalonada) + Histórico MT5':^80}")
    print("="*80)
    print(f"Data da Análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fontes = []
    if not USE_MOCK_DATA and os.path.exists(LOG_FILE_NAME):
        fontes.append(f"Log JSON: {LOG_FILE_NAME}")
    elif USE_MOCK_DATA:
        fontes.append("Mock Data (Demonstração)")
    
    if mt5_trades:
        fontes.append(f"Histórico MT5: {len(mt5_trades)} trades diretos")
    
    if fontes:
        print(f"Fonte de Dados: {' + '.join(fontes)}")
    else:
        print(f"Fonte de Dados: {LOG_FILE_NAME}")
    
    print("-" * 80)
    
    print(f"{'📊 MÉTRICAS DE PERFORMANCE GERAL':^80}")
    print("-" * 80)
    print(f"Total de Trades Analisados (Fechados): {total_trades_closed}")
    print(f"Lucro/Prejuízo Líquido (PnL):        {formatar_valor_monetario(total_pnl):>40}")
    print(f"Taxa de Acerto (Win Rate):           {win_rate:>6.2f}% ({winning_trades} Ganhos / {losing_trades} Perdas)")
    
    pf_display = f"{profit_factor:,.2f}"
    if profit_factor == float('inf'):
        pf_display = "INF (Sem perdas)"
    print(f"Fator de Lucro (Profit Factor):      {pf_display:>40}")
    
    if gross_profit > 0:
        print(f"Lucro Bruto Total:                  {formatar_valor_monetario(gross_profit):>40}")
    if gross_loss > 0:
        print(f"Prejuízo Bruto Total:               {formatar_valor_monetario(gross_loss):>40}")
    
    print("-" * 80)
    
    print(f"{'⭐ MÉTRICAS AVANÇADAS DE RISCO/RETORNO':^80}")
    print("-" * 80)
    print(f"Expectativa (Avg PnL por Trade):     {formatar_valor_monetario(expectancy):>40}")
    print(f"Maximum Drawdown (MDD):               {formatar_valor_monetario(mdd):>40} (Máxima queda do pico)")
    
    sharpe_display = f"{sharpe_ratio:.4f} {obter_status_sharpe(sharpe_ratio)}" if sharpe_ratio is not None else "N/A"
    print(f"Sharpe Ratio (Risco/Retorno):       {sharpe_display:>40}")
    
    print(f"Lucro Médio por Trade (Avg Win):     {formatar_valor_monetario(avg_win):>40}")
    print(f"Prejuízo Médio por Trade (Avg Loss): {formatar_valor_monetario(avg_loss):>40}")
    
    wl_ratio_display = f"{win_loss_ratio:.2f}"
    if win_loss_ratio == float('inf'):
        wl_ratio_display = "INF (Sem perdas)"
    print(f"Win/Loss Ratio (Avg Win / Avg Loss): {wl_ratio_display:>40}")
    
    print("-" * 80)
    
    print(f"{'🛡️ EFICÁCIA DA GESTÃO DE RISCO (V2.3)':^80}")
    print("-" * 80)
    parcial_count = risk_metrics.get('parcial_closed_count', 0)
    parcial_rate = (parcial_count / total_trades_closed * 100) if total_trades_closed > 0 else 0
    print(f"Trades que Atingiram TP Parcial (50%): {parcial_count} trades ({parcial_rate:>6.2f}%)")
    
    be_hit = risk_metrics.get('break_even_hit', 0)
    be_rate = (be_hit / total_trades_closed * 100) if total_trades_closed > 0 else 0
    print(f"Trades que Atingiram Break-Even (BE): {be_hit} trades ({be_rate:>6.2f}%)")
    
    print(f"Movimentos de Trailing Stop (TS):     {risk_metrics.get('trailing_stop_moves', 0)} movimentos")
    print(f"Fechamentos por Reversão:             {risk_metrics.get('closed_by_reversal', 0)} trades")
    print("-" * 80)

    # Impressão da Análise por Símbolo
    if len(symbol_analysis) > 0:
        print(f"{'📈 ANÁLISE DE PERFORMANCE POR SÍMBOLO':^80}")
        print("-" * 80)
        print(f"{'Símbolo':<12} {'Trades':<8} {'PnL':<15} {'Avg PnL':<15} {'Win Rate':<12} {'W/L':<10} {'TP Parcial':<12}")
        print("-" * 80)
        
        # Ordenar por PnL (maior primeiro)
        sorted_symbols = sorted(symbol_analysis.items(), key=lambda x: x[1]['pnl'], reverse=True)
        
        for symbol, data in sorted_symbols:
            symbol_win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            wl_ratio = f"{data['wins']}/{data['losses']}"
            print(f"{symbol:<12} "
                  f"{data['trades']:<8} "
                  f"{formatar_valor_monetario(data['pnl']):<15} "
                  f"{formatar_valor_monetario(data['avg_pnl']):<15} "
                  f"{symbol_win_rate:>10.2f}% "
                  f"{wl_ratio:<10} "
                  f"{data['parcial_closed']:<12}")
    
    print("="*80 + "\n")

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

def main():
    print("🔍 PROMETHEUS V2.4: Iniciando análise avançada de performance...")
    print("   (Combinando Logs JSON + Histórico Direto do MT5)")
    print()
    
    # 1. Ler dados dos logs JSON
    trades = {}
    risk_metrics = defaultdict(int)
    pnl_history = []
    
    if USE_MOCK_DATA:
        print(f"📂 Usando dados MOCK para demonstração")
        log_content = MOCK_LOG_CONTENT
        trades, risk_metrics, pnl_history = ler_log_e_extrair_dados(log_content, is_content=True)
    else:
        print(f"📂 Procurando arquivo: {LOG_FILE_NAME}")
        if not os.path.exists(LOG_FILE_NAME):
            print(f"⚠️ Arquivo não encontrado. Usando dados MOCK para demonstração...")
            log_content = MOCK_LOG_CONTENT
            trades, risk_metrics, pnl_history = ler_log_e_extrair_dados(log_content, is_content=True)
        else:
            trades, risk_metrics, pnl_history = ler_log_e_extrair_dados(LOG_FILE_NAME, is_content=False)
    
    # 2. Ler histórico direto do MT5 (se disponível)
    mt5_trades = None
    mt5_pnl_history = None
    
    if MT5_AVAILABLE:
        print("📊 Lendo histórico de ordens diretamente do MT5...")
        mt5_trades, mt5_pnl_history = ler_historico_mt5(magic_number=99991, days_back=7)
        if mt5_trades:
            print(f"   ✅ {len(mt5_trades)} trades encontrados no histórico do MT5")
        else:
            print("   ⚠️ Nenhum trade do Prometheus encontrado no histórico do MT5")
    else:
        print("   ⚠️ MetaTrader5 não disponível. Análise baseada apenas em logs JSON.")
    
    print()
    
    if trades is not None and risk_metrics is not None:
        gerar_relatorio_performance(trades, risk_metrics, pnl_history, mt5_trades, mt5_pnl_history)
    else:
        print("\n❌ Não foi possível gerar o relatório. Verifique se o arquivo de log existe.")

if __name__ == "__main__":
    # Verificar se numpy está instalado
    try:
        import numpy as np
    except ImportError:
        print("❌ ERRO: A biblioteca 'numpy' é necessária.")
        print("   Instale-a com: pip install numpy")
        sys.exit(1)
    
    main()
