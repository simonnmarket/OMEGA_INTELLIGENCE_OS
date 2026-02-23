# ==============================================================================
# PROMETHEUS V2.1: SISTEMA OPERACIONAL (GESTÃO DE RISCO AVANÇADA)
# Foco: Manter Telemetria (V2.0) + Implementar Break-Even (BE) e Trailing Stop (TS).
# Data: 26/11/2025
# ==============================================================================
import MetaTrader5 as mt5
import time
from datetime import datetime
import numpy as np
import json 
import math  # Para arredondamento de preços

# --- CONFIGURAÇÃO MÍNIMA ---
RISK_CONFIG = {
    'symbols': [],  # Será preenchido automaticamente com todos os símbolos do Market Watch
    'volume': 0.01,  # Lote fixo e mínimo (será ajustado por símbolo)
    'magic': 99991,
    'timeframe': mt5.TIMEFRAME_M15,
    # V1.1: Stop Loss e Take Profit em pips (mantido)
    'stop_loss_pips': 20,  # Stop Loss: 20 pips
    'take_profit_pips': 40,  # Take Profit: 40 pips (1:2 Risk/Reward)
    
    # --- NOVO: CONFIGURAÇÕES DE GESTÃO DE RISCO V2.1 ---
    # Gatilho de Break-Even: Em quantos pips de lucro movemos o SL para o Preço de Entrada (+margem)
    'be_trigger_pips': 15,  # 15 pips (quando lucro atinge 15 pips, move SL para BE)
    # Margem de Break-Even: Quantos pontos acima do preço de entrada o SL deve ficar (para cobrir spread/custos)
    'be_margin_points': 10,  # 10 pontos (1 pip em par de 5 casas)
    # Distância do Trailing Stop: Distância que o SL deve manter do preço atual, após o BE ser atingido
    'ts_distance_pips': 20,  # 20 pips (distância do trailing stop)
}

# ==============================================================================
# CLASSE SistemaOperacional - O ESQUELETO COM GESTÃO DE RISCO
# ==============================================================================
class SistemaOperacional:
    def __init__(self, config):
        self.config = config
        self.symbols = config['symbols']
        self.volume = config['volume']
        self.magic = config['magic']
        self.sl_pips = config.get('stop_loss_pips', 20)
        self.tp_pips = config.get('take_profit_pips', 40)
        
        # Novas Configurações V2.1
        self.be_trigger_pips = config.get('be_trigger_pips', 15)
        self.be_margin_points = config.get('be_margin_points', 10)
        self.ts_distance_pips = config.get('ts_distance_pips', 20)
        
        self.log_file = "prometheus_telemetry_v2.1.log"
        # Dicionário para rastrear o status de Break-Even
        self.be_status = {} 
        
    def descobrir_ativos_market_watch(self):
        """
        Descobre TODOS os símbolos disponíveis no Market Watch do MT5.
        Filtra apenas símbolos negociáveis (visible=True, trade_mode permite trading).
        """
        self.log_estruturado("discovery_start", {"message": "Iniciando descoberta de ativos do Market Watch"})
        
        all_symbols = mt5.symbols_get()
        if all_symbols is None:
            self.log_estruturado("discovery_error", {"message": "Erro ao obter lista de símbolos do MT5"})
            return []
        
        symbols_validos = []
        for symbol_info in all_symbols:
            symbol = symbol_info.name
            
            # Filtros básicos: símbolo deve ser visível e permitir trading
            if symbol_info.visible and symbol_info.trade_mode > 0:
                # Verificar se o símbolo tem dados disponíveis (spread válido)
                tick = mt5.symbol_info_tick(symbol)
                if tick and tick.time > 0:
                    symbols_validos.append(symbol)
        
        self.log_estruturado("discovery_complete", {
            "total_symbols": len(symbols_validos),
            "sample_symbols": symbols_validos[:10]
        })
        
        print(f"✅ {len(symbols_validos)} ativos válidos descobertos no Market Watch.")
        if len(symbols_validos) > 0:
            print(f"📊 Primeiros 10: {', '.join(symbols_validos[:10])}")
            if len(symbols_validos) > 10:
                print(f"   ... e mais {len(symbols_validos) - 10} ativos")
        
        return symbols_validos
        
    def log_estruturado(self, event_type: str, data: dict, print_to_console=True):
        """
        Função central de logging estruturado (JSON) para telemetria.
        (Mantida da V2.0)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        log_json = json.dumps(log_entry, ensure_ascii=False)
        
        # 1. Grava no arquivo de log
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_json + "\n")
        except Exception as e:
            print(f"❌ ERRO GRAVE ao escrever log: {e}")
            
        # 2. Imprime no console (se ativado)
        if print_to_console:
            print(f"[LOG: {event_type}] {log_json}")

    def conectar_mt5(self):
        """Conexão simples e robusta com verificação básica. (Mantida da V2.0)"""
        self.log_estruturado("system_init", {"message": "Tentando conectar ao MetaTrader 5..."})
        if not mt5.initialize():
            self.log_estruturado("error_critical", {"message": f"Falha na conexão MT5. Erro: {mt5.last_error()}"})
            return False
        
        account_info = mt5.account_info()
        if not account_info:
            self.log_estruturado("error_critical", {"message": "Falha ao obter informações da conta."})
            mt5.shutdown()
            return False
            
        self.log_estruturado("system_connected", {
            "login": account_info.login,
            "balance": account_info.balance,
            "equity": account_info.equity
        })
        mt5.set_current_rates_mode(mt5.TERMINAL_TRADE_MODE_REAL) 
        return True
    
    def calcular_ma(self, rates, periodo):
        """Calcula a Média Móvel Simples (SMA) do preço de fechamento. (Mantida da V2.0)"""
        precos_fechamento = rates['close']
        if len(precos_fechamento) < periodo:
            return None 
            
        ma = np.convolve(precos_fechamento, np.ones(periodo), 'valid') / periodo
        # Retorna o último valor
        return ma[-1] 

    def analise_simples(self, symbol: str) -> str:
        """Análise MÍNIMA (MA Crossover). (Mantida da V2.0)"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, self.config['timeframe'], 0, 51)
            
            if rates is None or len(rates) < 51:
                return "NO_DATA"
                
            PERIODO_MA_RAPIDA = 20
            PERIODO_MA_LENTA = 50

            ma_rapida = self.calcular_ma(rates, PERIODO_MA_RAPIDA)
            ma_lenta = self.calcular_ma(rates, PERIODO_MA_LENTA)
            
            if ma_rapida is None or ma_lenta is None:
                return "NO_DATA"

            if ma_rapida > ma_lenta:
                last_close = rates['close'][-1]
                self.log_estruturado("signal_detected", {
                    "symbol": symbol, 
                    "signal": "BUY", 
                    "ma20": round(float(ma_rapida), 5), 
                    "ma50": round(float(ma_lenta), 5),
                    "close_price": round(float(last_close), 5)
                }, print_to_console=False)  # Silenciando no console para não inundar
                return "BUY"
            
            self.log_estruturado("signal_clear", {"symbol": symbol, "signal": "NO_SIGNAL"}, print_to_console=False)
            return "NO_SIGNAL"
                
        except Exception as e:
            self.log_estruturado("error_analysis", {"symbol": symbol, "error": str(e)})
            return "ERROR"
    
    def verificar_posicoes_abertas(self, symbol: str) -> list:
        """Verifica e retorna a lista de posições BUY abertas. (Mantida da V2.0)"""
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            return [p for p in positions if p.magic == self.magic and p.type == mt5.POSITION_TYPE_BUY]
        return []

    def fechar_posicao_simples(self, posicao_a_fechar):
        """Tenta fechar a posição BUY especificada. (Mantida da V2.0)"""
        symbol = posicao_a_fechar.symbol
        ticket = posicao_a_fechar.ticket
        volume = posicao_a_fechar.volume
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            self.log_estruturado("error_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": "NO_TICK_DATA"
            })
            return False
        
        preco_fechamento = tick.bid

        # Obter filling mode correto
        filling_mode = self.obter_filling_mode(symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,  # Ordem inversa (SELL) para fechar uma COMPRA
            "price": preco_fechamento,
            "deviation": 20, 
            "magic": self.magic,
            "comment": "PROMETHEUS_V2_1_SAIDA_REVERSAO",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log_estruturado("position_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": "SIGNAL_REVERSAL",
                "entry_price": round(float(posicao_a_fechar.price_open), 5),
                "close_price": round(float(result.price), 5),
                "pnl": round(float(result.profit), 2), 
                "volume": round(float(volume), 2)
            })
            # Limpar status de BE quando posição é fechada
            if ticket in self.be_status:
                del self.be_status[ticket]
            print(f"[{symbol}] 🛑 SAÍDA SUCESSO: Posição {ticket} fechada por reversão de sinal.")
            print(f"   -> Preço Fechamento: {result.price:.5f} | PnL: {result.profit:.2f}")
            return True
        else:
            self.log_estruturado("error_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": "SIGNAL_REVERSAL_FAILURE",
                "retcode": result.retcode if result else 'N/A',
                "mt5_error": str(mt5.last_error())
            })
            print(f"[{symbol}] ❌ FALHA AO FECHAR POSIÇÃO {ticket}. Retcode: {result.retcode if result else 'N/A'}")
            return False

    def modificar_sl_tp(self, ticket: int, symbol: str, new_sl: float, new_tp: float):
        """
        Envia uma requisição para modificar o SL e/ou TP de uma ordem.
        Usado para Break-Even e Trailing Stop.
        """
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": symbol,
            "position": ticket,
            "sl": new_sl,
            "tp": new_tp,
            "magic": self.magic,
            "comment": "PROMETHEUS_V2_1_MOVE_SL",
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log_estruturado("sl_modified", {
                "ticket": ticket,
                "symbol": symbol,
                "old_sl": request["sl"], 
                "new_sl": new_sl,
                "new_tp": new_tp,
                "message": "Stop Loss modificado com sucesso."
            }, print_to_console=False)
            return True
        else:
            self.log_estruturado("error_sltp_modify", {
                "ticket": ticket,
                "symbol": symbol,
                "new_sl": new_sl,
                "retcode": result.retcode if result else 'N/A',
                "mt5_error": str(mt5.last_error())
            })
            return False

    def gerenciar_risco_posicao(self, pos):
        """
        Lógica central de Break-Even e Trailing Stop (V2.1).
        Aplica a regra de Trailing Stop APÓS a regra de Break-Even.
        """
        symbol_info = mt5.symbol_info(pos.symbol)
        if symbol_info is None:
            return

        point = symbol_info.point
        digits = symbol_info.digits
        
        # Preço atual de mercado (Bid para posição BUY)
        current_tick = mt5.symbol_info_tick(pos.symbol)
        if current_tick is None:
            return
        
        current_price = current_tick.bid
        
        # Calcular lucro em pips
        # Para símbolos com 3 ou 5 digits, 1 pip = 10 * point
        # Para símbolos com 2 ou 4 digits, 1 pip = point
        if digits == 3 or digits == 5:
            pip_value = 10 * point
        else:
            pip_value = point
        
        # Lucro em preço e em pips
        profit_in_price = current_price - pos.price_open
        profit_in_pips = profit_in_price / pip_value
        
        # --- 1. LÓGICA DE BREAK-EVEN (BE) ---
        
        # Calcula o nível de preço para Break-Even (Preço de Entrada + Margem)
        be_price_level = pos.price_open + (self.be_margin_points * point)
        be_price_level = round(be_price_level, digits)
        
        # Se a posição atingiu o gatilho de BE E o SL atual ainda não está em BE
        if (profit_in_pips >= self.be_trigger_pips) and (pos.sl < be_price_level):
            # Mover SL para Break-Even
            if self.modificar_sl_tp(pos.ticket, pos.symbol, be_price_level, pos.tp):
                self.log_estruturado("risk_management", {
                    "symbol": pos.symbol,
                    "ticket": pos.ticket,
                    "action": "BREAK_EVEN_SET",
                    "profit_pips": round(profit_in_pips, 1),
                    "entry_price": round(float(pos.price_open), digits),
                    "new_sl": round(float(be_price_level), digits)
                })
                print(f"[{pos.symbol}] 🛡️ BREAK-EVEN: SL movido para {be_price_level:.{digits}f} (Ticket: {pos.ticket})")
                # Atualiza o status do BE
                self.be_status[pos.ticket] = "BE_SET"
                return  # Sai para evitar Trailing Stop no mesmo ciclo
        
        # --- 2. LÓGICA DE TRAILING STOP (TS) ---
        
        # Esta lógica só se aplica se o SL já está no nível de BE ou superior
        if pos.sl >= be_price_level or pos.sl > pos.price_open:
            # Novo SL ideal para Trailing Stop (Preço Atual - Distância TS)
            ts_distance_price = self.ts_distance_pips * pip_value
            new_trailing_sl = current_price - ts_distance_price
            new_trailing_sl = round(new_trailing_sl, digits)
            
            # O novo SL deve ser sempre MAIOR que o SL atual (apenas move para cima)
            if new_trailing_sl > pos.sl:
                # Mover SL
                if self.modificar_sl_tp(pos.ticket, pos.symbol, new_trailing_sl, pos.tp):
                    self.log_estruturado("risk_management", {
                        "symbol": pos.symbol,
                        "ticket": pos.ticket,
                        "action": "TRAILING_STOP_MOVE",
                        "profit_pips": round(profit_in_pips, 1),
                        "old_sl": round(float(pos.sl), digits),
                        "new_sl": round(float(new_trailing_sl), digits)
                    })
                    print(f"[{pos.symbol}] 📈 TRAILING STOP: SL movido para {new_trailing_sl:.{digits}f} (Ticket: {pos.ticket})")

    def calcular_volume_valido(self, symbol: str) -> float:
        """Calcula o volume válido para o símbolo baseado em suas especificações."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return self.volume  # Fallback
        
        # Obter limites de volume do símbolo
        volume_min = symbol_info.volume_min
        volume_max = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        
        # Volume desejado (0.01)
        volume_desejado = self.volume
        
        # Garantir que o volume seja pelo menos o mínimo
        if volume_desejado < volume_min:
            volume_desejado = volume_min
        
        # Garantir que o volume não exceda o máximo
        if volume_desejado > volume_max:
            volume_desejado = volume_max
        
        # Ajustar para o step (arredondar para o múltiplo mais próximo do step)
        if volume_step > 0:
            volume_desejado = round(volume_desejado / volume_step) * volume_step
        
        # Garantir que ainda está dentro dos limites após o arredondamento
        volume_desejado = max(volume_min, min(volume_max, volume_desejado))
        
        return volume_desejado

    def obter_filling_mode(self, symbol: str) -> int:
        """Detecta o modo de preenchimento correto para o símbolo."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return mt5.ORDER_FILLING_RETURN  # Fallback mais seguro
        
        # Verificar quais modos são suportados (usando valores inteiros)
        filling_mode = symbol_info.filling_mode
        
        # Constantes MT5 (valores inteiros)
        SYMBOL_FILLING_FOK = 1
        SYMBOL_FILLING_IOC = 2
        SYMBOL_FILLING_RETURN = 4
        
        # Prioridade: RETURN > IOC > FOK (RETURN é o mais compatível)
        if filling_mode & SYMBOL_FILLING_RETURN:
            return mt5.ORDER_FILLING_RETURN
        elif filling_mode & SYMBOL_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        elif filling_mode & SYMBOL_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        else:
            return mt5.ORDER_FILLING_RETURN  # Fallback mais seguro

    def executar_ordem_simples(self, symbol: str):
        """
        Execução com SL e TP fixos em pips. 
        (Mantida da V2.0, com melhorias)
        """
        
        if self.verificar_posicoes_abertas(symbol):
            self.log_estruturado("trade_block", {"symbol": symbol, "reason": "POSITION_ALREADY_OPEN"}, print_to_console=False)
            print(f"[{symbol}] 🛑 BLOQUEIO: Posição BUY já aberta pelo Magic Number {self.magic}.")
            return False
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            symbol_info = mt5.symbol_info(symbol)
            if tick is None or tick.time == 0 or symbol_info is None:
                self.log_estruturado("error_execution", {"symbol": symbol, "message": "Sem dados de tick/símbolo."})
                return False

            # Calcular volume válido para o símbolo
            volume_valido = self.calcular_volume_valido(symbol)
            
            # Obter modo de preenchimento correto para o símbolo
            filling_mode = self.obter_filling_mode(symbol)

            preco_entrada = tick.ask 
            point = symbol_info.point
            digits = symbol_info.digits
            
            # Calcular SL e TP em pips
            # Para símbolos com 3 ou 5 digits, 1 pip = 10 * point
            # Para símbolos com 2 ou 4 digits, 1 pip = point
            if digits == 3 or digits == 5:
                pip_value = 10 * point
            else:
                pip_value = point
            
            sl_price = preco_entrada - (self.sl_pips * pip_value)
            tp_price = preco_entrada + (self.tp_pips * pip_value)
            
            # Arredondamento para a precisão do símbolo
            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume_valido,  # Volume ajustado para o símbolo
                "type": mt5.ORDER_TYPE_BUY,
                "price": preco_entrada,
                "sl": sl_price, 
                "tp": tp_price, 
                "deviation": 20, 
                "magic": self.magic,
                "comment": "PROMETHEUS_V2_1_GESTAO_RISCO",  # Comentário atualizado
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.log_estruturado("position_opened", {
                    "symbol": symbol,
                    "ticket": result.order,
                    "type": "BUY",
                    "entry_price": round(float(result.price), digits),
                    "sl_price": round(float(sl_price), digits),
                    "tp_price": round(float(tp_price), digits),
                    "sl_pips": self.sl_pips,
                    "tp_pips": self.tp_pips,
                    "volume": round(float(volume_valido), 2),
                    "reason": "MA_CROSSOVER"
                })
                print(f"[{symbol}] ✅ ORDEM V2.1 SUCESSO:")
                print(f"   -> Ticket: {result.order} | Preço: {result.price:.{digits}f}")
                print(f"   -> SL/TP: SL={sl_price:.{digits}f} ({self.sl_pips} pips) | TP={tp_price:.{digits}f} ({self.tp_pips} pips)")
                return True
            else:
                # Tentar modo alternativo se falhou
                if result and result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                    if filling_mode != mt5.ORDER_FILLING_RETURN:
                        print(f"[{symbol}] 🔄 Tentando modo RETURN como alternativa...")
                        request["type_filling"] = mt5.ORDER_FILLING_RETURN
                        result = mt5.order_send(request)
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            self.log_estruturado("position_opened", {
                                "symbol": symbol,
                                "ticket": result.order,
                                "type": "BUY",
                                "entry_price": round(float(result.price), digits),
                                "sl_price": round(float(sl_price), digits),
                                "tp_price": round(float(tp_price), digits),
                                "volume": round(float(volume_valido), 2),
                                "reason": "MA_CROSSOVER",
                                "retry": True
                            })
                            print(f"[{symbol}] ✅ ORDEM EXECUTADA (RETRY): Ticket: {result.order}")
                            return True
                
                self.log_estruturado("error_opening", {
                    "symbol": symbol,
                    "retcode": result.retcode if result else 'N/A',
                    "mt5_error": str(mt5.last_error())
                })
                print(f"[{symbol}] ❌ FALHA NA ORDEM: Código: {result.retcode if result else 'N/A'}")
                return False
                
        except Exception as e:
            self.log_estruturado("error_critical_execution", {"symbol": symbol, "error": str(e)})
            print(f"[{symbol}] ❌ ERRO CRÍTICO NA EXECUÇÃO: {e}")
            return False

    def ciclo_operacional(self):
        """Ciclo SIMPLES, ITERATIVO e FUNCIONAL com Gestão de Risco."""
        self.log_estruturado("cycle_start", {"version": "V2.1 Gestão de Risco", "timestamp": datetime.now().isoformat()}, print_to_console=False)
        
        print(f"\n==================================================")
        print(f"🔄 CICLO INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   VERSÃO: V2.1 Gestão de Risco (BE + Trailing Stop)")
        print(f"==================================================")
        
        for symbol in self.symbols:
            sinal = self.analise_simples(symbol)
            
            posicoes_abertas = self.verificar_posicoes_abertas(symbol)
            
            # 1. Lógica de Saída (Monitoramento V1.2) e Gestão de Risco (V2.1)
            if posicoes_abertas:
                
                for pos in posicoes_abertas:
                    
                    # a) Gestão de Risco (BE/TS) para posições ativas
                    self.gerenciar_risco_posicao(pos)
                    
                    # b) Saída por Reversão de Sinal (se o sinal sumir)
                    if sinal == "NO_SIGNAL" or sinal == "ERROR" or sinal == "NO_DATA":
                        self.log_estruturado("monitoring_action", {
                            "symbol": symbol,
                            "ticket": pos.ticket,
                            "message": "Saída por reversão acionada. Tentando fechar."
                        }, print_to_console=False)
                        print(f"[{symbol}] 🛑 SAÍDA POR REVERSÃO: Posição BUY ativa e sinal perdido. Tentando fechar.")
                        self.fechar_posicao_simples(pos)
                    else:
                        self.log_estruturado("monitoring_status", {
                            "symbol": symbol,
                            "status": "POSITION_HELD",
                            "message": "Posição BUY ativa. Sinal mantido."
                        }, print_to_console=False)
                    
            # 2. Lógica de Entrada
            elif sinal == "BUY":
                self.executar_ordem_simples(symbol)
            
            # Pausa breve entre os símbolos
            time.sleep(1)

# --- EXECUÇÃO PRINCIPAL ---
def main():
    sistema = SistemaOperacional(RISK_CONFIG)
    
    if sistema.conectar_mt5():
        # Descobrir todos os ativos do Market Watch
        simbolos_descobertos = sistema.descobrir_ativos_market_watch()
        
        if not simbolos_descobertos:
            sistema.log_estruturado("system_error", {"message": "Nenhum ativo válido encontrado. Encerrando sistema."})
            print("❌ Nenhum ativo válido encontrado. Encerrando sistema.")
            mt5.shutdown()
            return
        
        # Atualizar lista de símbolos com os descobertos
        sistema.symbols = simbolos_descobertos
        sistema.config['symbols'] = simbolos_descobertos
        
        print(f"🚀 SISTEMA OPERACIONAL V2.1 (GESTÃO DE RISCO) INICIADO!")
        print(f"📈 Monitorando {len(sistema.symbols)} ativos do Market Watch")
        print(f"⏱️  Timeframe: M15 | Intervalo entre ciclos: 5 minutos")
        print(f"🛡️  Gestão de Risco: SL={sistema.sl_pips} pips | TP={sistema.tp_pips} pips")
        print(f"🔄 Monitoramento: Fechamento automático por reversão de sinal")
        print(f"💰 Break-Even: Ativado em {sistema.be_trigger_pips} pips de lucro")
        print(f"📈 Trailing Stop: {sistema.ts_distance_pips} pips de distância (após BE)")
        print(f"📊 Log de Telemetria: {sistema.log_file}")
        print()
        
        sistema.log_estruturado("system_started", {
            "version": "V2.1 Gestão de Risco",
            "total_symbols": len(sistema.symbols),
            "sl_pips": sistema.sl_pips,
            "tp_pips": sistema.tp_pips,
            "be_trigger_pips": sistema.be_trigger_pips,
            "be_margin_points": sistema.be_margin_points,
            "ts_distance_pips": sistema.ts_distance_pips,
            "timeframe": "M15"
        })
        
        try:
            # Loop principal de execução
            while True:
                sistema.ciclo_operacional()
                # Intervalo de 5 minutos, adequado para o M15
                print(f"⏳ Aguardando 300 segundos para o próximo ciclo...")
                time.sleep(300)
                
        except KeyboardInterrupt:
            sistema.log_estruturado("system_shutdown", {"reason": "Stopped by user (KeyboardInterrupt)"})
            print("\n\n⏹️ Parado pelo usuário (KeyboardInterrupt).")
        except Exception as e:
            sistema.log_estruturado("error_fatal", {"error": str(e)})
            print(f"\n\n🚨 ERRO FATAL NO LOOP PRINCIPAL: {e}")
            import traceback
            traceback.print_exc()
            
    mt5.shutdown()
    print("✅ Conexão MT5 encerrada.")

if __name__ == "__main__":
    main()

