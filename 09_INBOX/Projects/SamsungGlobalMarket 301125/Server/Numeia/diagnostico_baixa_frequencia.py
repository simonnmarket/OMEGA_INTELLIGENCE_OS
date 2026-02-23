#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO: Por que apenas 5 operações em 8+ horas?

Analisa os logs do Prometheus v6.0 para identificar filtros que estão bloqueando sinais.
"""

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG_FILE = "prometheus_master_log_v6.0.jsonl"

def analisar_logs():
    """Analisa os logs para identificar padrões de bloqueio"""
    
    if not Path(LOG_FILE).exists():
        print(f"❌ Arquivo de log não encontrado: {LOG_FILE}")
        return
    
    bloqueios = {
        "strategic_block_sell": 0,  # Bloqueio estratégico CEO
        "regime_check": {"TENDÊNCIA": 0, "RUIDO": 0},
        "rsi_filter_failed": 0,
        "volume_filter_failed": 0,
        "trend_conflict": 0,
        "outside_trading_hours": 0,
        "forbidden_day": 0,
        "valid_signal_generated": 0,
        "order_executed": 0
    }
    
    adx_values = []
    timestamps = []
    
    print("="*80)
    print("DIAGNÓSTICO: ANÁLISE DE BLOQUEIOS DE SINAIS")
    print("="*80)
    print()
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # Parse do log estruturado
                if line.strip():
                    # Extrair timestamp e mensagem JSON
                    parts = line.split(' - ', 2)
                    if len(parts) >= 3:
                        timestamp = parts[0]
                        level = parts[1]
                        json_str = parts[2]
                        
                        try:
                            data = json.loads(json_str)
                            event = data.get("event", "")
                            
                            # Contar eventos
                            if event == "strategic_block_sell":
                                bloqueios["strategic_block_sell"] += 1
                                timestamps.append(timestamp)
                                
                            elif event == "regime_check":
                                regime = data.get("regime", "")
                                if regime == "TENDÊNCIA":
                                    bloqueios["regime_check"]["TENDÊNCIA"] += 1
                                elif regime == "RUIDO":
                                    bloqueios["regime_check"]["RUIDO"] += 1
                                
                                adx = data.get("adx", 0)
                                threshold = data.get("threshold", 0)
                                if adx > 0:
                                    adx_values.append({
                                        "adx": adx,
                                        "threshold": threshold,
                                        "symbol": data.get("symbol", ""),
                                        "timestamp": timestamp
                                    })
                                    
                            elif event == "rsi_filter_failed":
                                bloqueios["rsi_filter_failed"] += 1
                                
                            elif event == "volume_filter_failed":
                                bloqueios["volume_filter_failed"] += 1
                                
                            elif event == "trend_conflict":
                                bloqueios["trend_conflict"] += 1
                                
                            elif event == "outside_trading_hours":
                                bloqueios["outside_trading_hours"] += 1
                                
                            elif event == "forbidden_day":
                                bloqueios["forbidden_day"] += 1
                                
                            elif event == "valid_signal_generated":
                                bloqueios["valid_signal_generated"] += 1
                                
                            elif event == "order_executed":
                                bloqueios["order_executed"] += 1
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                continue
    
    # RELATÓRIO
    print("📊 ESTATÍSTICAS DE BLOQUEIOS:")
    print("-" * 80)
    print(f"🚫 Bloqueio Estratégico (SELL bloqueado): {bloqueios['strategic_block_sell']}")
    print(f"🎯 Regime Check - TENDÊNCIA: {bloqueios['regime_check']['TENDÊNCIA']}")
    print(f"🎯 Regime Check - RUIDO: {bloqueios['regime_check']['RUIDO']}")
    print(f"📉 RSI Filter Failed: {bloqueios['rsi_filter_failed']}")
    print(f"📊 Volume Filter Failed: {bloqueios['volume_filter_failed']}")
    print(f"⚔️  Trend Conflict (H4/H1): {bloqueios['trend_conflict']}")
    print(f"⏰ Outside Trading Hours: {bloqueios['outside_trading_hours']}")
    print(f"🚫 Forbidden Day: {bloqueios['forbidden_day']}")
    print()
    print("✅ SINAIS VÁLIDOS GERADOS:", bloqueios['valid_signal_generated'])
    print("✅ ORDENS EXECUTADAS:", bloqueios['order_executed'])
    print()
    
    # ANÁLISE DE ADX
    if adx_values:
        print("📈 ANÁLISE DE ADX:")
        print("-" * 80)
        adx_avg = sum(a["adx"] for a in adx_values) / len(adx_values)
        threshold_avg = sum(a["threshold"] for a in adx_values) / len(adx_values)
        
        abaixo_threshold = sum(1 for a in adx_values if a["adx"] < a["threshold"])
        acima_threshold = sum(1 for a in adx_values if a["adx"] >= a["threshold"])
        
        print(f"ADX Médio: {adx_avg:.1f}")
        print(f"Threshold Médio: {threshold_avg:.1f}")
        print(f"ADX < Threshold: {abaixo_threshold} ({abaixo_threshold/len(adx_values)*100:.1f}%)")
        print(f"ADX >= Threshold: {acima_threshold} ({acima_threshold/len(adx_values)*100:.1f}%)")
        print()
        
        # Mostrar exemplos de ADX baixo
        adx_baixos = sorted([a for a in adx_values if a["adx"] < a["threshold"]], 
                           key=lambda x: x["adx"])[:10]
        if adx_baixos:
            print("🔍 TOP 10 CASOS DE ADX ABAIXO DO THRESHOLD:")
            for a in adx_baixos:
                print(f"  {a['symbol']}: ADX={a['adx']:.1f} < T={a['threshold']:.1f} ({a['timestamp']})")
            print()
    
    # DIAGNÓSTICO FINAL
    print("="*80)
    print("🔍 DIAGNÓSTICO FINAL:")
    print("="*80)
    
    total_bloqueios = (
        bloqueios["strategic_block_sell"] +
        bloqueios["regime_check"]["RUIDO"] +
        bloqueios["rsi_filter_failed"] +
        bloqueios["volume_filter_failed"] +
        bloqueios["trend_conflict"] +
        bloqueios["outside_trading_hours"] +
        bloqueios["forbidden_day"]
    )
    
    print(f"Total de bloqueios detectados: {total_bloqueios}")
    print(f"Sinais válidos gerados: {bloqueios['valid_signal_generated']}")
    print(f"Ordens executadas: {bloqueios['order_executed']}")
    print()
    
    if bloqueios["strategic_block_sell"] > 0:
        print("⚠️  BLOQUEIO ESTRATÉGICO ATIVO:")
        print(f"   {bloqueios['strategic_block_sell']} sinais SELL foram bloqueados (conforme diretiva CEO)")
        print("   ✅ Isso é ESPERADO e CORRETO - apenas BUY permitido")
        print()
    
    if bloqueios["regime_check"]["RUIDO"] > bloqueios["regime_check"]["TENDÊNCIA"]:
        print("⚠️  PROBLEMA PRINCIPAL: ADX BAIXO (Regime de RUIDO)")
        print(f"   {bloqueios['regime_check']['RUIDO']} casos em RUIDO vs {bloqueios['regime_check']['TENDÊNCIA']} em TENDÊNCIA")
        print("   💡 SUGESTÃO: O threshold de ADX pode estar muito alto, ou o mercado está realmente sem tendência")
        print()
    
    if bloqueios["rsi_filter_failed"] > bloqueios["valid_signal_generated"] * 2:
        print("⚠️  FILTRO RSI MUITO RESTRITIVO:")
        print(f"   {bloqueios['rsi_filter_failed']} bloqueios por RSI")
        print("   💡 SUGESTÃO: Considerar ampliar a faixa de RSI pullback")
        print()
    
    if bloqueios["volume_filter_failed"] > bloqueios["valid_signal_generated"] * 2:
        print("⚠️  FILTRO DE VOLUME MUITO RESTRITIVO:")
        print(f"   {bloqueios['volume_filter_failed']} bloqueios por volume")
        print("   💡 SUGESTÃO: Considerar reduzir o threshold de volume (atualmente 80% da média)")
        print()
    
    if bloqueios["trend_conflict"] > 0:
        print(f"⚠️  CONFLITOS DE TENDÊNCIA: {bloqueios['trend_conflict']} casos")
        print("   H4 e H1 não estão alinhados - isso é normal em mercados laterais")
        print()
    
    if bloqueios["outside_trading_hours"] > 0:
        print(f"⚠️  FORA DO HORÁRIO DE TRADING: {bloqueios['outside_trading_hours']} casos")
        print("   Sistema está respeitando janelas de liquidez")
        print()
    
    print("="*80)
    print("✅ Análise concluída!")
    print("="*80)

if __name__ == "__main__":
    analisar_logs()

