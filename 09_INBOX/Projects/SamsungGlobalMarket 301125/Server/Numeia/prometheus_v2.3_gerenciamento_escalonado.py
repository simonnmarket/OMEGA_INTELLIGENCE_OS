# ==============================================================================
# PROMETHEUS V2.3: SISTEMA OPERACIONAL (GERENCIAMENTO ESCALONADO)
# Foco: Manter Telemetria (V2.0) + BE/TS (V2.1) + Implementar Trailing Stop Parcial.
# Data: 26/11/2025
# ==============================================================================
import MetaTrader5 as mt5
import time
from datetime import datetime
import numpy as np
import json 
import math
from collections import defaultdict

# Importar configuração de teste (se existir)
try:
    from prometheus_config_test import TEST_MODE, TEST_SYMBOLS
    TEST_CONFIG_LOADED = True
except ImportError:
    # Se o arquivo não existir, usar modo normal
    TEST_MODE = False
    TEST_SYMBOLS = []
    TEST_CONFIG_LOADED = False

# --- CONFIGURAÇÃO CHAVE ---
RISK_CONFIG = {
    'symbols': [],  # Será preenchido automaticamente com todos os símbolos do Market Watch
    'volume': 0.02,  # Aumentado para 0.02 para permitir fechamento de 50% (0.01)
    'magic': 99991,
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
        
        self.log_file = "prometheus_telemetry_v2.3.log"
        # Rastreia se a ação de fechamento parcial já ocorreu para o ticket
        self.parcial_closed = {} 
        
    def descobrir_ativos_market_watch(self):
        """
        Descobre símbolos disponíveis no Market Watch do MT5.
        Se TEST_MODE = True, usa apenas TEST_SYMBOLS.
        Se TEST_MODE = False, descobre TODOS os símbolos negociáveis.
        """
        # Verificar se está em modo teste
        if TEST_CONFIG_LOADED and TEST_MODE:
            self.log_estruturado("discovery_start", {
                "message": "MODO TESTE ATIVO - Usando símbolos específicos",
                "test_symbols": TEST_SYMBOLS
            })
            
            # Validar símbolos de teste
            symbols_validos = []
            for symbol in TEST_SYMBOLS:
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
                "mode": "TEST_MODE",
                "total_symbols": len(symbols_validos),
                "requested_symbols": TEST_SYMBOLS,
                "valid_symbols": symbols_validos
            })
            
            print(f"🧪 MODO TESTE: {len(symbols_validos)} de {len(TEST_SYMBOLS)} símbolos válidos")
            if symbols_validos:
                print(f"📊 Símbolos de teste: {', '.join(symbols_validos)}")
            
            return symbols_validos
        
        # Modo normal: descobrir todos os símbolos
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
            "mode": "NORMAL_MODE",
            "total_symbols": len(symbols_validos),
            "sample_symbols": symbols_validos[:10]
        })
        
        print(f"✅ {len(symbols_validos)} ativos válidos descobertos no Market Watch.")
        if len(symbols_validos) > 0:
            print(f"📊 Primeiros 10: {', '.join(symbols_validos[:10])}")
            if len(symbols_validos) > 10:
                print(f"   ... e mais {len(symbols_validos) - 10} ativos")
        
        return symbols_validos
        
    # --- FUNÇÕES BÁSICAS E DE LOGGING (Mantidas da V2.1) ---
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
            self.log_estruturado("error_critical", {"message": f"Falha na conexão MT5. Erro: {mt5.last_error()}"})
            return False
        
        account_info = mt5.account_info()
        if not account_info:
            mt5.shutdown()
            return False
            
        self.log_estruturado("system_connected", {
            "login": account_info.login,
            "balance": account_info.balance,
            "equity": account_info.equity
        })
        # Nota: set_current_rates_mode não está disponível em todas as versões do MT5
        # O modo de trading é determinado automaticamente pela conta conectada
        return True
    
    def verificar_posicoes_abertas(self, symbol: str) -> list:
        """Verifica e retorna a lista de posições BUY abertas."""
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            return [p for p in positions if p.magic == self.magic and p.type == mt5.POSITION_TYPE_BUY]
        return []

    # Implementações simples (mantidas ou adaptadas)
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
                    "signal": "BUY",
                    "ma20": round(float(ma_rapida), 5),
                    "ma50": round(float(ma_lenta), 5)
                }, print_to_console=False)
                return "BUY"
            
            self.log_estruturado("signal_clear", {"symbol": symbol, "signal": "NO_SIGNAL"}, print_to_console=False)
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
            "comment": "PROMETHEUS_V2_3_MOVE_SL",
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
                "mt5_error": str(mt5.last_error())
            })
            return False

    def fechar_posicao_simples(self, posicao_a_fechar, reason="SIGNAL_REVERSAL"):
        """Tenta fechar a posição BUY especificada (total)."""
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
            "type": mt5.ORDER_TYPE_SELL,
            "price": preco_fechamento,
            "deviation": 20, 
            "magic": self.magic,
            "comment": f"PROMETHEUS_V2_3_SAIDA_{reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            # Remove o rastreamento parcial se a posição total for fechada
            self.parcial_closed.pop(ticket, None) 
            self.log_estruturado("position_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": reason,
                "entry_price": round(float(posicao_a_fechar.price_open), 5),
                "close_price": round(float(result.price), 5),
                "pnl": round(float(result.profit), 2),
                "volume": round(float(volume), 2),
                "final_volume": 0.0
            })
            print(f"[{symbol}] 🛑 SAÍDA TOTAL: Posição {ticket} fechada. PnL: {result.profit:.2f}")
            return True
        else:
            self.log_estruturado("error_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": "REVERSAL_FAILURE",
                "retcode": result.retcode if result else 'N/A',
                "mt5_error": str(mt5.last_error())
            })
            return False

    # --- NOVO: FECHAMENTO PARCIAL ---
    def fechar_posicao_parcial(self, pos, volume_to_close, reason="TP_PARCIAL"):
        """Fecha uma parte do volume da posição BUY especificada."""
        symbol = pos.symbol
        ticket = pos.ticket
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            self.log_estruturado("error_partial_closing", {
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
            "volume": volume_to_close,
            "type": mt5.ORDER_TYPE_SELL,
            "price": preco_fechamento,
            "deviation": 20, 
            "magic": self.magic,
            "comment": f"PROMETHEUS_V2_3_SAIDA_{reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            # Atualizar volume restante (obter posição atualizada)
            updated_pos = mt5.positions_get(ticket=ticket)
            remaining_volume = updated_pos[0].volume if updated_pos else 0.0
            
            self.parcial_closed[ticket] = True  # Marca como parcial fechado
            
            self.log_estruturado("position_partially_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": reason,
                "volume_closed": round(float(volume_to_close), 2),
                "remaining_volume": round(float(remaining_volume), 2),
                "pnl_realized": round(float(result.profit), 2),
                "close_price": round(float(result.price), 5)
            })
            print(f"[{symbol}] 💰 FECHAMENTO PARCIAL: {volume_to_close:.2f} lotes fechados (Ticket: {ticket})")
            print(f"   -> Volume Restante: {remaining_volume:.2f} | PnL Realizado: {result.profit:.2f}")
            return True
        else:
            self.log_estruturado("error_partial_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "retcode": result.retcode if result else 'N/A',
                "mt5_error": str(mt5.last_error())
            })
            print(f"[{symbol}] ❌ FALHA AO FECHAR PARCIAL: Ticket {ticket}")
            return False

    def calcular_volume_valido(self, symbol: str) -> float:
        """Calcula o volume válido para o símbolo baseado em suas especificações."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return self.volume_inicial  # Fallback
        
        # Obter limites de volume do símbolo
        volume_min = symbol_info.volume_min
        volume_max = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        
        # Volume desejado
        volume_desejado = self.volume_inicial
        
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

    # --- NOVO: LÓGICA DE GESTÃO DE RISCO ESCALONADA ---
    def gerenciar_risco_posicao(self, pos):
        """
        Lógica central de Break-Even, Trailing Stop e Saída Parcial (V2.3).
        """
        symbol_info = mt5.symbol_info(pos.symbol)
        if symbol_info is None:
            return

        point = symbol_info.point
        digits = symbol_info.digits
        
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
        
        # 1. VERIFICAÇÃO DE FECHAMENTO PARCIAL (PRIORIDADE ALTA)
        # Se a posição atingiu o TP Parcial E ainda não foi fechada parcialmente
        if (profit_in_pips >= self.tp_parcial_pips) and (pos.ticket not in self.parcial_closed):
            if pos.volume >= self.volume_fechar_parcial:  # Garante que há volume suficiente
                self.fechar_posicao_parcial(pos, self.volume_fechar_parcial, reason="TP_PARCIAL")
                # Após o fechamento parcial, o objeto 'pos' do MT5 é invalidado/atualizado na próxima checagem.
                # Não fazemos BE/TS no mesmo ciclo para evitar confusão de volume/ticket.
                return 

        # 2. LÓGICA DE BREAK-EVEN (BE)
        be_price_level = pos.price_open + (self.be_margin_points * point)
        be_price_level = round(be_price_level, digits)
        
        if (profit_in_pips >= self.be_trigger_pips) and (pos.sl < be_price_level):
            # Move para BE e mantém o TP original/final
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
                # Não retorna, pois o TS pode ser acionado no mesmo ciclo se o preço subir rápido

        # 3. LÓGICA DE TRAILING STOP (TS)
        # Só ativa se o SL for maior ou igual ao preço de BE (ou maior que o preço de entrada)
        if pos.sl >= be_price_level or pos.sl > pos.price_open:
            ts_distance_price = self.ts_distance_pips * pip_value
            new_trailing_sl = current_price - ts_distance_price
            new_trailing_sl = round(new_trailing_sl, digits)
            
            # O novo SL deve ser sempre MAIOR que o SL atual (apenas move para cima)
            if new_trailing_sl > pos.sl:
                # O TP deve ser mantido ou podemos usar o TP_FINAL_PIPS aqui, mas é mais seguro manter o TP da ordem
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

    # --- EXECUÇÃO DE TRADE ---
    def verificar_mercado_aberto(self, symbol: str) -> bool:
        """Verifica se o mercado está aberto para o símbolo."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return False
        
        # Verificar se o símbolo permite trading
        if symbol_info.trade_mode == 0:
            return False
        
        # Verificar horário de trading (se disponível)
        # Muitas corretoras não expõem isso diretamente, então verificamos via tick
        tick = mt5.symbol_info_tick(symbol)
        if tick is None or tick.time == 0:
            return False
        
        # Verificar se o tick é recente (últimos 5 minutos para ser mais tolerante)
        import time as time_module
        current_time = time_module.time()
        tick_age = abs(current_time - tick.time)  # Usar abs para lidar com diferenças de fuso
        if tick_age > 300:  # 5 minutos
            return False
        
        # Verificar se há spread válido (spread muito alto pode indicar mercado fechado)
        if tick.ask > 0 and tick.bid > 0:
            spread = tick.ask - tick.bid
            # Se o spread for muito alto (mais de 1% do preço), pode ser mercado fechado
            if spread > (tick.bid * 0.01):
                return False
        
        return True

    def executar_ordem_simples(self, symbol: str):
        """Execução com SL e TP definidos para o V2.3."""
        
        if self.verificar_posicoes_abertas(symbol):
            self.log_estruturado("trade_block", {
                "symbol": symbol,
                "reason": "POSITION_ALREADY_OPEN"
            }, print_to_console=False)
            return False
        
        # Verificar se mercado está aberto
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

            # Calcular volume válido para o símbolo
            volume_valido = self.calcular_volume_valido(symbol)
            
            # Obter modo de preenchimento correto para o símbolo
            filling_mode = self.obter_filling_mode(symbol)

            preco_entrada = tick.ask 
            point = symbol_info.point
            digits = symbol_info.digits
            
            # Calcular SL e TP em pips
            if digits == 3 or digits == 5:
                pip_value = 10 * point
            else:
                pip_value = point
            
            # SL e TP calculados com base na entrada
            sl_price = round(preco_entrada - (self.sl_pips * pip_value), digits)
            # Usamos o TP FINAL (maior) para definir o TP da ordem, deixando o TP PARCIAL para a lógica do sistema
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
                "comment": "PROMETHEUS_V2_3_ESCALONADO",
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
                print(f"[{symbol}] ✅ ORDEM V2.3 SUCESSO:")
                print(f"   -> Ticket: {result.order} | Preço: {result.price:.{digits}f}")
                print(f"   -> Volume: {volume_valido:.2f} | SL: {sl_price:.{digits}f} ({self.sl_pips} pips)")
                print(f"   -> TP Parcial: {self.tp_parcial_pips} pips | TP Final: {self.tp_final_pips} pips")
                # Inicializa o rastreamento de fechamento parcial
                self.parcial_closed[result.order] = False
                return True
            else:
                # Tratamento de REQUOTE (10004) ou erro 10018 (Mercado Fechado)
                if result and (result.retcode == mt5.TRADE_RETCODE_REQUOTE or result.retcode == 10018):
                    # Erro 10018 geralmente significa mercado fechado
                    if result.retcode == 10018:
                        print(f"[{symbol}] ⏸️ Mercado fechado (10018). Aguardando próximo ciclo...")
                        self.log_estruturado("trade_block", {
                            "symbol": symbol,
                            "reason": "MARKET_CLOSED_10018",
                            "retcode": 10018
                        }, print_to_console=False)
                        return False
                    
                    # Para REQUOTE normal (10004), tentar novamente com novo preço
                    print(f"[{symbol}] 🔄 REQUOTE: Preço mudou. Requisitando novo preço...")
                    time.sleep(0.5)
                    new_tick = mt5.symbol_info_tick(symbol)
                    if new_tick and new_tick.time > 0:
                        new_price = new_tick.ask
                        # Recalcular SL/TP com novo preço
                        new_sl_price = round(new_price - (self.sl_pips * pip_value), digits)
                        new_tp_price = round(new_price + (self.tp_final_pips * pip_value), digits)
                        # Atualizar request com novo preço
                        request["price"] = new_price
                        request["sl"] = new_sl_price
                        request["tp"] = new_tp_price
                        # Tentar novamente
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
                        else:
                            print(f"[{symbol}] ⚠️ Falha após requote. Código: {result.retcode if result else 'N/A'}")
                
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
                            self.parcial_closed[result.order] = False
                            return True
                
                # Log do erro com mensagens específicas
                error_msg = ""
                if result:
                    if result.retcode == mt5.TRADE_RETCODE_REQUOTE or result.retcode == 10018:
                        error_msg = "Mercado fechado ou indisponível (10018/REQUOTE)"
                    elif result.retcode == mt5.TRADE_RETCODE_MARKET_CLOSED:
                        error_msg = "Mercado fechado"
                    elif result.retcode == mt5.TRADE_RETCODE_NO_MONEY:
                        error_msg = "Fundos insuficientes"
                    elif result.retcode == mt5.TRADE_RETCODE_INVALID_VOLUME:
                        error_msg = "Volume inválido"
                    elif result.retcode == mt5.TRADE_RETCODE_INVALID_PRICE:
                        error_msg = "Preço inválido"
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

    # --- CICLO PRINCIPAL ---
    def ciclo_operacional(self):
        """Ciclo SIMPLES, ITERATIVO e FUNCIONAL."""
        self.log_estruturado("cycle_start", {
            "version": "V2.3 Gerenciamento Escalonado",
            "timestamp": datetime.now().isoformat()
        }, print_to_console=False)
        
        print(f"\n==================================================")
        print(f"🔄 CICLO INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   VERSÃO: V2.3 Gerenciamento Escalonado (TP Parcial + BE + TS)")
        print(f"==================================================")
        
        for symbol in self.symbols:
            sinal = self.analise_simples(symbol)
            
            # Importante: verifica as posições ATUALIZADAS
            posicoes_abertas = self.verificar_posicoes_abertas(symbol)
            
            # 1. Lógica de Saída (Monitoramento V1.2) e Gestão de Risco (V2.3)
            if posicoes_abertas:
                
                for pos in posicoes_abertas:
                    
                    # a) Gestão de Risco (TP Parcial, BE/TS)
                    # Observação: Isso pode alterar o volume de 'pos' ou o SL/TP
                    self.gerenciar_risco_posicao(pos)
                    
                    # b) Saída por Reversão de Sinal (só fecha totalmente se houver volume)
                    if (sinal == "NO_SIGNAL" or sinal == "ERROR" or sinal == "NO_DATA") and pos.volume > 0:
                        self.log_estruturado("monitoring_action", {
                            "symbol": symbol,
                            "ticket": pos.ticket,
                            "message": "Saída por reversão acionada. Tentando fechar."
                        }, print_to_console=False)
                        print(f"[{symbol}] 🛑 SAÍDA POR REVERSÃO: Posição BUY ativa e sinal perdido. Tentando fechar.")
                        # O volume de 'pos' pode ter diminuído após o TP parcial
                        self.fechar_posicao_simples(pos, reason="SIGNAL_REVERSAL_FINAL")
                    elif sinal == "BUY" and pos.volume > 0:
                        self.log_estruturado("monitoring_status", {
                            "symbol": symbol,
                            "status": "POSITION_HELD",
                            "message": f"Posição BUY ativa. Volume: {pos.volume}"
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
            sistema.log_estruturado("system_error", {
                "message": "Nenhum ativo válido encontrado. Encerrando sistema."
            })
            print("❌ Nenhum ativo válido encontrado. Encerrando sistema.")
            mt5.shutdown()
            return
        
        # Atualizar lista de símbolos com os descobertos
        sistema.symbols = simbolos_descobertos
        sistema.config['symbols'] = simbolos_descobertos
        
        print(f"🚀 SISTEMA OPERACIONAL V2.3 (GERENCIAMENTO ESCALONADO) INICIADO!")
        
        # Mostrar modo atual (Teste ou Normal)
        if TEST_CONFIG_LOADED and TEST_MODE:
            print(f"🧪 MODO TESTE ATIVO: Monitorando apenas {len(sistema.symbols)} símbolos de teste")
            print(f"📊 Símbolos: {', '.join(sistema.symbols)}")
        else:
            print(f"📈 MODO NORMAL: Monitorando {len(sistema.symbols)} ativos do Market Watch")
        print(f"⏱️  Timeframe: M15 | Intervalo entre ciclos: 5 minutos")
        print(f"🛡️  Gestão de Risco: SL={sistema.sl_pips} pips | TP Final={sistema.tp_final_pips} pips")
        print(f"💰 Fechamento Parcial: {sistema.tp_parcial_pips} pips (fecha {sistema.volume_fechar_parcial:.2f} lotes)")
        print(f"🔄 Monitoramento: Fechamento automático por reversão de sinal")
        print(f"💰 Break-Even: Ativado em {sistema.be_trigger_pips} pips de lucro")
        print(f"📈 Trailing Stop: {sistema.ts_distance_pips} pips de distância (após BE)")
        print(f"📊 Log de Telemetria: {sistema.log_file}")
        print()
        
        sistema.log_estruturado("system_started", {
            "version": "V2.3 Gerenciamento Escalonado",
            "total_symbols": len(sistema.symbols),
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

