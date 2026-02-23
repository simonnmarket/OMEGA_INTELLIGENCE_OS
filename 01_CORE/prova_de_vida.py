import MetaTrader5 as mt5
import sys

if __name__ == "__main__":
    print("\n" + "="*50)
    print("[FASE 0]: PROVA DE VIDA - CONEXAO MT5")
    print("="*50)
    
    print("\n[1] Tentando conectar ao MetaTrader 5 Terminal...")
    
    if not mt5.initialize():
        print("[FALHA CRITICA]: MT5 nao inicializou.")
        print(f"Erro Interno: {mt5.last_error()}")
        sys.exit(1)
        
    print("[SUCESSO]: Conectado ao Terminal MetaTrader 5.")
    
    # Check connection parameters
    terminal_info = mt5.terminal_info()
    if terminal_info != None:
        print(f"Terminal Info: {terminal_info.name} (Versao {terminal_info.build})")
    
    print("\n[2] Tentando puxar dados reais de mercado (EURUSD)...")
    
    # Try different symbols if EURUSD is not available (e.g., EURUSD.a or EURUSDm)
    symbol = "EURUSD"
    
    # Select the symbol in Market Watch first
    selected = mt5.symbol_select(symbol, True)
    if not selected:
        print(f"[AVISO]: Falha ao selecionar {symbol}. Tentando forcar verificacao mesmo assim...")
        
    tick = mt5.symbol_info_tick(symbol)
    
    if tick:
        print(f"[SUCESSO ABSOLUTO]: Tick de Preco capturado em tempo real!")
        print(f"--> SIMBOLO: {symbol}")
        print(f"--> ASK (Compra): {tick.ask}")
        print(f"--> BID (Venda):  {tick.bid}")
        print(f"--> VOLUME:       {tick.volume}")
    else:
        print(f"[FALHA]: Nao foi possivel obter o Tick para {symbol}.")
        print("Motivo comum: O mercado esta fechado o sufixo da corretora e diferente.")
        print(f"Erro do MT5: {mt5.last_error()}")
        
    print("\n[3] Desconectando e encerrando.")
    mt5.shutdown()
    print("="*50 + "\n")
