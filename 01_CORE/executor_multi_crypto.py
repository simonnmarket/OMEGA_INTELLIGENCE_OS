import MetaTrader5 as mt5
import logging
import time

# Configurando o Logging (Registro Inquebrável de Atividades)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("executor_multi_crypto.log"),
        logging.StreamHandler()
    ]
)

def executor_muti_crypto():
    logging.info("=== INICIANDO EXECUTOR MULTI-CRYPTO (PILOTO INSTITUCIONAL) ===")
    
    # 1. Inicializacao
    if not mt5.initialize():
        logging.error(f"Falha ao inicializar MT5. Erro: {mt5.last_error()}")
        return False
        
    logging.info("MT5 Inicializado com sucesso na maquina local.")
    
    # Ativos alvo do Hub Crypto aprovados para o teste Live
    target_assets = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "LTCUSD"]
    
    success_count = 0
    fail_count = 0
    
    for base_symbol in target_assets:
        logging.info(f"\n--- Processando ativo alvo: {base_symbol} ---")
        
        # Hantec (e outras) costumam colocar sufixos como .m, .i, ou ter nomes ligeramente diferentes
        symbols = mt5.symbols_get(group=f"*{base_symbol[:3]}*")
        
        if not symbols:
            logging.warning(f"Simbolo {base_symbol} nao encontrado na arvore do broker.")
            fail_count += 1
            continue
            
        # Pega o melhor match
        symbol = symbols[0].name
        for s in symbols:
            if "USD" in s.name:
                symbol = s.name
                
        logging.info(f"Match de Broker encontrado: {symbol}. Ativando Market Watch...")
        
        # Forcar selecao e aguardar o terminal injetar cotacoes
        if not mt5.symbol_select(symbol, True):
            logging.error(f"Falha ao selecionar {symbol}. Ativo pode estar desabilitado para esta conta.")
            fail_count += 1
            continue

        time.sleep(1.5) # Aguarda o Market Watch sincronizar
        
        # Obtendo informacoes do ativo na corretora
        sym_info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)
        
        if not tick or tick.ask == 0.0:
            logging.error(f"Nao foi possivel obter o Tick do {symbol} (Pode estar sem cotacao/liquidez agora).")
            fail_count += 1
            continue
            
        if not sym_info:
            logging.error(f"Nao foi possivel obter as restricoes do {symbol}.")
            fail_count += 1
            continue
            
        point = sym_info.point
        price = tick.ask
        
        # AQUI ESTA A CORRECAO DO 'INVALID VOLUME': Pegamos o volume minimo aceito pelo broker para esta altcoin
        lot = sym_info.volume_min 
        
        logging.info(f"Cotacao atual {symbol}: {price}. Lote minimo requerido: {lot}. Preparando envio...")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": price - 10000 * point, 
            "tp": price + 10000 * point,
            "deviation": 20,
            "magic": 234100, # Numero Magico do OMEGA OS Multi-Crypto
            "comment": "OMEGA_PILOT_MULTI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC, # Immediate or Cancel
        }
        
        # Envio Real para a Corretora
        logging.info(f"Disparando Ordem: BUY {lot} {symbol} a {price}")
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"A Ordem falhou para {symbol}. Retcode: {result.retcode}")
            logging.info("Fallback para preenchimento ORDER_FILLING_RETURN...")
            request["type_filling"] = mt5.ORDER_FILLING_RETURN
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.info("Fallback para preenchimento ORDER_FILLING_FOK...")
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                result = mt5.order_send(request)
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logging.error(f"A Ordem falhou criticamente em {symbol}. Retcode: {result.retcode}. Status: {result.comment}")
                    fail_count += 1
                else:
                     logging.info(f"[SUCESSO] ORDEM EXECUTADA ({symbol})! Ticket: {result.order}")
                     success_count += 1
            else:
                logging.info(f"[SUCESSO] ORDEM EXECUTADA ({symbol})! Ticket: {result.order}")
                success_count += 1
        else:
            logging.info(f"[SUCESSO] ORDEM EXECUTADA ({symbol})! Ticket: {result.order}")
            success_count += 1
            
        time.sleep(1) # ZMQ Throttle protection

    logging.info(f"\n=== RELATORIO BATELADA MULTI-CRYPTO ===")
    logging.info(f"SUCESSOS: {success_count} | FALHAS: {fail_count}")
    mt5.shutdown()
    logging.info("=== CONEXAO MT5 DESLIGADA ===")
    return True

if __name__ == "__main__":
    executor_muti_crypto()
