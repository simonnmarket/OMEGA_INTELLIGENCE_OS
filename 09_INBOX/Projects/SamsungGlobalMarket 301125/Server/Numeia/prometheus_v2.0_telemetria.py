# ==============================================================================
# PROMETHEUS V2.0: SISTEMA OPERACIONAL (TELEMETRIA E LOGGING ESTRUTURADO)
# Foco: Manter a proteção V1.2 + Implementar Logging Estruturado (JSON)
# Data: 26/11/2025
# ==============================================================================
import MetaTrader5 as mt5
import time
from datetime import datetime
import numpy as np
import json  # Necessário para o logging estruturado

# --- CONFIGURAÇÃO MÍNIMA ---
RISK_CONFIG = {
    'symbols': [],  # Será preenchido automaticamente com todos os símbolos do Market Watch
    'volume': 0.01,  # Lote fixo e mínimo (será ajustado por símbolo)
    'magic': 99991,
    'timeframe': mt5.TIMEFRAME_M15,
    # V1.1: Stop Loss e Take Profit em pips (mantido)
    'stop_loss_pips': 20,  # Stop Loss: 20 pips
    'take_profit_pips': 40,  # Take Profit: 40 pips (1:2 Risk/Reward)
}

# ==============================================================================
# CLASSE SistemaOperacional - O ESQUELETO COM TELEMETRIA
# ==============================================================================
class SistemaOperacional:
    def __init__(self, config):
        self.config = config
        self.symbols = config['symbols']
        self.volume = config['volume']
        self.magic = config['magic']
        self.sl_pips = config.get('stop_loss_pips', 20)
        self.tp_pips = config.get('take_profit_pips', 40)
        self.log_file = "prometheus_telemetry_v2.0.log"
        
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
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        log_json = json.dumps(log_entry, ensure_ascii=False)
        
        # 1. Grava no arquivo de log (não-bloqueante)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_json + "\n")
        except Exception as e:
            print(f"❌ ERRO GRAVE ao escrever log: {e}")
            
        # 2. Imprime no console (se ativado)
        if print_to_console:
            print(f"[LOG: {event_type}] {log_json}")

    def conectar_mt5(self):
        """Conexão simples e robusta com verificação básica."""
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
        """Calcula a Média Móvel Simples (SMA) do preço de fechamento."""
        precos_fechamento = rates['close']
        if len(precos_fechamento) < periodo:
            return None 
            
        ma = np.convolve(precos_fechamento, np.ones(periodo), 'valid') / periodo
        # Retorna o último valor
        return ma[-1] 

    def analise_simples(self, symbol: str) -> str:
        """
        Análise MÍNIMA e REAL: Estratégia de Crossover de Média Móvel.
        Retorna BUY ou NO_SIGNAL.
        """
        try:
            # Puxa 50 barras + 1 para garantir o cálculo da MA Lenta (50)
            rates = mt5.copy_rates_from_pos(symbol, self.config['timeframe'], 0, 51)
            
            if rates is None or len(rates) < 51:
                self.log_estruturado("data_warning", {"symbol": symbol, "message": "Dados insuficientes para análise MA."}, print_to_console=False)
                return "NO_DATA"
                
            # Parâmetros da Estratégia de Média Móvel Simples (SMA Crossover)
            PERIODO_MA_RAPIDA = 20
            PERIODO_MA_LENTA = 50

            ma_rapida = self.calcular_ma(rates, PERIODO_MA_RAPIDA)
            ma_lenta = self.calcular_ma(rates, PERIODO_MA_LENTA)
            
            if ma_rapida is None or ma_lenta is None:
                self.log_estruturado("data_warning", {"symbol": symbol, "message": "Erro no cálculo da MA."}, print_to_console=False)
                return "NO_DATA"

            # Regra: Tendência de Alta Confirmada (MA Rápida > MA Lenta)
            if ma_rapida > ma_lenta:
                last_close = rates['close'][-1]
                self.log_estruturado("signal_detected", {
                    "symbol": symbol, 
                    "signal": "BUY", 
                    "ma20": round(float(ma_rapida), 5), 
                    "ma50": round(float(ma_lenta), 5),
                    "close_price": round(float(last_close), 5)
                }, print_to_console=False)
                print(f"[{symbol}] ✅ SINAL BUY: Close={last_close:.5f}, MA20={ma_rapida:.5f}, MA50={ma_lenta:.5f}")
                return "BUY"
            
            # Reversão/Sinal Neutro: Média Rápida <= Média Lenta
            return "NO_SIGNAL"
                
        except Exception as e:
            self.log_estruturado("error_analysis", {"symbol": symbol, "error": str(e)})
            return "ERROR"
    
    def verificar_posicoes_abertas(self, symbol: str) -> list:
        """Verifica e retorna a lista de posições BUY abertas pelo nosso robô no ativo."""
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            # Filtra apenas posições BUY com o nosso Magic Number
            return [p for p in positions if p.magic == self.magic and p.type == mt5.POSITION_TYPE_BUY]
        return []

    def fechar_posicao_simples(self, posicao_a_fechar):
        """
        Tenta fechar a posição BUY especificada.
        (V1.2 logic mantida)
        """
        symbol = posicao_a_fechar.symbol
        ticket = posicao_a_fechar.ticket
        volume = posicao_a_fechar.volume
        
        # Obter o preço de fechamento (bid para fechar uma compra)
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
            "comment": "PROMETHEUS_V2_0_SAIDA_REVERSAO",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        
        # LOGGING ESTRUTURADO PARA SAÍDA DE REVERSÃO
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log_estruturado("position_closed", {
                "symbol": symbol,
                "ticket": ticket,
                "reason": "SIGNAL_REVERSAL",
                "entry_price": round(float(posicao_a_fechar.price_open), 5),
                "close_price": round(float(result.price), 5),
                "pnl": round(float(result.profit), 2),  # PnL realizado
                "volume": round(float(volume), 2)
            })
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
        Execução com SL e TP fixos em pips (Survival Risk).
        (V1.1 logic mantida + melhorias)
        """
        
        # 1. Checa se já existe posição aberta
        if self.verificar_posicoes_abertas(symbol):
            self.log_estruturado("trade_block", {"symbol": symbol, "reason": "POSITION_ALREADY_OPEN"}, print_to_console=False)
            print(f"[{symbol}] 🛑 BLOQUEIO: Posição BUY já aberta pelo Magic Number {self.magic}.")
            return False
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None or tick.time == 0:
                self.log_estruturado("error_execution", {"symbol": symbol, "message": "Sem dados de tick recentes."})
                return False
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.log_estruturado("error_execution", {"symbol": symbol, "message": "Não foi possível obter informações do símbolo."})
                return False

            # Calcular volume válido para o símbolo
            volume_valido = self.calcular_volume_valido(symbol)
            
            # Obter modo de preenchimento correto para o símbolo
            filling_mode = self.obter_filling_mode(symbol)

            # 2. Obtenção do Preço e Ponto
            preco_entrada = tick.ask 
            point = symbol_info.point
            digits = symbol_info.digits
            
            # 3. Cálculo de SL e TP (em pips)
            # Para símbolos com 3 ou 5 digits, 1 pip = 10 * point
            # Para símbolos com 2 ou 4 digits, 1 pip = point
            if digits == 3 or digits == 5:
                pip_value = 10 * point
            else:
                pip_value = point
            
            # BUY: SL abaixo, TP acima
            sl_price = preco_entrada - (self.sl_pips * pip_value)
            tp_price = preco_entrada + (self.tp_pips * pip_value)
            
            # Normalizar preços
            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)
            
            # 4. Construção e Envio da Requisição
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
                "comment": "PROMETHEUS_V2_0_TELEMETRIA",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            
            result = mt5.order_send(request)
            
            # LOGGING ESTRUTURADO PARA ENTRADA
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
                print(f"[{symbol}] ✅ ORDEM V2.0 SUCESSO:")
                print(f"   -> Ticket: {result.order} | Preço: {result.price:.{digits}f}")
                print(f"   -> SL/TP Válidos: SL={sl_price:.{digits}f} ({self.sl_pips} pips) | TP={tp_price:.{digits}f} ({self.tp_pips} pips)")
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
        """Ciclo SIMPLES, ITERATIVO e FUNCIONAL com Telemetria."""
        self.log_estruturado("cycle_start", {"version": "V2.0 Telemetria", "timestamp": datetime.now().isoformat()}, print_to_console=False)
        
        print(f"\n==================================================")
        print(f"🔄 CICLO INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   VERSÃO: V2.0 Telemetria (Logging Estruturado)")
        print(f"==================================================")
        
        for symbol in self.symbols:
            sinal = self.analise_simples(symbol)
            
            posicoes_abertas = self.verificar_posicoes_abertas(symbol)
            
            # 1. Lógica de Saída (Monitoramento V1.2 mantida)
            if posicoes_abertas:
                # Se o sinal foi perdido E temos posições abertas
                if sinal == "NO_SIGNAL" or sinal == "ERROR" or sinal == "NO_DATA":
                    for pos in posicoes_abertas:
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
                    print(f"[{symbol}] ℹ️ POSIÇÃO ATIVA. Sinal BUY mantido.")
                    
            # 2. Lógica de Entrada
            elif sinal == "BUY":
                # Tenta executar a ordem protegida
                self.executar_ordem_simples(symbol)
            
            # Pausa breve entre os símbolos para evitar sobrecarga
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
        
        print(f"🚀 SISTEMA OPERACIONAL V2.0 (TELEMETRIA) INICIADO!")
        print(f"📈 Monitorando {len(sistema.symbols)} ativos do Market Watch")
        print(f"⏱️  Timeframe: M15 | Intervalo entre ciclos: 5 minutos")
        print(f"🛡️  Gestão de Risco: SL={sistema.sl_pips} pips | TP={sistema.tp_pips} pips")
        print(f"🔄 Monitoramento: Fechamento automático por reversão de sinal")
        print(f"📊 Log de Telemetria: {sistema.log_file}")
        print()
        
        sistema.log_estruturado("system_started", {
            "version": "V2.0 Telemetria",
            "total_symbols": len(sistema.symbols),
            "sl_pips": sistema.sl_pips,
            "tp_pips": sistema.tp_pips,
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

