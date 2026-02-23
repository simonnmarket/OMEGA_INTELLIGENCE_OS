#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE INTELIGÊNCIA DE MERCADO - PROMETHEUS v5.0
Sincronização com a realidade do mercado em tempo real
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

def get_real_time_market_state(symbols: List[str]) -> List[Dict]:
    """
    Obtém o estado real do mercado para cada símbolo.
    Retorna lista de dicionários com informações de negociabilidade.
    """
    if not mt5.initialize():
        return []
    
    market_state = []
    
    for symbol in symbols:
        try:
            if not mt5.symbol_select(symbol, True):
                market_state.append({
                    'symbol': symbol,
                    'is_tradable': False,
                    'status': 'UNAVAILABLE',
                    'spread_points': float('inf'),
                    'tick_volume': 0,
                    'reason': 'Symbol not available'
                })
                continue
            
            tick = mt5.symbol_info_tick(symbol)
            symbol_info = mt5.symbol_info(symbol)
            
            if tick is None or symbol_info is None:
                market_state.append({
                    'symbol': symbol,
                    'is_tradable': False,
                    'status': 'UNAVAILABLE',
                    'spread_points': float('inf'),
                    'tick_volume': 0,
                    'reason': 'Tick or symbol info unavailable'
                })
                continue
            
            point = symbol_info.point
            if point <= 0:
                continue
            
            spread = tick.ask - tick.bid
            spread_points = spread / point if point != 0 else float('inf')
            tick_volume = tick.volume if hasattr(tick, 'volume') else 0
            
            # Critérios de Negociabilidade - MUITO MAIS PERMISSIVOS
            # Usar limites maiores para diferentes tipos de ativos
            max_spread = (
                2000 if 'BTC' in symbol or 'ETH' in symbol else
                1500 if 'CRYPTO' in symbol.upper() else
                500 if 'XAU' in symbol or 'GOLD' in symbol else
                50 if 'US' in symbol or 'SPX' in symbol or 'NAS' in symbol else
                20  # Default para forex
            )
            # Remover requisito de volume mínimo (muitos ativos não reportam corretamente)
            min_volume = 0  # Sempre aceitar qualquer volume (incluindo 0)
            
            is_tradable = spread_points < max_spread and spread_points != float('inf')
            
            if not is_tradable:
                status = 'CLOSED'
            elif spread_points < (max_spread * 0.5):
                status = 'LIQUIDITY_HIGH'
            else:
                status = 'LIQUIDITY_LOW'
            
            market_state.append({
                'symbol': symbol,
                'is_tradable': is_tradable,
                'status': status,
                'spread_points': spread_points,
                'tick_volume': tick_volume,
                'ask': tick.ask,
                'bid': tick.bid,
                'point': point
            })
            
        except Exception as e:
            market_state.append({
                'symbol': symbol,
                'is_tradable': False,
                'status': 'ERROR',
                'spread_points': float('inf'),
                'tick_volume': 0,
                'reason': str(e)
            })
            continue
    
    return market_state

def filter_tradable_assets(market_state: List[Dict]) -> List[str]:
    """Filtra apenas os ativos que estão negociáveis no momento"""
    return [asset['symbol'] for asset in market_state if asset['is_tradable']]

def get_market_status(symbol: str, market_state: List[Dict]) -> Optional[Dict]:
    """Retorna o status de mercado de um símbolo específico"""
    for asset in market_state:
        if asset['symbol'] == symbol:
            return asset
    return None

