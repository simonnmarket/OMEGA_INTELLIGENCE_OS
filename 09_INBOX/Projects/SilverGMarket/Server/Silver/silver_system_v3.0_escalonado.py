# ==============================================================================
# SILVER SYSTEM V3.0: SISTEMA ESCALONADO COM MÚLTIPLAS ENTRADAS
# Projeto: SilverGMarket (Independente)
# Foco: Operações escalonadas para tendências de 500-1600 pontos
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
# CONFIGURAÇÃO ESPECÍFICA PARA PRATA (XAG) - ESCALONADA
# ==============================================================================
SILVER_SYMBOLS = [
    "XAGUSD",
    "XAGAUD", 
    "XAGEUR",
    "XAGGBP"
]

# --- CONFIGURAÇÃO ESCALONADA V3.0 ---
RISK_CONFIG = {
    'symbols': SILVER_SYMBOLS,
    'magic': 99992,
    'timeframe': mt5.TIMEFRAME_M1,  # M1 para mais entradas
    
    # ESCALONAMENTO DE VOLUME
    'volume_min': 0.10,      # Volume mínimo por ordem
    'volume_max': 50.00,     # Volume máximo por ordem
    'volume_inicial': 0.10,  # Primeira entrada
    'volume_step': 0.10,     # Incremento por nova entrada
    
    # GESTÃO DE RISCO PARA VALIDAÇÃO DA ESTRATÉGIA (SL menor = teste rápido)
    'stop_loss_pips': 30,         # SL: 30 pips (valida estratégia sem mascarar)
    'take_profit_pips': 60,       # TP: 60 pips (2:1 risk/reward)
    'take_profit_parcial_1': 20,  # TP Parcial 1: 20 pips (fecha 25%)
    'take_profit_parcial_2': 35,  # TP Parcial 2: 35 pips (fecha 25%)
    'take_profit_parcial_3': 50,  # TP Parcial 3: 50 pips (fecha 25%)
    
    # Break-Even/Trailing Stop (mais rápido para validação)
    'be_trigger_pips': 20,        # BE: 20 pips de lucro (mais rápido)
    'be_margin_points': 5,        # Margem acima da entrada (5 pontos)
    'ts_distance_pips': 15,      # TS: 15 pips de distância (mais apertado)
    
    # ESCALONAMENTO DE ENTRADAS (múltiplas entradas para validar estratégia)
    'max_posicoes_por_symbol': 999,  # Sem limite (999 = ilimitado)
    'distancia_entre_entradas_pips': 20,  # Distância mínima entre entradas (20 pips)
    'intervalo_entre_entradas_segundos': 30,  # Intervalo mínimo entre ordens
    
    # FILTROS DE SEGURANÇA (NOVO - Evitar saldo negativo na largada)
    'spread_max_pips': 50,        # Spread máximo aceitável (50 pips)
    'spread_max_percent': 0.5,    # Spread máximo em % do preço (0.5%)
    'atr_period': 14,             # Período para cálculo ATR (volatilidade)
    'atr_min_multiplier': 0.3,    # ATR mínimo (30% do spread) - mercado muito calmo
    'atr_max_multiplier': 3.0,    # ATR máximo (300% do spread) - mercado muito volátil
    'max_loss_before_block': -50.0,  # Bloquear novas entradas se PnL total < -50
    'min_distance_from_ma_pips': 5,  # Distância mínima da MA20 para entrada (5 pips)
    'max_distance_from_ma_pips': 100, # Distância máxima da MA20 para entrada (100 pips)
    'avoid_trading_hours': [(22, 0), (0, 1)],  # Evitar trading 22:00-01:00 (baixa liquidez)
}

# ==============================================================================
# CLASSE SistemaOperacional - ESCALONADO COM MÚLTIPLAS ENTRADAS
# ==============================================================================
class SistemaOperacional:
    def __init__(self, config):
        self.config = config
        self.symbols = config['symbols']
        self.magic = config['magic']
        self.timeframe = config['timeframe']
        
        # Volumes
        self.volume_min = config.get('volume_min', 0.10)
        self.volume_max = config.get('volume_max', 50.00)
        self.volume_inicial = config.get('volume_inicial', 0.10)
        self.volume_step = config.get('volume_step', 0.10)
        
        # SL/TP
        self.sl_pips = config.get('stop_loss_pips', 100)
        self.tp_pips = config.get('take_profit_pips', 800)
        self.tp_parcial_1 = config.get('take_profit_parcial_1', 200)
        self.tp_parcial_2 = config.get('take_profit_parcial_2', 400)
        self.tp_parcial_3 = config.get('take_profit_parcial_3', 600)
        
        # BE/TS
        self.be_trigger_pips = config.get('be_trigger_pips', 150)
        self.be_margin_points = config.get('be_margin_points', 20)
        self.ts_distance_pips = config.get('ts_distance_pips', 50)
        
        # Escalonamento
        self.max_posicoes = config.get('max_posicoes_por_symbol', 999)
        self.distancia_entradas = config.get('distancia_entre_entradas_pips', 50)
        self.intervalo_entradas = config.get('intervalo_entre_entradas_segundos', 30)
        
        # Filtros de segurança
        self.spread_max_pips = config.get('spread_max_pips', 50)
        self.spread_max_percent = config.get('spread_max_percent', 0.5)
        self.atr_period = config.get('atr_period', 14)
        self.atr_min_multiplier = config.get('atr_min_multiplier', 0.3)
        self.atr_max_multiplier = config.get('atr_max_multiplier', 3.0)
        self.max_loss_before_block = config.get('max_loss_before_block', -50.0)
        self.min_distance_from_ma_pips = config.get('min_distance_from_ma_pips', 5)
        self.max_distance_from_ma_pips = config.get('max_distance_from_ma_pips', 100)
        self.avoid_trading_hours = config.get('avoid_trading_hours', [(22, 0), (0, 1)])
        
        self.log_file = "silver_telemetry_v3.0.log"
        
        # Rastreamento de entradas escalonadas
        self.entradas_por_symbol = defaultdict(list)  # Lista de preços de entrada por símbolo
        self.ultima_entrada_timestamp = defaultdict(float)  # Timestamp da última entrada
        self.parcial_closed = {}  # Rastreamento de fechamentos parciais
        
    def descobrir_ativos_silver(self):
        """Valida os símbolos de prata (XAG) configurados."""
        self.log_estruturado("discovery_start", {
            "message": "SILVER SYSTEM V3.0 - Validando símbolos de prata",
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
                    print(f"⚠️ {symbol}: Não negociável")
            else:
                print(f"⚠️ {symbol}: Símbolo não encontrado no MT5")
        
        self.log_estruturado("discovery_complete", {
            "mode": "SILVER_SYSTEM_V3.0_ESCALONADO",
            "total_symbols": len(symbols_validos),
            "valid_symbols": symbols_validos
        })
        
        print(f"🥈 SILVER SYSTEM V3.0: {len(symbols_validos)} símbolos válidos")
        if symbols_validos:
            print(f"📊 Símbolos: {', '.join(symbols_validos)}")
        
        return symbols_validos
        
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
            print(f"❌ ERRO ao escrever log: {e}")
        
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
            "system": "SILVER_SYSTEM_V3.0_ESCALONADO"
        })
        
        return True
    
    def verificar_posicoes_abertas(self, symbol: str) -> list:
        """Retorna TODAS as posições BUY abertas (sem limite)."""
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
    
    def calcular_atr(self, rates, periodo=14):
        """Calcula o Average True Range (ATR) para medir volatilidade."""
        if len(rates) < periodo + 1:
            return None
        
        true_ranges = []
        for i in range(1, len(rates)):
            high = rates['high'][i]
            low = rates['low'][i]
            prev_close = rates['close'][i-1]
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        if len(true_ranges) < periodo:
            return None
        
        atr = np.mean(true_ranges[-periodo:])
        return atr
    
    def calcular_pnl_total(self, symbol: str = None) -> float:
        """Calcula o PnL total de todas as posições abertas (do sistema)."""
        if symbol:
            positions = self.verificar_posicoes_abertas(symbol)
        else:
            # Todas as posições do sistema
            all_positions = mt5.positions_get()
            if all_positions:
                positions = [p for p in all_positions if p.magic == self.magic]
            else:
                positions = []
        
        pnl_total = 0.0
        for pos in positions:
            pnl_total += pos.profit
        
        return pnl_total
    
    def verificar_horario_trading(self) -> bool:
        """Verifica se está em horário adequado para trading."""
        from datetime import datetime
        now = datetime.now()
        current_hour = now.hour
        
        for start_hour, end_hour in self.avoid_trading_hours:
            if start_hour > end_hour:  # Ex: 22:00 - 01:00 (cruza meia-noite)
                if current_hour >= start_hour or current_hour < end_hour:
                    return False
            else:  # Ex: 10:00 - 11:00 (normal)
                if start_hour <= current_hour < end_hour:
                    return False
        
        return True
    
    def validar_condicoes_mercado(self, symbol: str) -> tuple[bool, str]:
        """
        Valida TODAS as condições de mercado antes de abrir posição.
        Retorna (pode_operar, motivo_bloqueio)
        """
        # 1. VERIFICAR PnL TOTAL (BLOQUEIO CRÍTICO)
        pnl_total = self.calcular_pnl_total()
        if pnl_total < self.max_loss_before_block:
            return False, f"PnL_TOTAL_NEGATIVO: {pnl_total:.2f} < {self.max_loss_before_block:.2f}"
        
        # 1.5. VERIFICAR SE ÚLTIMAS 3 OPERAÇÕES FORAM PERDEDORAS (NOVO)
        # Se últimas 3 operações do símbolo foram perdedoras, bloquear
        deals = mt5.history_deals_get(0, datetime.now().timestamp())
        if deals:
            symbol_deals = [d for d in deals if d.symbol == symbol and d.magic == self.magic and d.entry == mt5.DEAL_ENTRY_OUT]
            if len(symbol_deals) >= 3:
                ultimas_3 = symbol_deals[-3:]
                todas_perdedoras = all([d.profit < 0 for d in ultimas_3])
                if todas_perdedoras:
                    return False, f"ULTIMAS_3_PERDEDORAS: {len(ultimas_3)} operações consecutivas em perda"
        
        # 2. VERIFICAR HORÁRIO
        if not self.verificar_horario_trading():
            return False, "HORARIO_INADEQUADO: Evitando horários de baixa liquidez"
        
        # 3. VERIFICAR SPREAD
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False, "SEM_TICK_DATA"
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return False, "SYMBOL_INFO_NULL"
        
        spread = tick.ask - tick.bid
        point = symbol_info.point
        digits = symbol_info.digits
        
        if digits == 3 or digits == 5:
            pip_value = 10 * point
        else:
            pip_value = point
        
        spread_pips = spread / pip_value
        spread_percent = (spread / tick.bid) * 100
        
        # Verificar spread absoluto
        if spread_pips > self.spread_max_pips:
            return False, f"SPREAD_ALTO_PIPS: {spread_pips:.1f} > {self.spread_max_pips}"
        
        # Verificar spread percentual
        if spread_percent > self.spread_max_percent:
            return False, f"SPREAD_ALTO_PERCENT: {spread_percent:.2f}% > {self.spread_max_percent}%"
        
        # 4. VERIFICAR VOLATILIDADE (ATR)
        rates_h1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, self.atr_period + 10)
        if rates_h1 is None or len(rates_h1) < self.atr_period + 1:
            return False, "SEM_DADOS_ATR"
        
        atr = self.calcular_atr(rates_h1, self.atr_period)
        if atr is None:
            return False, "ATR_CALCULO_FALHOU"
        
        # Verificar se mercado está muito calmo (ATR muito baixo)
        if atr < (spread * self.atr_min_multiplier):
            return False, f"MERCADO_MUITO_CALMO: ATR {atr:.5f} < {spread * self.atr_min_multiplier:.5f}"
        
        # Verificar se mercado está muito volátil (ATR muito alto)
        if atr > (spread * self.atr_max_multiplier):
            return False, f"MERCADO_MUITO_VOLATIL: ATR {atr:.5f} > {spread * self.atr_max_multiplier:.5f}"
        
        # 5. VERIFICAR DISTÂNCIA DA MA20 (entrada muito prematura ou muito tardia)
        rates_m1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 21)
        if rates_m1 is None or len(rates_m1) < 21:
            return False, "SEM_DADOS_M1"
        
        ma20_m1 = self.calcular_ma(rates_m1, 20)
        if ma20_m1 is None:
            return False, "MA20_CALCULO_FALHOU"
        
        current_price = tick.ask
        distance_from_ma = abs(current_price - ma20_m1) / pip_value
        
        # Verificar se está muito perto da MA (entrada prematura)
        if distance_from_ma < self.min_distance_from_ma_pips:
            return False, f"MUITO_PERTO_MA20: {distance_from_ma:.1f} pips < {self.min_distance_from_ma_pips}"
        
        # Verificar se está muito longe da MA (entrada tardia)
        if distance_from_ma > self.max_distance_from_ma_pips:
            return False, f"MUITO_LONGE_MA20: {distance_from_ma:.1f} pips > {self.max_distance_from_ma_pips}"
        
        # 5.5. VERIFICAR MOMENTUM (NOVO - Evitar entradas no topo)
        # Se últimas 3 velas M1 estão em queda, não entrar
        if len(rates_m1) >= 3:
            ultimas_3_velas = rates_m1[-3:]
            velas_em_queda = sum([1 for v in ultimas_3_velas if v['close'] < v['open']])
            if velas_em_queda >= 2:  # 2 de 3 velas em queda
                return False, f"MOMENTUM_NEGATIVO: {velas_em_queda}/3 velas em queda"
        
        # 5.6. VERIFICAR SE PREÇO ESTÁ SUBINDO (NOVO)
        # Preço atual deve estar acima da vela anterior
        if len(rates_m1) >= 2:
            vela_anterior = rates_m1[-2]
            if current_price < vela_anterior['close']:
                return False, "PRECO_CAINDO: Preço atual abaixo da vela anterior"
        
        # 6. VERIFICAR SE HÁ POSIÇÕES EM NEGATIVO NO SÍMBOLO
        posicoes_abertas = self.verificar_posicoes_abertas(symbol)
        if posicoes_abertas:
            pnl_symbol = sum([p.profit for p in posicoes_abertas])
            if pnl_symbol < -20.0:  # Se já está -20 negativo no símbolo, não abre mais
                return False, f"POSICOES_NEGATIVAS_SYMBOL: PnL {pnl_symbol:.2f} < -20.0"
        
        # 6.5. VERIFICAR TEMPO MÍNIMO ENTRE ENTRADAS (NOVO)
        # Não entrar se última entrada foi há menos de 5 minutos
        if symbol in self.ultima_entrada_timestamp:
            tempo_decorrido = time.time() - self.ultima_entrada_timestamp[symbol]
            if tempo_decorrido < 300:  # 5 minutos mínimo
                return False, f"INTERVALO_MUITO_CURTO: {int(tempo_decorrido)}s < 300s (5 min)"
        
        # TODAS AS VALIDAÇÕES PASSARAM
        return True, "OK"
    
    def analise_multi_timeframe(self, symbol: str) -> str:
        """
        Análise MULTI-TIMEFRAME: D1 + H4 + H1
        Todos devem confirmar BUY para executar no M1.
        Isso reduz entradas prematuras e melhora qualidade dos sinais.
        """
        try:
            # 1. ANÁLISE DIÁRIA (D1) - Tendência de longo prazo
            rates_d1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 51)
            if rates_d1 is None or len(rates_d1) < 51:
                return "NO_DATA"
            
            ma20_d1 = self.calcular_ma(rates_d1, 20)
            ma50_d1 = self.calcular_ma(rates_d1, 50)
            
            if ma20_d1 is None or ma50_d1 is None:
                return "NO_DATA"
            
            sinal_d1 = "BUY" if ma20_d1 > ma50_d1 else "NO_SIGNAL"
            
            # 2. ANÁLISE 4 HORAS (H4) - Tendência de médio prazo
            rates_h4 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 51)
            if rates_h4 is None or len(rates_h4) < 51:
                return "NO_DATA"
            
            ma20_h4 = self.calcular_ma(rates_h4, 20)
            ma50_h4 = self.calcular_ma(rates_h4, 50)
            
            if ma20_h4 is None or ma50_h4 is None:
                return "NO_DATA"
            
            sinal_h4 = "BUY" if ma20_h4 > ma50_h4 else "NO_SIGNAL"
            
            # 3. ANÁLISE 1 HORA (H1) - Tendência de curto prazo
            rates_h1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 51)
            if rates_h1 is None or len(rates_h1) < 51:
                return "NO_DATA"
            
            ma20_h1 = self.calcular_ma(rates_h1, 20)
            ma50_h1 = self.calcular_ma(rates_h1, 50)
            
            if ma20_h1 is None or ma50_h1 is None:
                return "NO_DATA"
            
            sinal_h1 = "BUY" if ma20_h1 > ma50_h1 else "NO_SIGNAL"
            
            # 4. CONFIRMAÇÃO: Todos os timeframes devem estar em BUY
            if sinal_d1 == "BUY" and sinal_h4 == "BUY" and sinal_h1 == "BUY":
                self.log_estruturado("signal_detected_multi", {
                    "symbol": symbol,
                    "signal": "BUY",
                    "timeframes": {
                        "D1": {"ma20": round(float(ma20_d1), 5), "ma50": round(float(ma50_d1), 5), "signal": sinal_d1},
                        "H4": {"ma20": round(float(ma20_h4), 5), "ma50": round(float(ma50_h4), 5), "signal": sinal_h4},
                        "H1": {"ma20": round(float(ma20_h1), 5), "ma50": round(float(ma50_h1), 5), "signal": sinal_h1}
                    },
                    "confirmation": "ALL_TIMEFRAMES_BUY"
                }, print_to_console=False)
                return "BUY"
            else:
                # Log detalhado quando não há confirmação
                self.log_estruturado("signal_clear_multi", {
                    "symbol": symbol,
                    "signal": "NO_SIGNAL",
                    "timeframes": {
                        "D1": {"ma20": round(float(ma20_d1), 5), "ma50": round(float(ma50_d1), 5), "signal": sinal_d1},
                        "H4": {"ma20": round(float(ma20_h4), 5), "ma50": round(float(ma50_h4), 5), "signal": sinal_h4},
                        "H1": {"ma20": round(float(ma20_h1), 5), "ma50": round(float(ma50_h1), 5), "signal": sinal_h1}
                    },
                    "reason": f"D1:{sinal_d1} H4:{sinal_h4} H1:{sinal_h1} - Não há confirmação de todos"
                }, print_to_console=False)
                return "NO_SIGNAL"
            
        except Exception as e:
            self.log_estruturado("error_analysis", {"symbol": symbol, "error": str(e)})
            return "ERROR"
    
    def calcular_volume_escalonado(self, symbol: str, num_entradas: int) -> float:
        """Calcula volume escalonado baseado no número de entradas."""
        # Volume aumenta progressivamente: 0.10, 0.20, 0.30, etc.
        volume_calculado = self.volume_inicial + (num_entradas * self.volume_step)
        
        # Respeitar limites do símbolo
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            volume_min_symbol = symbol_info.volume_min
            volume_max_symbol = symbol_info.volume_max
            volume_step_symbol = symbol_info.volume_step
            
            # Aplicar limites
            volume_calculado = max(volume_min_symbol, min(volume_max_symbol, volume_calculado))
            
            # Ajustar para step do símbolo
            if volume_step_symbol > 0:
                volume_calculado = round(volume_calculado / volume_step_symbol) * volume_step_symbol
            
            # Garantir que não excede nossos limites configurados
            volume_calculado = max(self.volume_min, min(self.volume_max, volume_calculado))
        else:
            volume_calculado = max(self.volume_min, min(self.volume_max, volume_calculado))
        
        return round(volume_calculado, 2)
    
    def pode_abrir_nova_entrada(self, symbol: str, current_price: float) -> bool:
        """Verifica se pode abrir nova entrada escalonada."""
        # Verificar limite de posições
        posicoes_abertas = self.verificar_posicoes_abertas(symbol)
        if len(posicoes_abertas) >= self.max_posicoes:
            return False
        
        # Verificar intervalo de tempo
        current_time = time.time()
        if symbol in self.ultima_entrada_timestamp:
            tempo_decorrido = current_time - self.ultima_entrada_timestamp[symbol]
            if tempo_decorrido < self.intervalo_entradas:
                return False
        
        # Verificar distância mínima entre entradas
        if symbol in self.entradas_por_symbol and len(self.entradas_por_symbol[symbol]) > 0:
            ultima_entrada = self.entradas_por_symbol[symbol][-1]
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                point = symbol_info.point
                digits = symbol_info.digits
                if digits == 3 or digits == 5:
                    pip_value = 10 * point
                else:
                    pip_value = point
                
                distancia_pips = abs(current_price - ultima_entrada) / pip_value
                if distancia_pips < self.distancia_entradas:
                    return False
        
        return True
    
    def calcular_volume_valido(self, symbol: str, volume_desejado: float) -> float:
        """Calcula volume válido respeitando limites do símbolo."""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return self.volume_min
        
        volume_min_symbol = symbol_info.volume_min
        volume_max_symbol = symbol_info.volume_max
        volume_step_symbol = symbol_info.volume_step
        
        volume = max(volume_min_symbol, min(volume_max_symbol, volume_desejado))
        
        if volume_step_symbol > 0:
            volume = round(volume / volume_step_symbol) * volume_step_symbol
        
        volume = max(volume_min_symbol, min(volume_max_symbol, volume))
        
        return round(volume, 2)
    
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
        """
        Verificação MÍNIMA: apenas verifica se símbolo existe e tem tick.
        REMOVIDAS todas as restrições de idade de tick e spread.
        Deixa o MT5 decidir se pode executar (ele retornará erro se mercado fechado).
        """
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return False
        
        # Apenas verificar se trade_mode não é zero (bloqueado completamente)
        if symbol_info.trade_mode == 0:
            return False
        
        # Verificar se há tick (mesmo que antigo)
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False
        
        # Se há tick e preços válidos, tenta executar
        # O MT5 decidirá se o mercado está realmente aberto
        if tick.ask > 0 and tick.bid > 0:
            return True
        
        return False
    
    def modificar_sl_tp(self, ticket: int, symbol: str, new_sl: float, new_tp: float):
        """Envia uma requisição para modificar o SL e/ou TP de uma ordem."""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": symbol,
            "position": ticket,
            "sl": new_sl,
            "tp": new_tp,
            "magic": self.magic,
            "comment": "SV3_MOVE_SL",
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log_estruturado("sl_modified", {
                "ticket": ticket,
                "symbol": symbol,
                "new_sl": new_sl,
                "new_tp": new_tp
            }, print_to_console=False)
            return True
        else:
            self.log_estruturado("error_sltp_modify", {
                "ticket": ticket,
                "symbol": symbol,
                "retcode": result.retcode if result else 'N/A'
            })
            return False
    
    def fechar_posicao_parcial(self, pos, volume_to_close: float, reason: str):
        """Fecha uma parte do volume da posição BUY."""
        symbol = pos.symbol
        ticket = pos.ticket
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False
        
        preco_fechamento = tick.bid
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
            "comment": f"SV3_{reason}"[:32],
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log_estruturado("position_partially_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": reason,
                "volume_closed": volume_to_close,
                "pnl_realized": result.profit
            })
            return True
        else:
            self.log_estruturado("error_partial_closing", {
                "symbol": symbol,
                "ticket": ticket,
                "retcode": result.retcode if result else 'N/A'
            })
            return False
    
    def gerenciar_risco_posicao(self, pos):
        """Gestão de risco escalonada com múltiplos TPs parciais."""
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
        
        # Verificar fechamentos parciais escalonados
        ticket_key = f"{pos.ticket}_{pos.symbol}"
        
        # TP Parcial 1: 200 pips (fecha 25%)
        if profit_in_pips >= self.tp_parcial_1 and f"{ticket_key}_tp1" not in self.parcial_closed:
            volume_fechar = pos.volume * 0.25
            if volume_fechar >= 0.01:
                if self.fechar_posicao_parcial(pos, volume_fechar, "TP_PARCIAL_200"):
                    self.parcial_closed[f"{ticket_key}_tp1"] = True
        
        # TP Parcial 2: 400 pips (fecha 25%)
        if profit_in_pips >= self.tp_parcial_2 and f"{ticket_key}_tp2" not in self.parcial_closed:
            volume_fechar = pos.volume * 0.25
            if volume_fechar >= 0.01:
                if self.fechar_posicao_parcial(pos, volume_fechar, "TP_PARCIAL_400"):
                    self.parcial_closed[f"{ticket_key}_tp2"] = True
        
        # TP Parcial 3: 600 pips (fecha 25%)
        if profit_in_pips >= self.tp_parcial_3 and f"{ticket_key}_tp3" not in self.parcial_closed:
            volume_fechar = pos.volume * 0.25
            if volume_fechar >= 0.01:
                if self.fechar_posicao_parcial(pos, volume_fechar, "TP_PARCIAL_600"):
                    self.parcial_closed[f"{ticket_key}_tp3"] = True
        
        # Break-Even
        be_price_level = pos.price_open + (self.be_margin_points * point)
        be_price_level = round(be_price_level, digits)
        
        if (profit_in_pips >= self.be_trigger_pips) and (pos.sl < be_price_level):
            if self.modificar_sl_tp(pos.ticket, pos.symbol, be_price_level, pos.tp):
                self.log_estruturado("risk_management", {
                    "symbol": pos.symbol,
                    "ticket": pos.ticket,
                    "action": "BREAK_EVEN_SET",
                    "profit_pips": round(profit_in_pips, 1),
                    "new_sl": be_price_level
                })
        
        # Trailing Stop
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
                        "profit_pips": round(profit_in_pips, 1),
                        "new_sl": new_trailing_sl
                    })
    
    def executar_ordem_escalonada(self, symbol: str):
        """
        Executa ordem escalonada com volume progressivo.
        Versão COM FILTROS RIGOROSOS: Valida todas as condições antes de executar.
        """
        
        # FILTRO 1: Verificação básica de mercado
        if not self.verificar_mercado_aberto(symbol):
            return False
        
        # FILTRO 2: Validação completa de condições de mercado (NOVO)
        pode_operar, motivo = self.validar_condicoes_mercado(symbol)
        if not pode_operar:
            self.log_estruturado("trade_blocked_filter", {
                "symbol": symbol,
                "reason": motivo,
                "pnl_total": round(self.calcular_pnl_total(), 2)
            }, print_to_console=False)
            return False
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False
        
        current_price = tick.ask
        
        # Verificar se pode abrir nova entrada
        if not self.pode_abrir_nova_entrada(symbol, current_price):
            return False
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False
            
            # Calcular volume escalonado
            posicoes_abertas = self.verificar_posicoes_abertas(symbol)
            num_entradas = len(posicoes_abertas)
            volume_escalonado = self.calcular_volume_escalonado(symbol, num_entradas)
            volume_valido = self.calcular_volume_valido(symbol, volume_escalonado)
            
            filling_mode = self.obter_filling_mode(symbol)
            
            point = symbol_info.point
            digits = symbol_info.digits
            
            if digits == 3 or digits == 5:
                pip_value = 10 * point
            else:
                pip_value = point
            
            # SL/TP para tendências grandes
            sl_price = round(current_price - (self.sl_pips * pip_value), digits)
            tp_price = round(current_price + (self.tp_pips * pip_value), digits)
            
            # Validações finais antes de enviar
            if current_price <= 0 or sl_price <= 0 or tp_price <= 0:
                self.log_estruturado("error_validation", {
                    "symbol": symbol,
                    "reason": "INVALID_PRICES",
                    "current_price": current_price,
                    "sl_price": sl_price,
                    "tp_price": tp_price
                })
                print(f"[{symbol}] ❌ Preços inválidos. Pulando...")
                return False
            
            if volume_valido <= 0:
                self.log_estruturado("error_validation", {
                    "symbol": symbol,
                    "reason": "INVALID_VOLUME",
                    "volume": volume_valido
                })
                print(f"[{symbol}] ❌ Volume inválido: {volume_valido}. Pulando...")
                return False
            
            # Verificar se trading está habilitado na conta
            account_info = mt5.account_info()
            if account_info is None:
                self.log_estruturado("error_validation", {
                    "symbol": symbol,
                    "reason": "ACCOUNT_INFO_NULL"
                })
                print(f"[{symbol}] ❌ Não foi possível obter informações da conta. Pulando...")
                return False
            
            if not account_info.trade_allowed:
                self.log_estruturado("error_validation", {
                    "symbol": symbol,
                    "reason": "TRADING_NOT_ALLOWED"
                })
                print(f"[{symbol}] ⏸️ Trading não permitido na conta. Pulando...")
                return False
            
            # Comentário limitado a 32 caracteres (limite do MT5)
            comment = f"SV3_E{num_entradas + 1}"[:32]
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume_valido,
                "type": mt5.ORDER_TYPE_BUY,
                "price": current_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": self.magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            
            # Log do request antes de enviar (para debug)
            self.log_estruturado("order_request", {
                "symbol": symbol,
                "volume": volume_valido,
                "price": current_price,
                "sl": sl_price,
                "tp": tp_price,
                "filling_mode": filling_mode
            }, print_to_console=False)
            
            result = mt5.order_send(request)
            
            # Verificar se result é None (erro crítico)
            if result is None:
                error_info = mt5.last_error()
                error_code = error_info[0] if isinstance(error_info, tuple) else error_info
                error_description = error_info[1] if isinstance(error_info, tuple) and len(error_info) > 1 else str(error_info)
                
                self.log_estruturado("error_opening", {
                    "symbol": symbol,
                    "retcode": "NONE",
                    "error_code": error_code,
                    "error_description": error_description,
                    "error_message": f"MT5 retornou None - Código: {error_code}, Descrição: {error_description}"
                })
                print(f"[{symbol}] ❌ FALHA CRÍTICA: MT5 retornou None")
                print(f"   -> Erro MT5: {error_code} - {error_description}")
                return False
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # Registrar entrada
                self.entradas_por_symbol[symbol].append(current_price)
                self.ultima_entrada_timestamp[symbol] = time.time()
                
                self.log_estruturado("position_opened", {
                    "symbol": symbol,
                    "ticket": result.order,
                    "type": "BUY",
                    "entry_price": round(float(result.price), digits),
                    "sl_price": round(float(sl_price), digits),
                    "tp_price": round(float(tp_price), digits),
                    "volume": round(float(volume_valido), 2),
                    "entrada_numero": num_entradas + 1,
                    "total_entradas_symbol": num_entradas + 1,
                    "reason": "MA_CROSSOVER_ESCALONADO"
                })
                
                print(f"[{symbol}] ✅ ORDEM ESCALONADA #{num_entradas + 1}:")
                print(f"   -> Ticket: {result.order} | Preço: {result.price:.{digits}f}")
                print(f"   -> Volume: {volume_valido:.2f} | SL: {sl_price:.{digits}f} ({self.sl_pips} pips)")
                print(f"   -> TP: {tp_price:.{digits}f} ({self.tp_pips} pips)")
                print(f"   -> Total de entradas: {num_entradas + 1}")
                
                return True
            else:
                # Tratamento inteligente de erros - MT5 decidiu que não pode executar
                if result:
                    retcode = result.retcode
                    comment = getattr(result, 'comment', 'N/A')
                    
                    # Erros comuns e suas mensagens
                    if retcode == 10018 or retcode == mt5.TRADE_RETCODE_MARKET_CLOSED:
                        print(f"[{symbol}] ⏸️ Mercado fechado (MT5: {retcode}). Aguardando próximo ciclo...")
                        self.log_estruturado("trade_block_mt5", {
                            "symbol": symbol,
                            "retcode": retcode,
                            "reason": "MARKET_CLOSED_BY_MT5",
                            "comment": comment
                        }, print_to_console=False)
                    elif retcode == mt5.TRADE_RETCODE_REQUOTE:
                        print(f"[{symbol}] 🔄 Requote (preço mudou). Tentando novamente...")
                        # Tentar uma vez mais com novo preço
                        time.sleep(0.5)
                        new_tick = mt5.symbol_info_tick(symbol)
                        if new_tick and new_tick.ask > 0:
                            new_price = new_tick.ask
                            new_sl_price = round(new_price - (self.sl_pips * pip_value), digits)
                            new_tp_price = round(new_price + (self.tp_pips * pip_value), digits)
                            request["price"] = new_price
                            request["sl"] = new_sl_price
                            request["tp"] = new_tp_price
                            result = mt5.order_send(request)
                            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                                self.entradas_por_symbol[symbol].append(new_price)
                                self.ultima_entrada_timestamp[symbol] = time.time()
                                self.log_estruturado("position_opened", {
                                    "symbol": symbol,
                                    "ticket": result.order,
                                    "type": "BUY",
                                    "entry_price": round(float(result.price), digits),
                                    "sl_price": round(float(new_sl_price), digits),
                                    "tp_price": round(float(new_tp_price), digits),
                                    "volume": round(float(volume_valido), 2),
                                    "entrada_numero": num_entradas + 1,
                                    "requote": True
                                })
                                print(f"[{symbol}] ✅ ORDEM EXECUTADA (REQUOTE): Ticket: {result.order}")
                                return True
                    else:
                        error_msg = f"Código: {retcode} - {comment}"
                        self.log_estruturado("error_opening", {
                            "symbol": symbol,
                            "retcode": retcode,
                            "error_message": error_msg,
                            "comment": comment
                        })
                        print(f"[{symbol}] ❌ FALHA NA ORDEM: {error_msg}")
                else:
                    error_msg = "Sem resposta do MT5"
                    self.log_estruturado("error_opening", {
                        "symbol": symbol,
                        "retcode": "N/A",
                        "error_message": error_msg
                    })
                    print(f"[{symbol}] ❌ FALHA NA ORDEM: {error_msg}")
                
                return False
                
        except Exception as e:
            self.log_estruturado("error_critical_execution", {"symbol": symbol, "error": str(e)})
            print(f"[{symbol}] ❌ ERRO CRÍTICO: {e}")
            return False
    
    def ciclo_operacional(self):
        """Ciclo operacional com múltiplas entradas escalonadas."""
        self.log_estruturado("cycle_start", {
            "version": "SILVER SYSTEM V3.0 ESCALONADO",
            "timestamp": datetime.now().isoformat()
        }, print_to_console=False)
        
        print(f"\n==================================================")
        print(f"🔄 CICLO INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   SISTEMA: SILVER V3.0 ESCALONADO")
        print(f"   ANÁLISE: D1 + H4 + H1 (Multi-Timeframe)")
        print(f"   EXECUÇÃO: M1 (após confirmação)")
        print(f"==================================================")
        
        for symbol in self.symbols:
            # ANÁLISE MULTI-TIMEFRAME: D1 + H4 + H1 (confirmação de tendência)
            # EXECUÇÃO: M1 (após confirmação)
            sinal = self.analise_multi_timeframe(symbol)
            posicoes_abertas = self.verificar_posicoes_abertas(symbol)
            
            # Gerenciar todas as posições abertas
            for pos in posicoes_abertas:
                self.gerenciar_risco_posicao(pos)
            
            # Se há sinal BUY, pode abrir nova entrada escalonada
            if sinal == "BUY":
                self.executar_ordem_escalonada(symbol)
            
            time.sleep(1)

# --- EXECUÇÃO PRINCIPAL ---
def main():
    sistema = SistemaOperacional(RISK_CONFIG)
    
    if sistema.conectar_mt5():
        simbolos_validos = sistema.descobrir_ativos_silver()
        
        if not simbolos_validos:
            print("❌ Nenhum símbolo de prata válido encontrado.")
            mt5.shutdown()
            return
        
        sistema.symbols = simbolos_validos
        sistema.config['symbols'] = simbolos_validos
        
        print(f"🥈 SILVER SYSTEM V3.0 ESCALONADO INICIADO!")
        print(f"📊 Monitorando {len(sistema.symbols)} símbolos: {', '.join(sistema.symbols)}")
        print(f"🔢 Magic Number: {sistema.magic}")
        print(f"⏱️  ANÁLISE MULTI-TIMEFRAME: D1 + H4 + H1 (confirmação)")
        print(f"⚡ EXECUÇÃO: M1 (após confirmação de todos os timeframes)")
        print(f"💰 Volume: {sistema.volume_min:.2f} - {sistema.volume_max:.2f} lotes (escalonado)")
        print(f"📈 Entradas: Ilimitadas por símbolo")
        print(f"🛡️  SL: {sistema.sl_pips} pips | TP: {sistema.tp_pips} pips")
        print(f"💎 TPs Parciais: {sistema.tp_parcial_1}/{sistema.tp_parcial_2}/{sistema.tp_parcial_3} pips")
        print(f"📊 Log: {sistema.log_file}")
        print()
        
        sistema.log_estruturado("system_started", {
            "version": "SILVER SYSTEM V3.0 ESCALONADO",
            "project": "SilverGMarket",
            "symbols": sistema.symbols,
            "analysis_timeframes": "D1+H4+H1",
            "execution_timeframe": "M1",
            "volume_range": f"{sistema.volume_min}-{sistema.volume_max}",
            "max_positions": sistema.max_posicoes,
            "sl_pips": sistema.sl_pips,
            "tp_pips": sistema.tp_pips
        })
        
        try:
            while True:
                sistema.ciclo_operacional()
                print(f"⏳ Aguardando 60 segundos para o próximo ciclo (M1)...")
                time.sleep(60)  # Ciclo de 1 minuto para M1
                
        except KeyboardInterrupt:
            sistema.log_estruturado("system_shutdown", {"reason": "Stopped by user"})
            print("\n\n⏹️ Parado pelo usuário.")
        except Exception as e:
            sistema.log_estruturado("error_fatal", {"error": str(e)})
            print(f"\n\n🚨 ERRO FATAL: {e}")
            import traceback
            traceback.print_exc()
            
    mt5.shutdown()
    print("✅ Conexão MT5 encerrada.")

if __name__ == "__main__":
    main()

