# ==============================================================================
# SILVER SYSTEM V2.3: SISTEMA OPERACIONAL ESPECIALIZADO EM PRATA (XAG)
# Projeto: SilverGMarket (Independente)
# Foco: Sistema isolado e independente para XAGUSD, XAGAUD, XAGEUR, XAGGBP
# Data: 26/11/2025
# Magic Number: 99992 (isolado de outros sistemas)
# ==============================================================================
import MetaTrader5 as mt5
import time
from datetime import datetime
import numpy as np
import json 
import math
from collections import defaultdict

# ==============================================================================
# CONFIGURAÇÃO ESPECÍFICA PARA PRATA (XAG) - HARDCODED
# ==============================================================================
SILVER_SYMBOLS = [
    "XAGUSD",
    "XAGAUD", 
    "XAGEUR",
    "XAGGBP"
]

# --- CONFIGURAÇÃO CHAVE ---
RISK_CONFIG = {
    'symbols': SILVER_SYMBOLS,  # Apenas símbolos de prata
    'volume': 0.02,  # Aumentado para 0.02 para permitir fechamento de 50% (0.01)
    'magic': 99992,  # Magic Number isolado
    'timeframe': mt5.TIMEFRAME_M15,
    
    # V1.1: Stop Loss em pips (mantido)
    'stop_loss_pips': 20,  # Stop Loss: 20 pips
    
    # --- NOVO: CONFIGURAÇÕES DE SAÍDA ESCALONADA ---
    # 1. TP PARCIAL: Quando o preço atinge esse nível, fecha uma parte do volume.
    'tp_parcial_pips': 40,  # 40 pips (Take Profit parcial)
    'volume_fechar_parcial': 0.01,  # Volume a fechar no TP parcial (50% do volume inicial)
    
    # 2. TP FINAL: O TP final no MT5 para o volume restante.
    'take_profit_pips': 80,  # 80 pips (Take Profit final - usado se o TS falhar)
    
    # 3. Break-Even/Trailing Stop (BE/TS)
    'be_trigger_pips': 15,     # 15 pips (Gatilho para mover SL para entrada)
    'be_margin_points': 10,     # 10 pontos (Margem acima da entrada para BE)
    'ts_distance_pips': 20,    # 20 pips (Distância do trailing stop)
}

# ==============================================================================
# CLASSE SistemaOperacional - O ESQUELETO COM GESTÃO ESCALONADA
# ==============================================================================
class SistemaOperacional:
    def __init__(self, config):
        self.config = config
        self.symbols = config['symbols']
        self.volume_inicial = config['volume']
        self.magic = config['magic']
        self.sl_pips = config.get('stop_loss_pips', 20)
        self.tp_parcial_pips = config.get('tp_parcial_pips', 40)
        self.volume_fechar_parcial = config.get('volume_fechar_parcial', 0.01)
        self.tp_final_pips = config.get('take_profit_pips', 80)
        
        self.be_trigger_pips = config.get('be_trigger_pips', 15)
        self.be_margin_points = config.get('be_margin_points', 10)
        self.ts_distance_pips = config.get('ts_distance_pips', 20)
        
        self.log_file = "silver_telemetry.log"  # Log específico para Silver
        # Rastreia se a ação de fechamento parcial já ocorreu para o ticket
        self.parcial_closed = {} 
        
    def descobrir_ativos_silver(self):
        """
        Valida os símbolos de prata (XAG) configurados.
        Sistema isolado - não descobre outros ativos.
        """
        self.log_estruturado("discovery_start", {
            "message": "SILVER SYSTEM - Validando símbolos de prata",
            "symbols": SILVER_SYMBOLS
        })
        
        symbols_validos = []
        for symbol in SILVER_SYMBOLS:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                if symbol_info.visible and symbol_info.trade_mode > 0:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick and tick.time > 0:
                        symbols_validos.append(symbol)
                    else:
                        print(f"⚠️ {symbol}: Sem dados de tick disponíveis")
                else:
                    print(f"⚠️ {symbol}: Não negociável (visible={symbol_info.visible}, trade_mode={symbol_info.trade_mode})")
            else:
                print(f"⚠️ {symbol}: Símbolo não encontrado no MT5")
        
        self.log_estruturado("discovery_complete", {
            "mode": "SILVER_SYSTEM",
            "total_symbols": len(symbols_validos),
            "requested_symbols": SILVER_SYMBOLS,
            "valid_symbols": symbols_validos
        })
        
        print(f"🥈 SILVER SYSTEM: {len(symbols_validos)} de {len(SILVER_SYMBOLS)} símbolos válidos")
        if symbols_validos:
            print(f"📊 Símbolos de prata: {', '.join(symbols_validos)}")
        
        return symbols_validos
        
    # --- FUNÇÕES BÁSICAS E DE LOGGING ---
    def log_estruturado(self, event_type: str, data: dict, print_to_console=True):
        """Função central de logging estruturado (JSON)."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        log_json = json.dumps(log_entry, ensure_ascii=False)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_json + "\n")
        except Exception as e:
            print(f"❌ ERRO GRAVE ao escrever log: {e}")
        
        if print_to_console:
            print(f"[LOG: {event_type}] {log_json}")
    
    def conectar_mt5(self):
        """Conexão com o MetaTrader 5."""
        self.log_estruturado("system_init", {"message": "Tentando conectar ao MetaTrader 5..."})
        
        if not mt5.initialize():
            self.log_estruturado("error_critical", {
                "message": f"Falha na conexão MT5. Erro: {mt5.last_error()}"
            })
            return False
        
        account_info = mt5.account_info()
        if not account_info:
            mt5.shutdown()
            return False
        
        self.log_estruturado("system_connected", {
            "login": account_info.login,
            "balance": account_info.balance,
            "system": "SILVER_SYSTEM"
        })
        
        return True
    
    def verificar_posicoes_abertas(self, symbol: str) -> list:
        """Verifica e retorna a lista de posições BUY abertas (Magic 99992)."""
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            return [p for p in positions if p.magic == self.magic and p.type == mt5.POSITION_TYPE_BUY]
        return []
    
    def calcular_ma(self, rates, periodo):
        """Calcula a Média Móvel Simples (SMA)."""
        precos_fechamento = rates['close']
        if len(precos_fechamento) < periodo:
            return None
        ma = np.convolve(precos_fechamento, np.ones(periodo), 'valid') / periodo
        return ma[-1]
    
    def analise_simples(self, symbol: str) -> str:
        """Análise MÍNIMA (MA Crossover)."""
        try:
            rates = mt5.copy_rates_from_pos(symbol, self.config['timeframe'], 0, 51)
            if rates is None or len(rates) < 51:
                return "NO_DATA"
            
            ma_rapida = self.calcular_ma(rates, 20)
            ma_lenta = self.calcular_ma(rates, 50)
            
            if ma_rapida is None or ma_lenta is None:
                return "NO_DATA"
            
            if ma_rapida > ma_lenta:
                self.log_estruturado("signal_detected", {
                    "symbol": symbol,
                    "signal": "BUY"
                }, print_to_console=False)
                return "BUY"
            
            self.log_estruturado("signal_clear", {
                "symbol": symbol,
                "signal": "NO_SIGNAL"
            }, print_to_console=False)
            return "NO_SIGNAL"
            
        except Exception as e:
            self.log_estruturado("error_analysis", {"symbol": symbol, "error": str(e)})
            return "ERROR"
    
    def modificar_sl_tp(self, ticket: int, symbol: str, new_sl: float, new_tp: float):
        """Envia uma requisição para modificar o SL e/ou TP de uma ordem."""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": symbol,
            "position": ticket,
            "sl": new_sl,
            "tp": new_tp,
            "magic": self.magic,
            "comment": "SILVER_SYSTEM_MOVE_SL",
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log_estruturado("sl_modified", {
                "ticket": ticket,
                "symbol": symbol,
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
                "mt5_error": mt5.last_error()
            })
            return False
    
    def fechar_posicao_simples(self, posicao_a_fechar, reason="SIGNAL_REVERSAL"):
        """Tenta fechar a posição BUY especificada (total)."""
        symbol = posicao_a_fechar.symbol
        ticket = posicao_a_fechar.ticket
        volume = posicao_a_fechar.volume
        
        tick = mt5.symbol_info_tick(symbol)
        preco_fechamento = tick.bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": preco_fechamento,
            "deviation": 20,
            "magic": self.magic,
            "comment": f"SILVER_SYSTEM_SAIDA_{reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.parcial_closed.pop(ticket, None)
            self.log_estruturado("position_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": reason,
                "entry_price": posicao_a_fechar.price_open,
                "close_price": result.price,
                "pnl": result.profit,
                "volume": volume,
                "final_volume": 0.0
            })
            return True
        else:
            self.log_estruturado("error_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": "REVERSAL_FAILURE",
                "retcode": result.retcode if result else 'N/A'
            })
            return False
    
    def fechar_posicao_parcial(self, pos, volume_to_close, reason="PARTIAL_PROFIT"):
        """Fecha uma parte do volume da posição BUY especificada."""
        symbol = pos.symbol
        ticket = pos.ticket
        
        tick = mt5.symbol_info_tick(symbol)
        preco_fechamento = tick.bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": symbol,
            "volume": volume_to_close,
            "type": mt5.ORDER_TYPE_SELL,
            "price": preco_fechamento,
            "deviation": 20,
            "magic": self.magic,
            "comment": f"SILVER_SYSTEM_SAIDA_{reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            remaining_volume = pos.volume - volume_to_close
            self.parcial_closed[ticket] = True
            self.log_estruturado("position_partially_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": reason,
                "volume_closed": volume_to_close,
                "remaining_volume": remaining_volume,
                "pnl_realized": result.profit,
            })
            return True
        else:
            self.log_estruturado("error_partial_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "retcode": result.retcode if result else 'N/A'
            })
            return False
    
    def calcular_volume_valido(self, symbol: str) -> float:
        """Calcula volume válido respeitando limites do símbolo."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.01
        
        volume_min = symbol_info.volume_min
        volume_max = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        
        volume_desejado = self.volume_inicial
        
        if volume_desejado < volume_min:
            volume_desejado = volume_min
        
        if volume_desejado > volume_max:
            volume_desejado = volume_max
        
        if volume_step > 0:
            volume_desejado = round(volume_desejado / volume_step) * volume_step
        
        volume_desejado = max(volume_min, min(volume_max, volume_desejado))
        
        return volume_desejado
    
    def obter_filling_mode(self, symbol: str) -> int:
        """Detecta o modo de preenchimento correto para o símbolo."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return mt5.ORDER_FILLING_RETURN
        
        filling_mode = symbol_info.filling_mode
        
        SYMBOL_FILLING_FOK = 1
        SYMBOL_FILLING_IOC = 2
        SYMBOL_FILLING_RETURN = 4
        
        if filling_mode & SYMBOL_FILLING_RETURN:
            return mt5.ORDER_FILLING_RETURN
        elif filling_mode & SYMBOL_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        elif filling_mode & SYMBOL_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        else:
            return mt5.ORDER_FILLING_RETURN
    
    def verificar_mercado_aberto(self, symbol: str) -> bool:
        """Verifica se o mercado está aberto para o símbolo."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return False
        
        if symbol_info.trade_mode == 0:
            return False
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None or tick.time == 0:
            return False
        
        import time as time_module
        current_time = time_module.time()
        tick_age = abs(current_time - tick.time)
        if tick_age > 300:
            return False
        
        if tick.ask > 0 and tick.bid > 0:
            spread = tick.ask - tick.bid
            if spread > (tick.bid * 0.01):
                return False
        
        return True
    
    def gerenciar_risco_posicao(self, pos):
        """Lógica central de Break-Even, Trailing Stop e Saída Parcial (V2.3)."""
        symbol_info = mt5.symbol_info(pos.symbol)
        if symbol_info is None:
            return
        
        point = symbol_info.point
        digits = symbol_info.digits
        
        current_tick = mt5.symbol_info_tick(pos.symbol)
        if current_tick is None:
            return
        
        current_price = current_tick.bid
        
        if digits == 3 or digits == 5:
            pip_value = 10 * point
        else:
            pip_value = point
        
        profit_in_price = current_price - pos.price_open
        profit_in_pips = profit_in_price / pip_value
        
        # 1. VERIFICAÇÃO DE FECHAMENTO PARCIAL
        if (profit_in_pips >= self.tp_parcial_pips) and (pos.ticket not in self.parcial_closed):
            if pos.volume >= self.volume_fechar_parcial:
                self.fechar_posicao_parcial(pos, self.volume_fechar_parcial, reason="TP_PARCIAL")
                return
        
        # 2. LÓGICA DE BREAK-EVEN (BE)
        be_price_level = pos.price_open + (self.be_margin_points * point)
        be_price_level = round(be_price_level, digits)
        
        if (profit_in_pips >= self.be_trigger_pips) and (pos.sl < be_price_level):
            if self.modificar_sl_tp(pos.ticket, pos.symbol, be_price_level, pos.tp):
                self.log_estruturado("risk_management", {
                    "symbol": pos.symbol,
                    "ticket": pos.ticket,
                    "action": "BREAK_EVEN_SET",
                    "profit_pips": profit_in_pips,
                    "new_sl": be_price_level
                })
        
        # 3. LÓGICA DE TRAILING STOP (TS)
        if pos.sl >= be_price_level or pos.sl > pos.price_open:
            ts_distance_price = self.ts_distance_pips * pip_value
            new_trailing_sl = current_price - ts_distance_price
            new_trailing_sl = round(new_trailing_sl, digits)
            
            if new_trailing_sl > pos.sl:
                if self.modificar_sl_tp(pos.ticket, pos.symbol, new_trailing_sl, pos.tp):
                    self.log_estruturado("risk_management", {
                        "symbol": pos.symbol,
                        "ticket": pos.ticket,
                        "action": "TRAILING_STOP_MOVE",
                        "profit_pips": profit_in_pips,
                        "new_sl": new_trailing_sl
                    })
    
    def executar_ordem_simples(self, symbol: str):
        """Execução com SL e TP definidos para o V2.3."""
        
        if self.verificar_posicoes_abertas(symbol):
            self.log_estruturado("trade_block", {
                "symbol": symbol,
                "reason": "POSITION_ALREADY_OPEN"
            }, print_to_console=False)
            return False
        
        if not self.verificar_mercado_aberto(symbol):
            self.log_estruturado("trade_block", {
                "symbol": symbol,
                "reason": "MARKET_CLOSED_OR_UNAVAILABLE"
            }, print_to_console=False)
            print(f"[{symbol}] ⏸️ Mercado fechado ou indisponível. Pulando...")
            return False
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            symbol_info = mt5.symbol_info(symbol)
            if tick is None or tick.time == 0 or symbol_info is None:
                self.log_estruturado("error_execution", {
                    "symbol": symbol,
                    "message": "Sem dados de tick/símbolo."
                })
                return False
            
            volume_valido = self.calcular_volume_valido(symbol)
            filling_mode = self.obter_filling_mode(symbol)
            
            preco_entrada = tick.ask 
            point = symbol_info.point
            digits = symbol_info.digits
            
            if digits == 3 or digits == 5:
                pip_value = 10 * point
            else:
                pip_value = point
            
            sl_price = round(preco_entrada - (self.sl_pips * pip_value), digits)
            tp_price = round(preco_entrada + (self.tp_final_pips * pip_value), digits)
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume_valido,
                "type": mt5.ORDER_TYPE_BUY,
                "price": preco_entrada,
                "sl": sl_price, 
                "tp": tp_price, 
                "deviation": 20, 
                "magic": self.magic,
                "comment": "SILVER_SYSTEM_V2.3",
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
                    "tp_final_pips": self.tp_final_pips,
                    "tp_parcial_pips": self.tp_parcial_pips,
                    "volume": round(float(volume_valido), 2),
                    "reason": "MA_CROSSOVER"
                })
                print(f"[{symbol}] ✅ ORDEM SILVER SUCESSO:")
                print(f"   -> Ticket: {result.order} | Preço: {result.price:.{digits}f}")
                print(f"   -> Volume: {volume_valido:.2f} | SL: {sl_price:.{digits}f} ({self.sl_pips} pips)")
                print(f"   -> TP Parcial: {self.tp_parcial_pips} pips | TP Final: {self.tp_final_pips} pips")
                self.parcial_closed[result.order] = False
                return True
            else:
                # Tratamento de REQUOTE (10004) ou erro 10018 (Mercado Fechado)
                if result and (result.retcode == mt5.TRADE_RETCODE_REQUOTE or result.retcode == 10018):
                    if result.retcode == 10018:
                        print(f"[{symbol}] ⏸️ Mercado fechado (10018). Aguardando próximo ciclo...")
                        self.log_estruturado("trade_block", {
                            "symbol": symbol,
                            "reason": "MARKET_CLOSED_10018",
                            "retcode": 10018
                        }, print_to_console=False)
                        return False
                    
                    print(f"[{symbol}] 🔄 REQUOTE: Preço mudou. Requisitando novo preço...")
                    time.sleep(0.5)
                    new_tick = mt5.symbol_info_tick(symbol)
                    if new_tick and new_tick.time > 0:
                        new_price = new_tick.ask
                        new_sl_price = round(new_price - (self.sl_pips * pip_value), digits)
                        new_tp_price = round(new_price + (self.tp_final_pips * pip_value), digits)
                        request["price"] = new_price
                        request["sl"] = new_sl_price
                        request["tp"] = new_tp_price
                        result = mt5.order_send(request)
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            self.log_estruturado("position_opened", {
                                "symbol": symbol,
                                "ticket": result.order,
                                "type": "BUY",
                                "entry_price": round(float(result.price), digits),
                                "sl_price": round(float(new_sl_price), digits),
                                "tp_price": round(float(new_tp_price), digits),
                                "volume": round(float(volume_valido), 2),
                                "reason": "MA_CROSSOVER",
                                "requote": True
                            })
                            print(f"[{symbol}] ✅ ORDEM EXECUTADA (REQUOTE): Ticket: {result.order} | Novo Preço: {result.price:.{digits}f}")
                            self.parcial_closed[result.order] = False
                            return True
                
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
                            self.parcial_closed[result.order] = False
                            return True
                
                error_msg = ""
                if result:
                    if result.retcode == mt5.TRADE_RETCODE_REQUOTE or result.retcode == 10018:
                        error_msg = "Mercado fechado ou indisponível (10018/REQUOTE)"
                    elif result.retcode == mt5.TRADE_RETCODE_MARKET_CLOSED:
                        error_msg = "Mercado fechado"
                    elif result.retcode == mt5.TRADE_RETCODE_NO_MONEY:
                        error_msg = "Fundos insuficientes"
                    else:
                        error_msg = f"Código: {result.retcode} - {result.comment if hasattr(result, 'comment') else 'N/A'}"
                else:
                    error_msg = "Sem resposta do MT5"
                
                self.log_estruturado("error_opening", {
                    "symbol": symbol,
                    "retcode": result.retcode if result else 'N/A',
                    "mt5_error": str(mt5.last_error()),
                    "error_message": error_msg
                })
                print(f"[{symbol}] ❌ FALHA NA ORDEM: {error_msg}")
                return False
                
        except Exception as e:
            self.log_estruturado("error_critical_execution", {"symbol": symbol, "error": str(e)})
            print(f"[{symbol}] ❌ ERRO CRÍTICO NA EXECUÇÃO: {e}")
            return False
    
    def ciclo_operacional(self):
        """Ciclo SIMPLES, ITERATIVO e FUNCIONAL."""
        self.log_estruturado("cycle_start", {
            "version": "SILVER SYSTEM V2.3",
            "timestamp": datetime.now().isoformat()
        }, print_to_console=False)
        
        print(f"\n==================================================")
        print(f"🔄 CICLO INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   SISTEMA: SILVER SYSTEM V2.3 (Prata XAG)")
        print(f"==================================================")
        
        for symbol in self.symbols:
            sinal = self.analise_simples(symbol)
            
            posicoes_abertas = self.verificar_posicoes_abertas(symbol)
            
            if posicoes_abertas:
                for pos in posicoes_abertas:
                    self.gerenciar_risco_posicao(pos)
                    
                    if (sinal == "NO_SIGNAL" or sinal == "ERROR" or sinal == "NO_DATA") and pos.volume > 0:
                        self.log_estruturado("monitoring_action", {
                            "symbol": symbol,
                            "ticket": pos.ticket,
                            "message": "Saída por reversão acionada. Tentando fechar."
                        }, print_to_console=False)
                        print(f"[{symbol}] 🛑 SAÍDA POR REVERSÃO: Posição BUY ativa e sinal perdido. Tentando fechar.")
                        self.fechar_posicao_simples(pos, reason="SIGNAL_REVERSAL_FINAL")
                    elif sinal == "BUY" and pos.volume > 0:
                        self.log_estruturado("monitoring_status", {
                            "symbol": symbol,
                            "status": "POSITION_HELD",
                            "message": f"Posição BUY ativa. Volume: {pos.volume}"
                        }, print_to_console=False)
            
            elif sinal == "BUY":
                self.executar_ordem_simples(symbol)
            
            time.sleep(1)

# --- EXECUÇÃO PRINCIPAL ---
def main():
    sistema = SistemaOperacional(RISK_CONFIG)
    
    if sistema.conectar_mt5():
        simbolos_validos = sistema.descobrir_ativos_silver()
        
        if not simbolos_validos:
            sistema.log_estruturado("system_error", {
                "message": "Nenhum símbolo de prata válido encontrado. Encerrando sistema."
            })
            print("❌ Nenhum símbolo de prata válido encontrado. Encerrando sistema.")
            mt5.shutdown()
            return
        
        sistema.symbols = simbolos_validos
        sistema.config['symbols'] = simbolos_validos
        
        print(f"🥈 SILVER SYSTEM V2.3 INICIADO!")
        print(f"📊 Monitorando {len(sistema.symbols)} símbolos de prata: {', '.join(sistema.symbols)}")
        print(f"🔢 Magic Number: {sistema.magic} (projeto isolado)")
        print(f"⏱️  Timeframe: M15 | Intervalo entre ciclos: 5 minutos")
        print(f"🛡️  Gestão de Risco: SL={sistema.sl_pips} pips | TP Final={sistema.tp_final_pips} pips")
        print(f"💰 Fechamento Parcial: {sistema.tp_parcial_pips} pips (fecha {sistema.volume_fechar_parcial:.2f} lotes)")
        print(f"🔄 Monitoramento: Fechamento automático por reversão de sinal")
        print(f"💰 Break-Even: Ativado em {sistema.be_trigger_pips} pips de lucro")
        print(f"📈 Trailing Stop: {sistema.ts_distance_pips} pips de distância (após BE)")
        print(f"📊 Log de Telemetria: {sistema.log_file}")
        print()
        
        sistema.log_estruturado("system_started", {
            "version": "SILVER SYSTEM V2.3",
            "project": "SilverGMarket",
            "total_symbols": len(sistema.symbols),
            "symbols": sistema.symbols,
            "magic": sistema.magic,
            "volume_inicial": sistema.volume_inicial,
            "volume_fechar_parcial": sistema.volume_fechar_parcial,
            "sl_pips": sistema.sl_pips,
            "tp_parcial_pips": sistema.tp_parcial_pips,
            "tp_final_pips": sistema.tp_final_pips,
            "be_trigger_pips": sistema.be_trigger_pips,
            "be_margin_points": sistema.be_margin_points,
            "ts_distance_pips": sistema.ts_distance_pips,
            "timeframe": "M15"
        })
        
        try:
            while True:
                sistema.ciclo_operacional()
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

