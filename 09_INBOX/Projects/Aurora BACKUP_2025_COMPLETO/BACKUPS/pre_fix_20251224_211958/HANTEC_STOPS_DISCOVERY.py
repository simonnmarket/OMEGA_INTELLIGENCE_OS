"""
HANTEC_STOPS_DISCOVERY.py - Descobre limites REAIS do Hantec
===========================================================

ESTRATÉGIA: Testa diferentes distâncias até encontrar a mínima aceita.
MÉTODO: Envia ordens de teste com volumes MÍNIMOS até funcionar.
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime
import time

logger = logging.getLogger("HANTEC_DISCOVERY")

def discover_minimal_stops(symbol: str, test_volume: float = 0.01) -> dict:
    """
    Descobre a distância MÍNIMA de stops que o Hantec aceita.
    
    Estratégia: Testa de 1 a 1000 pontos, incrementando até funcionar.
    """
    print(f"\n🔍 DESCOBRINDO LIMITES PARA {symbol}")
    print("=" * 60)
    
    if not mt5.initialize():
        return {"error": "MT5 não inicializado"}
    
    try:
        # Obter informações do símbolo
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return {"error": f"Símbolo {symbol} não encontrado"}
        
        point = symbol_info.point
        digits = symbol_info.digits
        tick = mt5.symbol_info_tick(symbol)
        
        print(f"📊 Informações do {symbol}:")
        print(f"   • Point: {point}")
        print(f"   • Digits: {digits}")
        print(f"   • Ask: {tick.ask}")
        print(f"   • Bid: {tick.bid}")
        print(f"   • Stops Level: {symbol_info.trade_stops_level}")
        print(f"   • Volume Min: {symbol_info.volume_min}")
        
        results = []
        price = tick.ask
        
        # TESTAR DISTÂNCIAS CRESCENTES
        print(f"\n🧪 Testando distâncias mínimas...")
        
        for distance_points in [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]:
            distance_price = distance_points * point
            
            # Calcular SL/TP
            sl = round(price - distance_price, digits)
            tp = round(price + (distance_points * 2 * point), digits)  # TP = 2x distância
            
            print(f"\n   Testando {distance_points} pontos ({distance_price:.5f}):")
            print(f"   Price: {price}, SL: {sl}, TP: {tp}")
            
            # Tentar enviar ordem
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": test_volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": 999999,
                "comment": f"Test_{distance_points}pts",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"   ✅ ACEITO com {distance_points} pontos!")
                
                # Fechar ordem imediatamente (não queremos manter)
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": test_volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": tick.bid,
                    "position": result.order,
                    "magic": 999999,
                    "comment": "Close_test",
                }
                
                mt5.order_send(close_request)
                
                return {
                    "symbol": symbol,
                    "min_distance_points": distance_points,
                    "min_distance_price": distance_price,
                    "tested_price": price,
                    "successful_sl": sl,
                    "successful_tp": tp,
                    "status": "FOUND",
                    "message": f"Mínimo: {distance_points} pontos ({distance_price:.5f})"
                }
            else:
                error_msg = f"{result.retcode}: {result.comment}" if result else "No result"
                print(f"   ❌ Rejeitado: {error_msg}")
                results.append({
                    "points": distance_points,
                    "error": error_msg,
                    "sl": sl,
                    "tp": tp
                })
            
            time.sleep(0.5)  # Não floodar o servidor
        
        # Se chegou aqui, nenhum funcionou
        print(f"\n⚠️  NENHUMA distância funcionou até 1000 pontos!")
        
        # ÚLTIMA TENTATIVA: SEM STOPS
        print(f"\n🔄 Tentando SEM stops...")
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": test_volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": 10,
            "magic": 999999,
            "comment": "Test_NoStops",
            "type_time": mt5.ORDER_TIME_GTC,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"   ✅ FUNCIONOU sem stops!")
            
            # Fechar
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": test_volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": tick.bid,
                "position": result.order,
            }
            
            mt5.order_send(close_request)
            
            return {
                "symbol": symbol,
                "min_distance_points": "INFINITE",
                "status": "REQUIRES_NO_STOPS",
                "message": "Só funciona SEM stops inicialmente"
            }
        else:
            return {
                "symbol": symbol,
                "status": "FAILED_ALL",
                "errors": results,
                "message": "Nenhuma configuração funcionou"
            }
            
    except Exception as e:
        return {"error": str(e)}
    finally:
        mt5.shutdown()

def test_all_cryptos():
    """Testa todos os cryptos principais."""
    cryptos = ["BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD", "XRPUSD"]
    results = {}
    
    print("🚀 TESTANDO LIMITES REAIS DO HANTEC")
    print("=" * 60)
    print("OBJETIVO: Descobrir distância MÍNIMA que funciona")
    print("VOLUME: 0.01 (mínimo)")
    print("\n⚠️  ATENÇÃO: Serão abertas/fechadas ordens REAIS na demo")
    print("   Use volume mínimo para testes")
    print("=" * 60)
    
    for crypto in cryptos:
        result = discover_minimal_stops(crypto, test_volume=0.01)
        results[crypto] = result
        
        if "min_distance_points" in result:
            points = result["min_distance_points"]
            price_dist = result.get("min_distance_price", 0)
            
            if points == "INFINITE":
                print(f"\n❌ {crypto}: SÓ FUNCIONA SEM STOPS")
            else:
                print(f"\n✅ {crypto}: MÍNIMO = {points} pontos (${price_dist:.3f})")
        else:
            print(f"\n❌ {crypto}: FALHA - {result.get('message', 'Erro')}")
        
        time.sleep(2)  # Aguardar entre símbolos
    
    return results

def generate_recommendation(results: dict):
    """Gera recomendações baseadas nos testes."""
    print("\n" + "=" * 60)
    print("🎯 RECOMENDAÇÕES BASEADAS NOS TESTES")
    print("=" * 60)
    
    recommendations = []
    
    for symbol, data in results.items():
        if data.get("status") == "FOUND":
            points = data["min_distance_points"]
            price_dist = data["min_distance_price"]
            
            if points <= 10:
                rec = f"✅ {symbol}: OK ({points} pts = ${price_dist:.3f}) - Pode usar stops normais"
            elif points <= 100:
                rec = f"⚠️  {symbol}: Aceitável ({points} pts = ${price_dist:.2f}) - Usar stops largos"
            else:
                rec = f"❌ {symbol}: Inviável ({points} pts = ${price_dist:.1f}) - Recomendo SEM stops"
            
            recommendations.append(rec)
        
        elif data.get("status") == "REQUIRES_NO_STOPS":
            recommendations.append(f"❌ {symbol}: SÓ FUNCIONA SEM STOPS - Usar método 'adicionar depois'")
        else:
            recommendations.append(f"💥 {symbol}: FALHA NOS TESTES - Investigar manualmente")
    
    for rec in recommendations:
        print(f"• {rec}")
    
    print("\n" + "=" * 60)
    print("🚀 ESTRATÉGIA RECOMENDADA:")
    
    # Verificar se algum funciona com stops pequenos
    small_stops = any(
        data.get("min_distance_points", 1000) <= 10 
        for data in results.values() 
        if isinstance(data.get("min_distance_points"), int)
    )
    
    if small_stops:
        print("✅ Alguns símbolos aceitam stops pequenos")
        print("   Usar stops calculados normalmente para esses")
    else:
        print("❌ NENHUM símbolo aceita stops pequenos")
        print("   USAR ESTRATÉGIA: Enviar SEM stops, adicionar depois")
        print("\n🔧 IMPLEMENTAÇÃO:")
        print("   1. Enviar ordem com sl=0, tp=0")
        print("   2. Aguardar execução (2 segundos)")
        print("   3. Adicionar stops com valores grandes")
        print("   4. Se falhar, operar SEM stops (mental stops)")

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.WARNING)  # Reduzir logs do MT5
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║        HANTEC STOPS DISCOVERY - TESTE DE LIMITES REAIS      ║
╠══════════════════════════════════════════════════════════════╣
║ ATENÇÃO: Este script enviará ordens REAIS na conta DEMO     ║
║          com volume MÍNIMO (0.01) para descobrir limites    ║
║                                                              ║
║ OBJETIVO: Descobrir a distância MÍNIMA que o Hantec aceita  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    confirm = input("\n▶️  Continuar? As ordens serão abertas/fechadas automaticamente. [s/N]: ")
    
    if confirm.lower() not in ['s', 'sim', 'y', 'yes']:
        print("⏹️  Cancelado pelo usuário")
        exit(0)
    
    print("\n🚀 Iniciando testes...")
    
    try:
        results = test_all_cryptos()
        generate_recommendation(results)
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hantec_limits_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("HANTEC LIMITS DISCOVERY RESULTS\n")
            f.write("=" * 50 + "\n")
            for symbol, data in results.items():
                f.write(f"\n{symbol}:\n")
                f.write(f"  Status: {data.get('status', 'UNKNOWN')}\n")
                if 'min_distance_points' in data:
                    f.write(f"  Min Points: {data['min_distance_points']}\n")
                    f.write(f"  Min Distance: ${data.get('min_distance_price', 0):.5f}\n")
                f.write(f"  Message: {data.get('message', '')}\n")
        
        print(f"\n📁 Resultados salvos em: {filename}")
        
    except Exception as e:
        print(f"💥 Erro: {e}")
        import traceback
        traceback.print_exc()

