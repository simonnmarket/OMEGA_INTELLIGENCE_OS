#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preparar o sistema para operação em criptomoedas no final de semana
Verifica símbolos disponíveis e sugere configurações
"""

import MetaTrader5 as mt5
import json
from pathlib import Path

def verificar_cripto_disponiveis():
    """Verifica quais criptomoedas estão disponíveis no MT5"""
    print("=" * 80)
    print("VERIFICAÇÃO DE CRIPTOMOEDAS DISPONÍVEIS NO MT5")
    print("=" * 80)
    
    if not mt5.initialize():
        print("❌ ERRO: Não foi possível inicializar MetaTrader 5")
        return []
    
    # Buscar todos os símbolos
    symbols = mt5.symbols_get()
    
    # Filtrar criptomoedas (geralmente contêm BTC, ETH, ou CRYPTO no nome)
    crypto_keywords = ['BTC', 'ETH', 'CRYPTO', 'CRYPT', 'BITCOIN', 'ETHEREUM', 'LTC', 'XRP', 'ADA', 'SOL', 'DOT']
    crypto_symbols = []
    
    for symbol in symbols:
        name = symbol.name.upper()
        for keyword in crypto_keywords:
            if keyword in name:
                # Verificar se o símbolo está ativo
                if symbol.visible:
                    tick = mt5.symbol_info_tick(symbol.name)
                    if tick:
                        # Calcular spread em pips
                        spread = (tick.ask - tick.bid) / symbol.point if symbol.point > 0 else 0
                        spread_pips = spread / (10 ** (-symbol.digits)) if symbol.digits > 0 else spread
                        
                        crypto_symbols.append({
                            'name': symbol.name,
                            'description': symbol.description,
                            'digits': symbol.digits,
                            'point': symbol.point,
                            'spread_pips': spread_pips,
                            'bid': tick.bid,
                            'ask': tick.ask,
                            'volume_min': symbol.volume_min,
                            'volume_max': symbol.volume_max,
                            'volume_step': symbol.volume_step
                        })
                break
    
    # Remover duplicatas e ordenar por nome
    seen = set()
    unique_crypto = []
    for crypto in crypto_symbols:
        if crypto['name'] not in seen:
            seen.add(crypto['name'])
            unique_crypto.append(crypto)
    
    unique_crypto.sort(key=lambda x: x['name'])
    
    mt5.shutdown()
    return unique_crypto

def sugerir_configuracao(crypto_symbols):
    """Sugere configuração para operação em cripto"""
    print("\n" + "=" * 80)
    print("SUGESTÃO DE CONFIGURAÇÃO PARA CRIPTOMOEDAS")
    print("=" * 80)
    
    if not crypto_symbols:
        print("❌ Nenhuma criptomoeda encontrada")
        return
    
    print(f"\n✅ {len(crypto_symbols)} criptomoeda(s) disponível(eis):\n")
    
    # Mostrar principais criptomoedas
    principais = ['BTCUSD', 'ETHUSD', 'BTC', 'ETH', 'BITCOIN', 'ETHEREUM']
    sugeridos = []
    
    for crypto in crypto_symbols:
        name = crypto['name'].upper()
        is_principal = any(p in name for p in principais)
        
        status = "⭐ PRINCIPAL" if is_principal else "   "
        print(f"{status} {crypto['name']:20s} | Spread: {crypto['spread_pips']:8.2f} pips | "
              f"Bid: {crypto['bid']:12.2f} | Desc: {crypto['description'][:40]}")
        
        if is_principal and len(sugeridos) < 5:
            sugeridos.append(crypto['name'])
    
    # Se não encontrou principais, pegar as primeiras 5
    if not sugeridos:
        sugeridos = [c['name'] for c in crypto_symbols[:5]]
    
    print(f"\n📊 SUGESTÃO DE SÍMBOLOS PARA ADICIONAR AO CONFIG:")
    print(f"   {sugeridos}")
    
    # Sugerir limites de spread para cripto
    print(f"\n📊 SUGESTÃO DE LIMITES DE SPREAD (MAX_SPREAD_PIPS):")
    max_spreads = {}
    for crypto in sugeridos:
        crypto_info = next((c for c in crypto_symbols if c['name'] == crypto), None)
        if crypto_info:
            # Sugerir limite de 2x o spread atual (com mínimo de 50 pips)
            suggested_spread = max(50, crypto_info['spread_pips'] * 2)
            max_spreads[crypto] = round(suggested_spread)
            print(f"   {crypto:20s}: {max_spreads[crypto]:6.0f} pips")
    
    # Gerar configuração JSON sugerida
    config_sugerida = {
        "TRADING_SYMBOLS": sugeridos,
        "MAX_SPREAD_PIPS": max_spreads,
        "OBSERVACAO": "Configuração sugerida para operação em criptomoedas no final de semana"
    }
    
    config_path = Path(__file__).parent.parent.parent / "config_crypto_sugestao.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_sugerida, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Configuração sugerida salva em: {config_path}")
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   1. Revisar os símbolos sugeridos antes de adicionar ao config.json")
    print(f"   2. Verificar se os símbolos estão disponíveis na sua conta MT5")
    print(f"   3. Ajustar MAX_SPREAD_PIPS conforme necessário")
    print(f"   4. Criptomoedas têm spreads maiores que Forex - ajustar limites adequadamente")
    print(f"   5. Considerar horários de mercado (cripto é 24/7, mas liquidez varia)")

if __name__ == "__main__":
    print("\n🔍 Verificando criptomoedas disponíveis no MT5...\n")
    crypto_symbols = verificar_cripto_disponiveis()
    
    if crypto_symbols:
        sugerir_configuracao(crypto_symbols)
    else:
        print("\n⚠️  AVISO: Nenhuma criptomoeda encontrada.")
        print("   Possíveis causas:")
        print("   - Conta MT5 não tem acesso a criptomoedas")
        print("   - Broker não oferece criptomoedas")
        print("   - Símbolos não estão visíveis no Market Watch")
        print("\n   Ação recomendada:")
        print("   - Verificar no MT5 se há criptomoedas disponíveis")
        print("   - Adicionar símbolos ao Market Watch no MT5")
        print("   - Verificar configurações da conta com o broker")

