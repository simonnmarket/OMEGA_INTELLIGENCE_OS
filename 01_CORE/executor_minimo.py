import MetaTrader5 as mt5
import logging
import time

# Configurando o Logging (Registro Inquebrável de Atividades)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("executor_minimo.log"),
        logging.StreamHandler()
    ]
)

def executor_minimo():
    logging.info("=== INICIANDO FASE 1: EXECUTOR MINIMO ===")
    
    # 1. Inicializacao
    if not mt5.initialize():
        logging.error(f"Falha ao inicializar MT5. Erro: {mt5.last_error()}")
        return False
        
    logging.info("MT5 Inicializado com sucesso na maquina local.")
    # 2. Verificacao de Autenticacao (Usando a conta logada no Terminal)
    account_info = mt5.account_info()
    if account_info is not None:
        logging.info(f"DADOS DA CONTA NO TERMINAL -> Balance: ${account_info.balance} | Equity: ${account_info.equity} | Login: {account_info.login}")
        if account_info.login != 510065181:
            logging.warning("⚠️ ATENCAO: O terminal nao esta logado na conta 510065181 (Hantec).")
            logging.warning(f"O script ira operar na conta atual ({account_info.login}). Para usar a conta Hantec, faca o login manualmente no aplicativo do MetaTrader 5.")
    else:
        logging.error("Nao foi possivel recuperar os dados da conta. O terminal esta conectado a internet e logado em uma conta broker?")
        mt5.shutdown()
        return False
        
    # 3. Descobrindo o nome verdadeiro do Bitcoin na Corretora
    logging.info("Buscando o simbolo correto do Bitcoin na corretora...")
    symbols = mt5.symbols_get(group="*BTC*")
    if symbols is None or len(symbols) == 0:
        symbols = mt5.symbols_get(group="*Bitcoin*")
    
    if symbols is None or len(symbols) == 0:
        logging.error("Nao foi encontrado nenhum simbolo contendo 'BTC' ou 'Bitcoin'. O mercado de Cripto esta liberado nessa conta?")
        mt5.shutdown()
        return False
        
    symbol = symbols[0].name
    for s in symbols:
        logging.info(f"Simbolo Encontrado: {s.name}")
        # Prioritize USD pairs
        if "USD" in s.name:
            symbol = s.name
            
    logging.info(f"Selecionado o simbolo para operar: {symbol}")
    
    if not mt5.symbol_select(symbol, True):
        logging.error(f"Falha ao selecionar {symbol}. O simbolo existe na corretora?")
        mt5.shutdown()
        return False

    logging.info(f"Preparando envio de ordem para {symbol}...")
    
    # Obtendo precos atuais
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logging.error(f"Nao foi possivel obter o Tick do {symbol}")
        mt5.shutdown()
        return False
        
    point = mt5.symbol_info(symbol).point
    price = tick.ask
    
    if price == 0.0:
        logging.error(f"FALHA: O preco de {symbol} retornou 0.0. Certifique-se que o simbolo tem liquidacao ou esta aberto no momento.")
        mt5.shutdown()
        return False
        
    lot = 0.01  # Risco minimo de teste
    
    # Estrutura padrao de ordem a mercado MT5 (Buy)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - 5000 * point, # Stop Loss (Crypto needs larger point distance)
        "tp": price + 5000 * point, # Take Profit
        "deviation": 20,
        "magic": 234000, # Numero Magico do OMEGA OS Fase 1
        "comment": "OMEGA_FASE1_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC, # Immediate or Cancel
    }
    
    # 4. Envio Real para a Corretora
    logging.info(f"Disparando Ordem: BUY {lot} {symbol} a {price}")
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(f"A Ordem falhou. Retcode: {result.retcode}")
        # Tratamento de erro 10030 (Unsupported filling mode)
        logging.info("Tentando preenchimento ORDER_FILLING_RETURN...")
        request["type_filling"] = mt5.ORDER_FILLING_RETURN
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            # Fallback final: FOK (Fill Or Kill)
            logging.info("Tentando preenchimento ORDER_FILLING_FOK...")
            request["type_filling"] = mt5.ORDER_FILLING_FOK
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"A Ordem falhou criticamente. Retcode: {result.retcode}. Status: {result.comment}")
            else:
                 logging.info(f"[SUCESSO ABSOLUTO] ORDEM EXECUTADA! Ticket: {result.order}")
        else:
            logging.info(f"[SUCESSO ABSOLUTO] ORDEM EXECUTADA! Ticket: {result.order}")
    else:
        logging.info(f"[SUCESSO ABSOLUTO] ORDEM EXECUTADA! Ticket: {result.order}")

        
    mt5.shutdown()
    logging.info("=== EXECUTOR MINIMO DESCONECTADO ===")
    return True

if __name__ == "__main__":
    executor_minimo()
