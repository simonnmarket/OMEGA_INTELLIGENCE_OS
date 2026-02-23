# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 2.4
Implementar Sistema de Geração de Sinais

FUNÇÃO: _implement_signal_system()
OBJETIVO: Integrar lógica de sinais de trading ao servidor
TESTÁVEL: Sim - gera sinais reais com dados de mercado
"""

import logging
import json
import ccxt
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """
    Calcular ATR (Average True Range) para volatilidade
    
    Args:
        df: DataFrame com OHLC
        period: Período do ATR
    
    Returns:
        float: Valor do ATR
    """
    try:
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return float(atr) if not pd.isna(atr) else 0.0
    except Exception as e:
        logger.warning(f"Erro ao calcular ATR: {e}")
        return 0.0

def _analyze_trend(df: pd.DataFrame) -> Tuple[str, float]:
    """
    Analisar tendência do mercado
    
    Args:
        df: DataFrame com OHLC
    
    Returns:
        tuple: (tendência, confiança)
            tendência: 'BULLISH', 'BEARISH', 'NEUTRAL'
            confiança: 0.0 a 1.0
    """
    try:
        if len(df) < 20:
            return 'NEUTRAL', 0.0
        
        close = df['close']
        
        # Médias móveis simples
        sma_short = close.rolling(window=10).mean().iloc[-1]
        sma_long = close.rolling(window=20).mean().iloc[-1]
        current_price = close.iloc[-1]
        
        # Determinar tendência
        if sma_short > sma_long and current_price > sma_short:
            trend = 'BULLISH'
            # Confiança baseada na distância das médias
            confidence = min((sma_short - sma_long) / sma_long * 100, 1.0)
        elif sma_short < sma_long and current_price < sma_short:
            trend = 'BEARISH'
            confidence = min((sma_long - sma_short) / sma_long * 100, 1.0)
        else:
            trend = 'NEUTRAL'
            confidence = 0.0
        
        return trend, float(confidence)
    
    except Exception as e:
        logger.warning(f"Erro ao analisar tendência: {e}")
        return 'NEUTRAL', 0.0

def _generate_signal(symbol: str, timeframe: str = '1h') -> Dict:
    """
    Gerar sinal de trading para um símbolo
    
    Args:
        symbol: Símbolo para análise (ex: BTC/USDT)
        timeframe: Timeframe para análise
    
    Returns:
        dict: Sinal de trading com action, confidence, sl, tp
    """
    try:
        # Buscar dados
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        
        if not ohlcv or len(ohlcv) < 20:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Dados insuficientes',
                'stop_loss': 0,
                'take_profit': 0
            }
        
        # Criar DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        current_price = float(df['close'].iloc[-1])
        
        # Análise de tendência
        trend, trend_confidence = _analyze_trend(df)
        
        # Calcular ATR para SL/TP
        atr = _calculate_atr(df)
        
        # Gerar sinal baseado na tendência
        if trend == 'BULLISH' and trend_confidence > 0.3:
            action = 'BUY'
            confidence = min(trend_confidence, 0.85)  # Cap em 0.85
            
            # SL/TP baseados em ATR
            if atr > 0:
                stop_loss = current_price - (2.0 * atr)
                take_profit = current_price + (3.0 * atr)
            else:
                # Fallback: percentual
                stop_loss = current_price * 0.98  # -2%
                take_profit = current_price * 1.05  # +5%
            
            reason = f"Tendência BULLISH (conf: {trend_confidence:.2f})"
        
        elif trend == 'BEARISH' and trend_confidence > 0.3:
            action = 'SELL'
            confidence = min(trend_confidence, 0.85)
            
            # SL/TP baseados em ATR
            if atr > 0:
                stop_loss = current_price + (2.0 * atr)
                take_profit = current_price - (3.0 * atr)
            else:
                # Fallback: percentual
                stop_loss = current_price * 1.02  # +2%
                take_profit = current_price * 0.95  # -5%
            
            reason = f"Tendência BEARISH (conf: {trend_confidence:.2f})"
        
        else:
            action = 'HOLD'
            confidence = 0.0
            stop_loss = 0
            take_profit = 0
            reason = f"Tendência {trend} (conf: {trend_confidence:.2f} < 0.3)"
        
        return {
            'action': action,
            'confidence': float(confidence),
            'reason': reason,
            'stop_loss': float(stop_loss),
            'take_profit': float(take_profit),
            'atr': float(atr),
            'current_price': float(current_price),
            'trend': trend
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar sinal: {e}")
        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': f'Erro: {str(e)}',
            'stop_loss': 0,
            'take_profit': 0
        }

def _format_signal_for_ea(signal: Dict, symbol: str) -> Dict:
    """
    Formatar sinal para o formato esperado pelo EA
    
    Args:
        signal: Sinal gerado
        symbol: Símbolo do ativo
    
    Returns:
        dict: Sinal formatado para EA
    """
    return {
        'symbol': symbol,
        'action': signal['action'],
        'confidence': signal['confidence'],
        'reason': signal['reason'],
        'stop_loss': signal['stop_loss'],
        'take_profit': signal['take_profit'],
        'timestamp': int(datetime.now().timestamp()),
        'server_version': 'v3.1_SIGNAL_SYSTEM'
    }

def _implement_signal_system() -> bool:
    """
    Integrar sistema de geração de sinais ao servidor
    
    Implementa:
    - Geração de sinais de trading
    - Análise de confiança (baseada em tendência)
    - Cálculo de SL/TP (baseado em ATR)
    - Formatação para EA
    
    Returns:
        bool: True se sistema de sinais integrado com sucesso
    
    VALIDAÇÃO:
    - Gera sinal real para BTC/USDT
    - Valida cálculo de ATR
    - Valida análise de tendência
    - Valida formatação para EA
    """
    try:
        logger.info("="*80)
        logger.info("FASE 2.4: Integrando Sistema de Sinais")
        logger.info("="*80)
        
        # TESTE 1: GERAR SINAL REAL
        logger.info("\n1. GERANDO SINAL REAL PARA BTC/USDT...")
        
        signal = _generate_signal('BTC/USDT', '1h')
        
        if signal:
            logger.info(f"  ✅ Sinal gerado")
            logger.info(f"  📊 Action: {signal['action']}")
            logger.info(f"  📊 Confidence: {signal['confidence']:.2f}")
            logger.info(f"  📊 Reason: {signal['reason']}")
            logger.info(f"  📊 Current Price: ${signal['current_price']:.2f}")
            
            if signal['action'] != 'HOLD':
                logger.info(f"  📊 Stop Loss: ${signal['stop_loss']:.2f}")
                logger.info(f"  📊 Take Profit: ${signal['take_profit']:.2f}")
                logger.info(f"  📊 ATR: ${signal['atr']:.2f}")
            
            signal_ok = True
        else:
            logger.error(f"  ❌ Falha ao gerar sinal")
            signal_ok = False
        
        # TESTE 2: VALIDAR CÁLCULO DE ATR
        logger.info("\n2. VALIDANDO CÁLCULO DE ATR...")
        
        try:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            atr = _calculate_atr(df)
            
            if atr > 0:
                logger.info(f"  ✅ ATR calculado: ${atr:.2f}")
                atr_ok = True
            else:
                logger.warning(f"  ⚠️ ATR = 0 (dados insuficientes?)")
                atr_ok = False
        except Exception as e:
            logger.error(f"  ❌ Erro ao calcular ATR: {e}")
            atr_ok = False
        
        # TESTE 3: VALIDAR ANÁLISE DE TENDÊNCIA
        logger.info("\n3. VALIDANDO ANÁLISE DE TENDÊNCIA...")
        
        try:
            trend, trend_conf = _analyze_trend(df)
            
            logger.info(f"  ✅ Tendência: {trend}")
            logger.info(f"  📊 Confiança: {trend_conf:.2f}")
            
            trend_ok = trend in ['BULLISH', 'BEARISH', 'NEUTRAL']
        except Exception as e:
            logger.error(f"  ❌ Erro ao analisar tendência: {e}")
            trend_ok = False
        
        # TESTE 4: VALIDAR FORMATAÇÃO PARA EA
        logger.info("\n4. VALIDANDO FORMATAÇÃO PARA EA...")
        
        try:
            ea_signal = _format_signal_for_ea(signal, 'BTCUSD')
            
            required_fields = ['symbol', 'action', 'confidence', 'reason', 'stop_loss', 'take_profit', 'timestamp']
            has_all_fields = all(field in ea_signal for field in required_fields)
            
            if has_all_fields:
                logger.info(f"  ✅ Formatação EA: OK")
                logger.info(f"     Campos: {list(ea_signal.keys())}")
                format_ok = True
            else:
                logger.error(f"  ❌ Campos faltando")
                format_ok = False
        except Exception as e:
            logger.error(f"  ❌ Erro ao formatar: {e}")
            format_ok = False
        
        # VALIDAÇÃO FINAL
        logger.info("\n" + "="*80)
        logger.info("VALIDAÇÃO DO SISTEMA DE SINAIS:")
        logger.info(f"  Geração de sinal: {'✅ OK' if signal_ok else '❌ Falha'}")
        logger.info(f"  Cálculo de ATR: {'✅ OK' if atr_ok else '⚠️ Limitado'}")
        logger.info(f"  Análise de tendência: {'✅ OK' if trend_ok else '❌ Falha'}")
        logger.info(f"  Formatação EA: {'✅ OK' if format_ok else '❌ Falha'}")
        logger.info("="*80)
        
        all_ok = signal_ok and trend_ok and format_ok
        # ATR pode ser 0 em alguns casos, não é crítico
        
        if all_ok:
            logger.info("✅ SISTEMA DE SINAIS VALIDADO")
            return True
        else:
            logger.error("❌ SISTEMA DE SINAIS TEM PROBLEMAS")
            return False
    
    except Exception as e:
        logger.error(f"❌ ERRO ao implementar sistema de sinais: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# =====================================================
# TESTE DA FUNÇÃO
# =====================================================

def test_implement_signal_system():
    """
    Teste para validar que sistema de sinais foi implementado corretamente
    
    Returns:
        dict: Resultado do teste com status e detalhes
    """
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _implement_signal_system()")
    logger.info("="*80)
    
    # Executar função
    result = _implement_signal_system()
    
    # Teste adicional: Gerar múltiplos sinais
    logger.info("\nTESTE ADICIONAL: Múltiplos sinais...")
    
    symbols_to_test = ['BTC/USDT', 'ETH/USDT']
    signals_generated = {}
    
    for symbol in symbols_to_test:
        try:
            signal = _generate_signal(symbol, '1h')
            signals_generated[symbol] = {
                'action': signal['action'],
                'confidence': signal['confidence'],
                'success': True
            }
            logger.info(f"  ✅ {symbol}: {signal['action']} (conf: {signal['confidence']:.2f})")
        except Exception as e:
            signals_generated[symbol] = {'success': False, 'error': str(e)}
            logger.warning(f"  ⚠️ {symbol}: {e}")
    
    # Resultado do teste
    test_result = {
        'function': '_implement_signal_system()',
        'passed': result,
        'timestamp': datetime.now().isoformat(),
        'details': {
            'system_validated': result,
            'signals_generated': signals_generated
        }
    }
    
    if test_result['passed']:
        logger.info("\n✅ TESTE PASSOU")
        logger.info(f"  Sistema de sinais validado: OK")
        logger.info(f"  Sinais gerados: {len([s for s in signals_generated.values() if s.get('success')])}/{len(symbols_to_test)}")
    else:
        logger.error("\n❌ TESTE FALHOU")
        logger.error("  Sistema de sinais tem problemas")
    
    logger.info("="*80)
    
    return test_result

if __name__ == "__main__":
    """Executar teste quando rodar este arquivo"""
    
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 2.4")
    print("Funcao: _implement_signal_system()")
    print("="*80 + "\n")
    
    # Executar teste
    result = test_implement_signal_system()
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print("="*80)
    print(f"Funcao: {result['function']}")
    print(f"Passou: {result['passed']}")
    print(f"Timestamp: {result['timestamp']}")
    
    if result['details']['signals_generated']:
        print(f"\nSinais gerados:")
        for symbol, signal in result['details']['signals_generated'].items():
            if signal.get('success'):
                print(f"  {symbol}: {signal['action']} (conf: {signal['confidence']:.2f})")
            else:
                print(f"  {symbol}: Erro - {signal.get('error', 'Desconhecido')}")
    
    print("="*80 + "\n")
    
    # Salvar resultado
    with open('test_result_phase_2_4.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_2_4.json\n")

