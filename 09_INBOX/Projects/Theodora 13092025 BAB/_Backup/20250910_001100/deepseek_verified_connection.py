import MetaTrader5 as mt5
import pandas as pd  # noqa: F401 (reservado para extensões futuras)
import time
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DeepSeek-Verified")


class VerifiedMT5Connection:
    def __init__(self, account, password, server):
        self.account = account
        self.password = password
        self.server = server
        self.connected = False
        self.connection_info = {}
        
    def verify_connection(self):
        """Verificar e estabelecer conexão com MT5"""
        try:
            # Tentar inicializar
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"Falha ao inicializar MT5: {error}")
                return False
                
            # Tentar login
            if not mt5.login(self.account, self.password, self.server):
                error = mt5.last_error()
                logger.error(f"Login falhou: {error}")
                logger.error("Verifique:")
                logger.error(f"   Conta: {self.account}")
                logger.error(f"   Servidor: {self.server}")
                logger.error("   Senha: [VERIFICAR]")
                return False
                
            # Conexão bem-sucedida
            self.connected = True
            account_info = mt5.account_info()
            
            self.connection_info = {
                "login": getattr(account_info, 'login', None),
                "company": getattr(account_info, 'company', None),
                "balance": getattr(account_info, 'balance', None),
                "equity": getattr(account_info, 'equity', None),
                "server": getattr(account_info, 'server', None),
                "trade_mode": getattr(account_info, 'trade_mode', None),
            }
            
            logger.info("CONEXAO VERIFICADA COM SUCESSO!")
            logger.info(f"   Conta: {self.connection_info['login']}")
            logger.info(f"   Corretora: {self.connection_info['company']}")
            logger.info(f"   Servidor: {self.connection_info['server']}")
            logger.info(f"   Saldo: {self.connection_info['balance']}")
            logger.info(f"   Equity: {self.connection_info['equity']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação: {e}")
            return False
    
    def get_symbols_availability(self, symbols):
        """Verificar quais símbolos estão disponíveis"""
        available_symbols = []
        unavailable_symbols = []
        
        for symbol in symbols:
            if mt5.symbol_select(symbol, True):
                info = mt5.symbol_info(symbol)
                if info is not None:
                    available_symbols.append(symbol)
                else:
                    unavailable_symbols.append(symbol)
            else:
                unavailable_symbols.append(symbol)
                
        return available_symbols, unavailable_symbols


# SUAS CREDENCIAIS - EDITAR AQUI (placeholders)
YOUR_ACCOUNT = 12345678           # ← SUA CONTA AQUI
YOUR_PASSWORD = "sua_senha"       # ← SUA SENHA AQUI  
YOUR_SERVER = "seu_servidor"      # ← SEU SERVIDOR AQUI

# SÍMBOLOS PARA VERIFICAR
SYMBOLS_TO_CHECK = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]


def _load_config_defaults():
    cfg_path = os.path.join("Backend", "config.json")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            return (
                int(cfg.get("mt5_account", 0) or 0),
                str(cfg.get("mt5_password", "")),
                str(cfg.get("mt5_server", "")),
                list(cfg.get("symbols", SYMBOLS_TO_CHECK)) or SYMBOLS_TO_CHECK,
            )
        except Exception as e:
            logger.warning(f"Falha ao ler Backend/config.json: {e}")
    return (YOUR_ACCOUNT, YOUR_PASSWORD, YOUR_SERVER, SYMBOLS_TO_CHECK)


def main():
    print("INICIANDO VERIFICACAO DE CONEXAO MT5")
    print("=" * 50)
    
    # Carregar credenciais do config se placeholders não foram alterados
    acc, pwd, srv, symbols = _load_config_defaults()
    if (acc == 12345678 and pwd == "sua_senha" and srv == "seu_servidor"):
        print("ATENCAO: Usando placeholders. Edite Backend/config.json ou ajuste as variaveis do script.")
    
    # 1. Criar conexão
    connection = VerifiedMT5Connection(acc, pwd, srv)
    
    # 2. Verificar conexão
    if connection.verify_connection():
        print("\nCONEXAO BEM-SUCEDIDA!")
        print("=" * 50)
        
        # 3. Verificar símbolos disponíveis
        print("\nVERIFICANDO SIMBOLOS DISPONIVEIS...")
        available, unavailable = connection.get_symbols_availability(symbols)
        
        print(f"Disponivel: {available}")
        if unavailable:
            print(f"Indisponivel: {unavailable}")
            
        print("\nSISTEMA PRONTO PARA TRADING!")
        
    else:
        print("\nFALHA NA CONEXAO")
        print("=" * 50)
        print("Possiveis solucoes:")
        print("1. Verifique se o MetaTrader 5 esta aberto")
        print("2. Confirme numero da conta e servidor")
        print("3. Verifique se a senha esta correta")
        print("4. Confirme se a conta e de trading real/demo")
        print("5. Verifique permissoes de execucao")


if __name__ == "__main__":
    main()


