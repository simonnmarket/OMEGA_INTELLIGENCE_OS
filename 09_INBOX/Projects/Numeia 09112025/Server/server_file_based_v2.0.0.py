"""
Samsung Global Market - Servidor de Análise ML v2.0.0
Comunicação baseada em arquivos (File-Based IPC)
Baseado em Prometheus EA Server (100% funcional)
"""

import os
import json
import glob
import time
import logging
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SamsungMLServer:
    """
    Servidor de análise ML que se comunica com EA via arquivos JSON.
    """
    
    def __init__(self, mt5_files_path=None):
        """
        Inicializar servidor.
        
        Args:
            mt5_files_path: Caminho para diretório de arquivos do MT5.
                           Se None, usa caminho padrão do Windows.
        """
        if mt5_files_path is None:
            # Caminho padrão do MT5 no Windows
            # Exemplo: C:\Users\<User>\AppData\Roaming\MetaQuotes\Terminal\<ID>\MQL5\Files
            # Você precisa ajustar <ID> para o ID do seu terminal MT5
            mt5_files_path = os.path.join(
                os.getenv('APPDATA'),
                'MetaQuotes', 'Terminal', 'Common', 'Files'
            )
        
        self.mt5_files_path = mt5_files_path
        self.running = False
        
        logger.info(f"Servidor inicializado. Diretório de arquivos: {self.mt5_files_path}")
    
    def analyze_market(self, request_data):
        """
        Analisar dados de mercado e gerar sinal de trading.
        
        Args:
            request_data: Dicionário com dados do request (symbol, bid, ask, etc.)
        
        Returns:
            Dicionário com resposta (action, confidence, reason)
        """
        symbol = request_data.get('symbol', 'UNKNOWN')
        bid = request_data.get('bid', 0.0)
        ask = request_data.get('ask', 0.0)
        spread = request_data.get('spread', 0.0)
        
        logger.info(f"[ANALYZE] {symbol}: bid={bid:.5f}, ask={ask:.5f}, spread={spread:.1f}")
        
        # ============================================================
        # TODO: IMPLEMENTAR LÓGICA DE ANÁLISE ML AQUI
        # ============================================================
        # 
        # Exemplos de análise:
        # 1. Análise técnica (indicadores, padrões)
        # 2. Análise de sentimento (notícias, redes sociais)
        # 3. Modelo de ML (Random Forest, LSTM, etc.)
        # 4. Análise de volume e liquidez
        # 5. Correlação com outros ativos
        #
        # Por enquanto, implementação MOCK para demonstração:
        
        # Lógica CORRIGIDA: Considerar spread em relação à volatilidade
        # Spread alto é aceitável se há movimento forte no mercado
        
        import random
        import time
        
        # NOVA LÓGICA: Spread absoluto não é o único critério
        # O que importa é spread RELATIVO à volatilidade/movimento do ativo
        
        # Para sistema MOCK: Aceitar spreads até 15 pips (realista para demo/contas retail)
        # Em produção, calcular volatilidade real (ATR, desvio padrão) e usar ratio
        
        if spread < 15.0:  # Spread aceitável (<15 pips) - realista para contas demo/retail
            # Com spread <15 pips, avaliar oportunidade
            # Em produção: usar indicadores reais (RSI, MACD, tendência, volume)
            
            signal_strength = random.random()
            
            # Ajustar probabilidade baseado no spread
            # Spread baixo (<3 pips) = maior chance de sinal
            # Spread alto (10-15 pips) = chance moderada mas ainda opera
            
            if spread < 3.0:
                threshold = 0.30  # 70% chance de sinal
            elif spread < 6.0:
                threshold = 0.40  # 60% chance de sinal
            else:  # 6-15 pips
                threshold = 0.50  # 50% chance de sinal
            
            if signal_strength > threshold:
                if signal_strength > 0.65:  # BUY
                    action = "BUY"
                    confidence = 0.60 + (signal_strength - 0.65) * 0.30  # 0.60 a 0.90
                    reason = f"Setup compra detectado (spread: {spread:.1f} pips aceitável)"
                else:  # SELL
                    action = "SELL"
                    confidence = 0.55 + (signal_strength - threshold) * 0.35  # 0.55 a 0.85
                    reason = f"Setup venda detectado (spread: {spread:.1f} pips aceitável)"
            else:
                action = "HOLD"
                confidence = 0.52
                reason = f"Aguardando confirmação (spread: {spread:.1f} pips)"
                
        else:
            # Spread muito alto (>15 pips) = spread/movimento > 5% (não vale a pena)
            action = "HOLD"
            confidence = 0.50
            reason = f"Spread excessivo ({spread:.1f} pips) - aguardando melhoria"
        
        # ============================================================
        
        response = {
            "symbol": symbol,
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "timestamp": int(time.time()),
            "server_version": "2.0.0"
        }
        
        logger.info(f"[RESULT] {symbol}: {action} (conf={confidence:.2f}) - {reason}")
        
        return response
    
    def process_request(self, request_file):
        """
        Processar arquivo de request.
        
        Args:
            request_file: Caminho completo do arquivo AIRequest.*.json
        """
        try:
            # 1. Ler request
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            symbol = request_data.get('symbol', 'UNKNOWN')
            logger.info(f"[REQUEST] Processando {symbol} de {os.path.basename(request_file)}")
            
            # 2. Analisar
            response_data = self.analyze_market(request_data)
            
            # 3. Escrever response
            response_file = request_file.replace("AIRequest", "AIResponse")
            with open(response_file, 'w') as f:
                # JSON compacto (sem indentação) para facilitar parsing no EA
                json.dump(response_data, f, separators=(',', ':'))
            
            logger.info(f"[RESPONSE] {symbol} escrito em {os.path.basename(response_file)}")
            
            # 4. Deletar request (limpar)
            os.remove(request_file)
            logger.debug(f"[CLEANUP] {os.path.basename(request_file)} deletado")
            
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] JSON inválido em {request_file}: {e}")
            # Deletar arquivo corrompido
            os.remove(request_file)
        except Exception as e:
            logger.error(f"[ERROR] Falha ao processar {request_file}: {e}")
    
    def run(self):
        """
        Loop principal do servidor.
        """
        self.running = True
        logger.info("Servidor iniciado. Aguardando requests...")
        
        try:
            while self.running:
                # Buscar arquivos de request
                pattern = os.path.join(self.mt5_files_path, "AIRequest.*.json")
                request_files = glob.glob(pattern)
                
                if request_files:
                    logger.info(f"[SCAN] {len(request_files)} request(s) encontrado(s)")
                    
                    # Processar cada request
                    for request_file in request_files:
                        self.process_request(request_file)
                
                # Aguardar 1 segundo antes de próximo scan
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Servidor interrompido pelo usuário (Ctrl+C)")
        except Exception as e:
            logger.error(f"[ERROR] Erro fatal no servidor: {e}")
        finally:
            self.running = False
            logger.info("Servidor finalizado")
    
    def stop(self):
        """
        Parar servidor.
        """
        logger.info("Parando servidor...")
        self.running = False


def main():
    """
    Função principal.
    """
    import sys
    
    print("=" * 60)
    print("Samsung Global Market - Servidor de Análise ML v2.0.0")
    print("Comunicação baseada em arquivos (File-Based IPC)")
    print("=" * 60)
    print()
    
    # Aceitar caminho como argumento de linha de comando
    if len(sys.argv) > 1:
        mt5_files_path = sys.argv[1]
        print(f"Caminho recebido como argumento: {mt5_files_path}")
    else:
        # IMPORTANTE: Ajustar caminho para o diretório de arquivos do MT5
        # Exemplo Windows: C:\Users\<User>\AppData\Roaming\MetaQuotes\Terminal\Common\Files
        mt5_files_path = input("Digite o caminho do diretório de arquivos do MT5 (ou Enter para usar padrão): ").strip()
        
        if not mt5_files_path:
            mt5_files_path = None  # Usar padrão
    
    # Criar servidor
    server = SamsungMLServer(mt5_files_path=mt5_files_path)
    
    # Verificar se diretório existe
    if not os.path.exists(server.mt5_files_path):
        logger.error(f"ERRO: Diretório não encontrado: {server.mt5_files_path}")
        logger.error("Por favor, verifique o caminho e tente novamente.")
        return
    
    logger.info(f"Diretório de arquivos: {server.mt5_files_path}")
    logger.info("Pressione Ctrl+C para parar o servidor")
    print()
    
    # Iniciar servidor
    server.run()


if __name__ == "__main__":
    main()

