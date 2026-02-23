#!/usr/bin/env python3
"""
SOLUÇÃO DEFINITIVA - AURORA MT5
================================
Solução profissional para executar ordens no MT5 sem erros amadores.

OBJETIVO: Descobrir símbolos corretos e executar ordens de forma robusta.
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("SOLUCAO_DEFINITIVA")

def descobrir_simbolos_crypto() -> Dict[str, str]:
    """
    Descobre os símbolos CORRETOS de crypto no MT5.
    Retorna mapeamento: {"BTCUSD": "BTCUSD.m", ...}
    """
    if not mt5.initialize():
        logger.error("Falha ao inicializar MT5")
        return {}
    
    try:
        # Obter TODOS os símbolos disponíveis
        symbols = mt5.symbols_get()
        logger.info(f"Total de símbolos no MT5: {len(symbols)}")
        
        # Procurar cryptos
        crypto_patterns = {
            "BTC": ["BTC", "BITCOIN"],
            "ETH": ["ETH", "ETHEREUM"],
            "BNB": ["BNB", "BINANCE"],
            "SOL": ["SOL", "SOLANA"],
            "XRP": ["XRP", "RIPPLE"]
        }
        
        encontrados = {}
        
        for symbol_info in symbols:
            name = symbol_info.name.upper()
            
            for crypto_key, patterns in crypto_patterns.items():
                if any(pattern in name for pattern in patterns):
                    # Verificar se é símbolo negociável
                    if symbol_info.trade_mode == 4:  # TRADE_MODE_FULL
                        encontrados[f"{crypto_key}USD"] = symbol_info.name
                        logger.info(f"✅ {crypto_key}USD encontrado: {symbol_info.name}")
                        break
        
        return encontrados
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return {}
    finally:
        mt5.shutdown()

def testar_ordem_simples(symbol: str) -> Dict:
    """Testa executar uma ordem simples no símbolo."""
    if not mt5.initialize():
        return {"success": False, "error": "MT5 não inicializado"}
    
    try:
        # Selecionar símbolo
        if not mt5.symbol_select(symbol, True):
            error = mt5.last_error()
            return {"success": False, "error": f"Símbolo não disponível: {error}"}
        
        # Obter tick
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return {"success": False, "error": "Tick não disponível"}
        
        # Obter info do símbolo
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return {"success": False, "error": "Info do símbolo não disponível"}
        
        logger.info(f"📊 {symbol}:")
        logger.info(f"   Point: {symbol_info.point}")
        logger.info(f"   Digits: {symbol_info.digits}")
        logger.info(f"   Volume Min: {symbol_info.volume_min}")
        logger.info(f"   Ask: {tick.ask}, Bid: {tick.bid}")
        
        # Preparar ordem de teste
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": symbol_info.volume_min,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": 10,
            "magic": 999999,
            "comment": "TESTE_SIMPLES",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        logger.info(f"📤 Enviando ordem de teste...")
        result = mt5.order_send(request)
        
        if result is None:
            error = mt5.last_error()
            return {"success": False, "error": f"Result None: {error}"}
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                "success": False,
                "error": f"{result.retcode}: {result.comment}",
                "retcode": result.retcode,
                "comment": result.comment
            }
        
        # Fechar ordem imediatamente
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": symbol_info.volume_min,
            "type": mt5.ORDER_TYPE_SELL,
            "position": result.order,
            "deviation": 10,
            "magic": 999999,
            "comment": "FECHAR_TESTE",
        }
        
        mt5.order_send(close_request)
        
        return {
            "success": True,
            "ticket": result.order,
            "price": result.price,
            "message": "Ordem executada e fechada com sucesso"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        mt5.shutdown()

def main():
    """Função principal."""
    print("=" * 60)
    print("SOLUÇÃO DEFINITIVA - DESCOBRIR SÍMBOLOS E TESTAR ORDENS")
    print("=" * 60)
    
    # 1. Descobrir símbolos
    print("\n1️⃣ Descobrindo símbolos de crypto no MT5...")
    simbolos = descobrir_simbolos_crypto()
    
    if not simbolos:
        print("❌ Nenhum símbolo de crypto encontrado!")
        return
    
    print(f"\n✅ Símbolos encontrados: {len(simbolos)}")
    for key, value in simbolos.items():
        print(f"   {key} → {value}")
    
    # 2. Testar cada símbolo
    print("\n2️⃣ Testando execução de ordens...")
    resultados = {}
    
    for crypto_key, symbol_name in simbolos.items():
        print(f"\n🧪 Testando {crypto_key} ({symbol_name})...")
        resultado = testar_ordem_simples(symbol_name)
        resultados[crypto_key] = resultado
        
        if resultado.get("success"):
            print(f"   ✅ SUCESSO! Ticket: {resultado.get('ticket')}")
        else:
            print(f"   ❌ FALHA: {resultado.get('error')}")
    
    # 3. Relatório final
    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL")
    print("=" * 60)
    
    sucessos = sum(1 for r in resultados.values() if r.get("success"))
    print(f"\n✅ Símbolos funcionais: {sucessos}/{len(resultados)}")
    
    if sucessos > 0:
        print("\n📋 SÍMBOLOS QUE FUNCIONAM:")
        for key, resultado in resultados.items():
            if resultado.get("success"):
                symbol_name = simbolos[key]
                print(f"   ✅ {key} → {symbol_name}")
        
        print("\n🎯 PRÓXIMO PASSO:")
        print("   Use estes símbolos no sistema principal!")
    else:
        print("\n❌ NENHUM símbolo funcionou!")
        print("   Verifique configuração da conta MT5")
    
    # Salvar mapeamento
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = f"simbolos_mt5_mapeamento_{timestamp}.txt"
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write("MAPEAMENTO DE SÍMBOLOS MT5\n")
        f.write("=" * 50 + "\n\n")
        for key, value in simbolos.items():
            status = "✅ FUNCIONA" if resultados.get(key, {}).get("success") else "❌ FALHA"
            f.write(f"{key} → {value} [{status}]\n")
    
    print(f"\n📁 Mapeamento salvo em: {arquivo}")

if __name__ == "__main__":
    main()

