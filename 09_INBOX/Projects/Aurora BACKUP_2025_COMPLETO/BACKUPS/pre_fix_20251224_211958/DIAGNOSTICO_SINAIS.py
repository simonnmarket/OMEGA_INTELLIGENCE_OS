#!/usr/bin/env python3
"""
DIAGNÓSTICO - POR QUE NÃO HÁ SINAIS?
====================================
Investiga por que as estratégias não estão gerando sinais.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def testar_dados(symbol: str):
    """Testa se os dados estão chegando corretamente."""
    print(f"\n{'='*60}")
    print(f"TESTANDO: {symbol}")
    print(f"{'='*60}")
    
    # Converter para formato yfinance
    yf_symbol = symbol.replace("USD", "-USD") if not "-" in symbol else symbol
    
    try:
        # Buscar dados
        print(f"📥 Buscando dados para {yf_symbol}...")
        data = yf.download(yf_symbol, period="1d", interval="5m", progress=False)
        
        if len(data) == 0:
            print(f"❌ NENHUM dado retornado!")
            return False
        
        print(f"✅ Dados recebidos: {len(data)} candles")
        print(f"   Período: {data.index[0]} até {data.index[-1]}")
        print(f"   Colunas: {list(data.columns)}")
        
        # Corrigir MultiIndex se necessário
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        
        # Verificar dados básicos
        print(f"\n📊 ESTATÍSTICAS:")
        close_min = float(data['Close'].min())
        close_max = float(data['Close'].max())
        close_atual = float(data['Close'].iloc[-1])
        vol_min = float(data['Volume'].min())
        vol_max = float(data['Volume'].max())
        vol_atual = float(data['Volume'].iloc[-1])
        
        print(f"   Close: min={close_min:.2f}, max={close_max:.2f}, atual={close_atual:.2f}")
        print(f"   Volume: min={vol_min:.0f}, max={vol_max:.0f}, atual={vol_atual:.0f}")
        
        # Verificar se há dados suficientes
        if len(data) < 20:
            print(f"⚠️  DADOS INSUFICIENTES: {len(data)} candles (mínimo: 20)")
            return False
        
        # Testar estratégias básicas
        print(f"\n🧪 TESTANDO ESTRATÉGIAS:")
        
        # 1. Alpha Momentum
        closes = [float(x) for x in data['Close'].tolist()]
        volumes = [float(x) for x in data['Volume'].tolist()]
        
        if len(closes) >= 10:
            sma_10 = np.mean(closes[-10:])
            sma_20 = np.mean(closes[-20:]) if len(closes) >= 20 else sma_10
            current_price = closes[-1]
            
            momentum_signal = None
            if current_price > sma_10 > sma_20:
                momentum_signal = "BUY"
            elif current_price < sma_10 < sma_20:
                momentum_signal = "SELL"
            
            print(f"   Alpha Momentum: {momentum_signal or 'NENHUM'}")
            print(f"      Preço: {current_price:.2f}, SMA10: {sma_10:.2f}, SMA20: {sma_20:.2f}")
        
        # 2. Mean Reversion
        if len(closes) >= 20:
            sma = np.mean(closes[-20:])
            std = np.std(closes[-20:])
            current = closes[-1]
            
            deviation = (current - sma) / sma * 100
            
            mean_reversion_signal = None
            if deviation < -0.1:  # 0.1% abaixo da média
                mean_reversion_signal = "BUY"
            elif deviation > 0.1:  # 0.1% acima da média
                mean_reversion_signal = "SELL"
            
            print(f"   Mean Reversion: {mean_reversion_signal or 'NENHUM'}")
            print(f"      Desvio: {deviation:.3f}%")
        
        # 3. Breakout
        if len(data) >= 20:
            highs = [float(x) for x in data['High'].tolist()]
            lows = [float(x) for x in data['Low'].tolist()]
            
            recent_high = max(highs[-20:])
            recent_low = min(lows[-20:])
            current_high = highs[-1]
            current_low = lows[-1]
            
            breakout_signal = None
            if current_high > recent_high * 1.001:  # 0.1% acima
                breakout_signal = "BUY"
            elif current_low < recent_low * 0.999:  # 0.1% abaixo
                breakout_signal = "SELL"
            
            print(f"   Breakout: {breakout_signal or 'NENHUM'}")
            print(f"      High: {current_high:.2f} vs {recent_high:.2f}")
            print(f"      Low: {current_low:.2f} vs {recent_low:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal."""
    print("="*60)
    print("DIAGNÓSTICO - POR QUE NÃO HÁ SINAIS?")
    print("="*60)
    
    symbols = ["BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD"]
    
    resultados = {}
    
    for symbol in symbols:
        resultados[symbol] = testar_dados(symbol)
    
    # Resumo
    print(f"\n{'='*60}")
    print("RESUMO")
    print(f"{'='*60}")
    
    sucesso = sum(1 for r in resultados.values() if r)
    print(f"✅ Símbolos com dados: {sucesso}/{len(symbols)}")
    
    if sucesso == 0:
        print("\n❌ PROBLEMA: Nenhum símbolo retornou dados!")
        print("   Possíveis causas:")
        print("   - yfinance não está funcionando")
        print("   - Símbolos incorretos")
        print("   - Problema de conexão")
    else:
        print("\n✅ Dados estão chegando corretamente")
        print("   O problema pode ser:")
        print("   - Estratégias muito restritivas")
        print("   - Condições de mercado não atendidas")
        print("   - Parâmetros muito conservadores")

if __name__ == "__main__":
    main()

