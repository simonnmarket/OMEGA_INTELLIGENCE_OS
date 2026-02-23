# ==============================================================================
# PROMETHEUS V1.1: SISTEMA OPERACIONAL MÍNIMO VIÁVEL + SURVIVAL RISK (MVPO)
# Foco: Conexão Estável, Estratégia Simples REAL, Execução Garantida + SL/TP.
# Data: 26/11/2025
# Versão: 1.1 (Survival Risk - Adiciona Stop Loss e Take Profit)
# ==============================================================================
import MetaTrader5 as mt5
import time
from datetime import datetime

# --- CONFIGURAÇÃO MÍNIMA ---
# Usamos a configuração mais simples possível para garantir a execução.
RISK_CONFIG = {
    'symbols': [],  # Será preenchido automaticamente com todos os símbolos do Market Watch
    'volume': 0.01,  # Lote fixo e mínimo (será ajustado por símbolo)
    'magic': 99991,
    'timeframe': mt5.TIMEFRAME_M15,
    # V1.1: Gestão de Risco - SL/TP fixos em pips
    'stop_loss_pips': 20,  # Stop Loss fixo: 20 pips
    'take_profit_pips': 40,  # Take Profit fixo: 40 pips (1:2 Risk/Reward)
}

# ==============================================================================
# CLASSE SistemaOperacional - O ESQUELETO MÍNIMO E FUNCIONAL
# ==============================================================================
class SistemaOperacional:
    def __init__(self, config):
        self.config = config
        self.symbols = config['symbols']
        self.volume = config['volume']
        self.magic = config['magic']
    
    def descobrir_ativos_market_watch(self):
        """
        Descobre TODOS os símbolos disponíveis no Market Watch do MT5.
        Filtra apenas símbolos negociáveis (visible=True, trade_mode permite trading).
        """
        print("🔍 Descobrindo ativos do Market Watch...")
        
        all_symbols = mt5.symbols_get()
        if all_symbols is None:
            print("❌ Erro ao obter lista de símbolos do MT5.")
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
        
        print(f"✅ {len(symbols_validos)} ativos válidos descobertos no Market Watch.")
        if len(symbols_validos) > 0:
            print(f"📊 Primeiros 10: {', '.join(symbols_validos[:10])}")
            if len(symbols_validos) > 10:
                print(f"   ... e mais {len(symbols_validos) - 10} ativos")
        
        return symbols_validos
        
    def conectar_mt5(self):
        """Conexão simples e robusta com verificação básica."""
        print("🔄 Tentando conectar ao MetaTrader 5...")
        if not mt5.initialize():
            print(f"❌ Falha na conexão MT5. Erro: {mt5.last_error()}")
            return False
        
        account_info = mt5.account_info()
        if not account_info:
            print("❌ Falha ao obter informações da conta.")
            mt5.shutdown()
            return False
            
        print(f"✅ MT5 Conectado. Login: {account_info.login}")
        return True
    
    def analise_simples(self, symbol: str) -> str:
        """
        Análise MÍNIMA mas REAL: Estratégia de Crossover de Média Móvel (5 vs 20 períodos).
        Apenas gera sinal BUY (conforme diretiva do V7.0/Survival).
        """
        try:
            # Puxa 20 barras (suficiente para as MAs)
            rates = mt5.copy_rates_from_pos(symbol, self.config['timeframe'], 0, 20)
            
            if rates is None or len(rates) < 20:
                print(f"[{symbol}] ⚠️ Dados insuficientes (rates.count={len(rates) if rates is not None else 0}).")
                return "NO_DATA"
                
            closes = [r['close'] for r in rates]
            
            # MA Rápida (5 períodos) - Média dos últimos 5 fechamentos
            ma_rapida = sum(closes[-5:]) / 5
            
            # MA Lenta (20 períodos) - Média dos 20 fechamentos
            ma_lenta = sum(closes) / len(closes)
            
            last_close = closes[-1]
            
            # Condição de BUY: Preço atual > MA Rápida > MA Lenta (Forte tendência de alta)
            if last_close > ma_rapida and ma_rapida > ma_lenta:
                print(f"[{symbol}] ✅ SINAL BUY: Close={last_close:.5f}, MA5={ma_rapida:.5f}, MA20={ma_lenta:.5f}")
                return "BUY"
            
            print(f"[{symbol}] ❌ NO SIGNAL: Tendência não confirmada para BUY.")
            return "NO_SIGNAL"
                
        except Exception as e:
            print(f"[{symbol}] ❌ ERRO ANÁLISE: {e}")
            return "ERROR"
    
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
    
    def executar_ordem_simples(self, symbol: str):
        """Execução GARANTIDA de ordem de mercado (BUY)."""
        
        # Checa se já existe posição aberta para este símbolo (Survival Mínimo)
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            print(f"[{symbol}] 🛑 BLOQUEIO: Posição já aberta (Ticket: {positions[0].ticket}).")
            return False
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None or tick.time == 0:
                print(f"[{symbol}] ❌ ERRO: Sem dados de tick recentes.")
                return False
            
            # Calcular volume válido para o símbolo
            volume_valido = self.calcular_volume_valido(symbol)
            
            # Obter modo de preenchimento correto para o símbolo
            filling_mode = self.obter_filling_mode(symbol)
            
            # V1.1: Calcular SL/TP fixos em pips
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                print(f"[{symbol}] ❌ ERRO: Não foi possível obter informações do símbolo.")
                return False
            
            point = symbol_info.point
            digits = symbol_info.digits
            
            # Calcular SL e TP em pips
            # Para BUY: SL abaixo do preço, TP acima do preço
            entry_price = tick.ask
            sl_pips = self.config.get('stop_loss_pips', 20)
            tp_pips = self.config.get('take_profit_pips', 40)
            
            # Converter pips para preço (considerando digits)
            # Para símbolos com 3 ou 5 digits, 1 pip = 10 * point
            # Para símbolos com 2 ou 4 digits, 1 pip = point
            if digits == 3 or digits == 5:
                pip_value = 10 * point
            else:
                pip_value = point
            
            sl_price = entry_price - (sl_pips * pip_value)
            tp_price = entry_price + (tp_pips * pip_value)
            
            # Normalizar preços para o número de dígitos do símbolo
            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume_valido,  # Volume ajustado para o símbolo
                "type": mt5.ORDER_TYPE_BUY,
                "price": entry_price,
                "sl": sl_price,  # V1.1: Stop Loss fixo
                "tp": tp_price,  # V1.1: Take Profit fixo
                "deviation": 20, # Desvio aceitável (2 pips em Majors)
                "magic": self.magic,
                "comment": "PROMETHEUS_V1.1_SLTP",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,  # Modo detectado automaticamente
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"[{symbol}] ✅ ORDEM EXECUTADA: Ticket: {result.order} | Volume: {result.volume} | SL: {sl_price:.{digits}f} ({sl_pips} pips) | TP: {tp_price:.{digits}f} ({tp_pips} pips)")
                return True
            else:
                # Tentar modo alternativo se falhou (RETURN é mais compatível)
                if result and result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                    if filling_mode != mt5.ORDER_FILLING_RETURN:
                        print(f"[{symbol}] 🔄 Tentando modo RETURN como alternativa...")
                        request["type_filling"] = mt5.ORDER_FILLING_RETURN
                        result = mt5.order_send(request)
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"[{symbol}] ✅ ORDEM EXECUTADA (RETRY): Ticket: {result.order} | Volume: {result.volume}")
                            return True
                
                # Logar a falha com o código de erro
                print(f"[{symbol}] ❌ FALHA NA ORDEM: Código: {result.retcode if result else 'N/A'}")
                if result:
                    print(f"[{symbol}] ❌ Comentário MT5: {result.comment}")
                return False
                
        except Exception as e:
            print(f"[{symbol}] ❌ ERRO CRÍTICO NA EXECUÇÃO: {e}")
            return False
    
    def ciclo_operacional(self):
        """Ciclo SIMPLES, ITERATIVO e FUNCIONAL."""
        print(f"\n==================================================")
        print(f"🔄 CICLO INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"==================================================")
        
        for symbol in self.symbols:
            sinal = self.analise_simples(symbol)
            
            if sinal == "BUY":
                self.executar_ordem_simples(symbol)
            elif sinal == "NO_SIGNAL":
                 print(f"[{symbol}] ℹ️ NO_SIGNAL: Sem condição de compra.")
            
            time.sleep(1)  # Pequeno intervalo para evitar flood de requests

# --- EXECUÇÃO PRINCIPAL ---
def main():
    sistema = SistemaOperacional(RISK_CONFIG)
    
    if sistema.conectar_mt5():
        # Descobrir todos os ativos do Market Watch
        simbolos_descobertos = sistema.descobrir_ativos_market_watch()
        
        if not simbolos_descobertos:
            print("❌ Nenhum ativo válido encontrado. Encerrando sistema.")
            mt5.shutdown()
            return
        
        # Atualizar lista de símbolos com os descobertos
        sistema.symbols = simbolos_descobertos
        sistema.config['symbols'] = simbolos_descobertos
        
        print(f"🚀 SISTEMA OPERACIONAL V1.1 INICIADO! (Survival Risk)")
        print(f"📈 Monitorando {len(sistema.symbols)} ativos do Market Watch")
        print(f"⏱️  Timeframe: M15 | Intervalo entre ciclos: 5 minutos")
        print(f"🛡️  Gestão de Risco: SL={sistema.config.get('stop_loss_pips', 20)} pips | TP={sistema.config.get('take_profit_pips', 40)} pips")
        print()
        
        try:
            # Loop principal de execução
            while True:
                sistema.ciclo_operacional()
                # Intervalo de 5 minutos, adequado para o M15
                print(f"⏳ Aguardando 300 segundos para o próximo ciclo...")
                time.sleep(300)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Parado pelo usuário (KeyboardInterrupt).")
        except Exception as e:
            print(f"\n\n🚨 ERRO FATAL NO LOOP PRINCIPAL: {e}")
            import traceback
            traceback.print_exc()
            
    mt5.shutdown()
    print("✅ Conexão MT5 encerrada.")

if __name__ == "__main__":
    main()

