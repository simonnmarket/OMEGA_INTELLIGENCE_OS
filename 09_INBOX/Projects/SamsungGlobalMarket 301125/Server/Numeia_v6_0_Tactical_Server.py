# -*- coding: utf-8 -*-
"""
================================================================================
SERVIDOR NUMEIA v6.0 - TACTICAL WAR ROOM
================================================================================

FILOSOFIA: "Agressão ao Mercado - Testar TUDO"
OBJETIVO: Executar múltiplas estratégias táticas em paralelo
PROTOCOLO: Experimento de Refutação Rápida
COMUNICAÇÃO: File-based (JSON) com EA

ARQUITETURA:
  Python War Room (este servidor)
    ├─ Strategy 1: Momentum Scanner
    ├─ Strategy 2: Breakout Hunter
    ├─ Strategy 3: Mean Reversion (Forex)
    ├─ Strategy 4: Volatility Arbitrage
    └─ Strategy 5: Regime Adaptive
    
    ↓ Sinais consolidados
    
  EA MT5 (Executor Tático)
    └─ Recebe sinais via TacticalSignals.json

================================================================================
"""

import os
import sys
import json
import time
import logging
import importlib.util
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

try:
    import MetaTrader5 as mt5  # type: ignore
except ImportError:
    mt5 = None

# Setup paths
current_dir = Path(__file__).parent
root_dir = current_dir.parent
core_dir = current_dir.parent / 'Core'
strategies_dir = core_dir / 'Strategies' / 'Tactical'

sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(strategies_dir))

from Core.DataProviders.DataHubIntraday import DataHubIntraday, MarketDataBundle
from Core.Analytics.RegimeDetector import RegimeDetector, RegimeAssessment
from Core.Calendars import MarketSessionManager, MarketSessionMode
from Core.Strategies.Tactical.MomentumScanner_Aggressive import MomentumScannerAggressive
from Core.Strategies.Tactical.BreakoutHunter_Aggressive import BreakoutHunterAggressive
from Core.Strategies.Tactical.FXMeanReversion_Aggressive import FXMeanReversionAggressive

# Logging
log_file = current_dir / 'Numeia_v6_0_Tactical.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pasta MT5
MT5_PATH = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
SIGNALS_FILE = MT5_PATH / 'TacticalSignals.json'  # Arquivo que EA lê

logger.info("="*80)
logger.info("NUMEIA v6.0 - TACTICAL WAR ROOM SERVER")
logger.info("="*80)
logger.info(f"MT5 Path: {MT5_PATH}")
logger.info(f"Signals File: {SIGNALS_FILE}")
logger.info("="*80)

class NumeiaV6TacticalServer:
    """
    Servidor tático agressivo para Numeia v6.0.
    
    Executa múltiplas estratégias em paralelo e consolida sinais.
    """
    
    def __init__(self):
        self.strategies = {}
        self.last_scan_time = None
        self.scan_interval = 300  # 5 minutos
        self.total_signals_generated = 0
        self.base_min_confidence = 0.50
        self.last_regime_assessment: Optional[RegimeAssessment] = None
        self.last_data_bundles: Dict[str, MarketDataBundle] = {}

        # Universo de ativos (após filtro Market Watch) + calendário
        self.session_manager = MarketSessionManager()
        self.market_watch_symbols = self._load_market_watch_whitelist()
        self.universe_full = self._build_filtered_universe()
        self.berlin_tz = self.session_manager.timezone

        current_dt = datetime.now(self.session_manager.timezone)
        self.active_mode = self.session_manager.get_active_mode(current_dt)
        self.universe = self.session_manager.filter_universe(self.universe_full, self.active_mode)
        if not self.universe:
            self.universe = self.session_manager.filter_universe(
                self.universe_full,
                MarketSessionMode.CRYPTO_ONLY,
            )
        logger.info("🗓️ Modo inicial: %s", self.session_manager.describe_mode(self.active_mode))
        
        # Importar estratégias
        try:
            self.strategies['momentum'] = MomentumScannerAggressive(self.universe_full)
            self.strategies['breakout'] = BreakoutHunterAggressive()
            fx_symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
            self.strategies['mean_reversion'] = FXMeanReversionAggressive(fx_symbols)
            logger.info("✅ Estratégias carregadas: %s", ", ".join(self.strategies.keys()))
        except Exception as e:
            logger.error(f"❌ Erro ao carregar estratégias: {e}")

        self.data_hub = DataHubIntraday(self.universe_full, bars_per_timeframe=250)
        self.regime_detector = RegimeDetector()

        logger.info("✅ Universo base: %d ativos", len(self.universe_full))
        logger.info("   Universo ativo inicial: %d ativos", len(self.universe))
        logger.info("="*80)
    
    def _load_market_watch_whitelist(self) -> List[str]:
        """
        Carrega a lista de símbolos disponíveis a partir do arquivo exportado
        do Market Watch da Hantec.
        """
        csv_path = Path.home() / 'Documents' / 'Market Watch 20251109 175450.csv'
        if not csv_path.exists():
            logger.warning("⚠️ Market Watch CSV não encontrado: %s", csv_path)
            return []

        try:
            df = pd.read_csv(csv_path, sep=';', encoding='utf-16')
            if 'Symbol' not in df.columns:
                logger.warning("⚠️ Coluna 'Symbol' ausente no Market Watch CSV")
                return []

            symbols = (
                df['Symbol']
                .dropna()
                .astype(str)
                .apply(lambda s: s.strip())
            )
            whitelist = [s for s in symbols if s]

            logger.info("✅ Market Watch: %d símbolos carregados", len(whitelist))
            return whitelist
        except Exception as e:
            logger.warning("⚠️ Falha ao ler Market Watch CSV: %s", e)
            return []

    def _build_filtered_universe(self) -> List[str]:
        """
        Constrói o universo final considerando apenas símbolos disponíveis
        na corretora (Market Watch).
        """
        desired_priority = [
            # Índices
            'US500', 'US30', 'US100', 'US2000', 'GER40', 'UK100', 'FR40', 'EU50',
            # Commodities / Energias
            'XAUUSD', 'XAGUSD', 'UKOIL+', 'USOIL+', 'XAUEUR', 'XAUCHF',
            # Forex majors
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD',
            'NZDUSD', 'EURJPY', 'EURGBP', 'GBPJPY', 'USDSEK', 'USDCNH',
            # Cripto principais
            'BTCUSD', 'ETHUSD',
        ]

        if not self.market_watch_symbols:
            logger.warning("⚠️ Usando universo mínimo (fallback)")
            fallback = ['US500', 'GER40', 'UK100', 'XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
            return fallback

        allowed_set = set(self.market_watch_symbols)
        filtered = [sym for sym in desired_priority if sym in allowed_set]

        missing = [sym for sym in desired_priority if sym not in allowed_set]
        if missing:
            logger.info("ℹ️ Símbolos filtrados por ausência no Market Watch: %s", ", ".join(missing))

        if not filtered:
            logger.warning("⚠️ Nenhum símbolo desejado encontrado; usando fallback mínimo")
            return ['US500', 'XAUUSD', 'EURUSD']

        logger.info("✅ Universo filtrado (Hantec): %s", ", ".join(filtered))
        return filtered

    def fetch_market_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Wrapper para compatibilidade com scanners legados."""

        bundles = self.data_hub.fetch_market_data()
        data_dict: Dict[str, pd.DataFrame] = {}

        for sym, bundle in bundles.items():
            origin = getattr(bundle, "fetched_from", "unknown")
            last_update = getattr(bundle, "last_update", datetime.utcnow())
            logger.info("📡 Origem dados %s → %s | última atualização: %s", sym, origin, last_update)

        for symbol in symbols:
            bundle = bundles.get(symbol)
            if bundle is None:
                continue
            df = bundle.timeframe_data.get('D1')
            if df is None or df.empty:
                df = bundle.timeframe_data.get('H1')
            if df is None or df.empty:
                continue
            data_dict[symbol] = df.copy()

        if not data_dict:
            logger.warning("⚠️ DataHub não retornou dados utilizáveis - fallback yfinance direto")
            data_dict = self._fetch_via_yfinance(symbols)

        self.last_data_bundles = bundles
        return data_dict
    
    def _fetch_via_yfinance(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Fallback: buscar dados via yfinance."""
        data_dict = {}
        
        # Mapear símbolos Hantec para yfinance
        symbol_map = {
            'US500': '^GSPC',  # S&P 500
            'GER40': '^GDAXI',  # DAX
            'UK100': '^FTSE',  # FTSE 100
            'XAUUSD': 'GC=F',  # Gold Futures
            'XAGUSD': 'SI=F',  # Silver Futures
            'UKOIL+': 'BZ=F',  # Brent Oil
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'JPY=X',
        }
        
        import yfinance as yf
        
        logger.info("📊 Buscando dados via yfinance (fallback)...")
        
        for symbol in symbols:
            try:
                # Mapear símbolo
                yf_symbol = symbol_map.get(symbol, symbol)
                
                # Baixar dados (6 meses)
                data = yf.download(yf_symbol, period='6mo', progress=False, interval='1d')
                
                if not data.empty and 'Close' in data.columns:
                    data_dict[symbol] = data
                    logger.debug(f"  ✅ {symbol}: {len(data)} dias")
                else:
                    logger.warning(f"  ⚠️ {symbol}: Dados vazios")
                    
            except Exception as e:
                logger.warning(f"  ❌ {symbol}: {e}")
        
        return data_dict
    
    def run_momentum_scanner(self, data_dict: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Executar Momentum Scanner e gerar sinais."""
        try:
            scanner = self.strategies['momentum']
            momentum_df = scanner.scan_universe(data_dict)
            
            if momentum_df.empty:
                return []
            
            signals = scanner.generate_signals(momentum_df)
            
            logger.info(f"  ✅ Momentum Scanner: {len(signals)} sinais")
            return signals
            
        except Exception as e:
            logger.error(f"  ❌ Erro no Momentum Scanner: {e}")
            return []

    def run_breakout_hunter(self, bundles: Dict[str, MarketDataBundle]) -> List[Dict]:
        try:
            scanner = self.strategies.get('breakout')
            if scanner is None:
                return []

            data_dict = {}
            for symbol, bundle in bundles.items():
                if bundle is None:
                    continue
                df = bundle.timeframe_data.get('D1')
                if df is None or df.empty:
                    continue
                data_dict[symbol] = df

            if not data_dict:
                return []

            signals = scanner.generate_signals(data_dict)
            logger.info(f"  ✅ Breakout Hunter: {len(signals)} sinais")
            return signals
        except Exception as e:
            logger.error(f"  ❌ Erro no Breakout Hunter: {e}")
            return []

    def run_mean_reversion(self, bundles: Dict[str, MarketDataBundle]) -> List[Dict]:
        try:
            scanner = self.strategies.get('mean_reversion')
            if scanner is None:
                return []

            data_dict = {}
            for symbol, bundle in bundles.items():
                if bundle is None:
                    continue
                df = bundle.timeframe_data.get('D1')
                if df is None or df.empty:
                    continue
                data_dict[symbol] = df

            if not data_dict:
                return []

            signals = scanner.generate_signals(data_dict)
            logger.info(f"  ✅ Mean Reversion FX: {len(signals)} sinais")
            return signals
        except Exception as e:
            logger.error(f"  ❌ Erro na Mean Reversion FX: {e}")
            return []

    def assess_regime(self, bundles: Dict[str, MarketDataBundle]) -> Optional[RegimeAssessment]:
        if not bundles:
            return None

        preferred_symbols = ['XAUUSD', 'US500', 'GER40'] + list(bundles.keys())

        for symbol in preferred_symbols:
            bundle = bundles.get(symbol)
            if bundle is None:
                continue

            df = bundle.timeframe_data.get('D1')
            if df is None or df.empty:
                df = bundle.timeframe_data.get('H1')
            if df is None or df.empty or 'Close' not in df.columns:
                continue

            try:
                assessment = self.regime_detector.assess(df['Close'])
                self.last_regime_assessment = assessment
                return assessment
            except Exception as exc:
                logger.warning(f"⚠️ Falha na avaliação de regime ({symbol}): {exc}")

        return self.last_regime_assessment
    
    def consolidate_signals(self, all_signals: List[List[Dict]]) -> List[Dict]:
        """
        Consolidar sinais de múltiplas estratégias.
        
        Lógica:
        - Se múltiplas estratégias geram sinal para mesmo ativo, priorizar maior confidence
        - Remover duplicatas
        - Limitar a top 20 sinais
        """
        consolidated = {}
        
        for strategy_signals in all_signals:
            for signal in strategy_signals:
                symbol = signal['symbol']
                
                # Se já existe sinal para este símbolo, manter o de maior confidence
                if symbol not in consolidated:
                    consolidated[symbol] = signal
                elif signal.get('confidence', 0) > consolidated[symbol].get('confidence', 0):
                    consolidated[symbol] = signal
        
        # Converter para lista e ordenar por confidence
        signals_list = list(consolidated.values())
        signals_list.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Limitar a top 20
        return signals_list[:20]
    
    def _compute_dynamic_min_confidence(self, adjuster: float) -> float:
        if adjuster <= 0:
            return self.base_min_confidence

        dynamic = self.base_min_confidence / adjuster
        return max(0.25, min(0.85, dynamic))

    def _rank_confidences(self, signals: List[Dict], min_confidence: float) -> None:
        if not signals:
            return

        scores = np.array([
            float(signal.get('score', signal.get('confidence', min_confidence)))
            for signal in signals
        ], dtype=float)

        order = np.argsort(scores)
        percent_ranks = np.empty_like(order, dtype=float)
        percent_ranks[order] = np.linspace(0.1, 1.0, len(signals))

        for idx, signal in enumerate(signals):
            base_conf = float(max(min_confidence, signal.get('confidence', min_confidence)))
            boosted = base_conf * (0.75 + 0.35 * percent_ranks[idx])
            signal['confidence'] = float(min(0.99, max(min_confidence, boosted)))

    def format_signals_for_ea(
        self,
        signals: List[Dict],
        min_confidence: float,
        assessment: Optional[RegimeAssessment],
        risk_multiplier: float,
    ) -> Dict:
        """
        Formatar sinais para o EA.
        
        Formato esperado pelo EA:
        {
            "timestamp": "2025-11-06T13:40:00",
            "signals": [
                {
                    "symbol": "XAUUSD",
                    "action": "BUY",
                    "entry_price": 4065.0,
                    "stop_loss": 3943.05,
                    "take_profit": 4390.2,
                    "confidence": 0.85,
                    "strategy": "momentum",
                    "reason": "..."
                }
            ]
        }
        """
        formatted = {
            'timestamp': datetime.now().isoformat(),
            'signals': [],
            'regime': assessment.label if assessment else 'UNKNOWN',
            'confidence_adjuster': assessment.confidence_adjuster if assessment else 1.0,
            'risk_multiplier': risk_multiplier,
            'min_confidence': float(min_confidence),
            'session_mode': self.active_mode.value,
        }

        tradable_cache: Dict[str, bool] = {}
        mt5_ready = False
        if mt5 is not None:
            try:
                mt5_ready = mt5.initialize()
            except Exception as exc:
                logger.warning("⚠️ Falha ao inicializar MT5 para checar ticks: %s", exc)

        for signal in signals:
            symbol = signal['symbol']
            signal_confidence = float(signal.get('confidence', min_confidence))
            if signal_confidence < min_confidence:
                logger.info("⚠️ Sinal descartado por confiança insuficiente: %s (%.2f)", symbol, signal_confidence)
                continue

            if mt5_ready:
                tradable = tradable_cache.get(symbol)
                if tradable is None:
                    tradable = self._is_symbol_tradable(symbol, self.active_mode)
                    tradable_cache[symbol] = tradable
                if not tradable:
                    logger.info("⏸️ %s descartado: última cotação fora da janela operacional (base Berlin)", symbol)
                    continue

            formatted_signal = {
                'symbol': symbol,
                'action': signal['action'],
                'entry_price': float(signal['entry_price']),
                'stop_loss': float(signal['stop_loss']),
                'take_profit': float(signal['take_profit']),
                'confidence': signal_confidence,
                'strategy': signal.get('strategy', 'unknown'),
                'reason': signal.get('reason', '')
            }
            formatted['signals'].append(formatted_signal)

        if mt5_ready:
            try:
                mt5.shutdown()
            except Exception:
                pass
        return formatted
    
    def _is_symbol_tradable(self, symbol: str, mode: MarketSessionMode) -> bool:
        """
        Verifica se o símbolo possui tick recente (base Berlin) para evitar envio
        de sinais quando o mercado estiver fechado ou dados desatualizados.
        """

        if not self.session_manager.is_symbol_allowed(symbol, mode):
            return False

        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.debug("   ⏸️ %s sem tick disponível no MT5", symbol)
                return False

            tick_time_utc = datetime.fromtimestamp(tick.time, tz=ZoneInfo("UTC"))
            tick_time_berlin = tick_time_utc.astimezone(self.berlin_tz)
            now_berlin = datetime.now(self.berlin_tz)

            age_seconds = (now_berlin - tick_time_berlin).total_seconds()
            if age_seconds < 0:
                age_seconds = 0.0

            max_allowed = self.session_manager.max_tick_age_for(symbol, mode)
            if max_allowed <= 0:
                logger.debug("   ⏸️ %s bloqueado pelo modo %s", symbol, mode.value)
                return False

            if age_seconds > max_allowed:
                logger.debug(
                    "   ⏸️ %s tick desatualizado há %.0f segundos (limite %d)",
                    symbol,
                    age_seconds,
                    max_allowed,
                )
                return False

            return True
        except Exception as exc:
            logger.warning("⚠️ Falha ao avaliar tick de %s: %s", symbol, exc)
            return True
    
    def save_signals(self, signals_dict: Dict):
        """Salvar sinais no arquivo JSON para o EA ler."""
        try:
            MT5_PATH.mkdir(parents=True, exist_ok=True)

            with open(SIGNALS_FILE, 'w', encoding='utf-8') as f:
                json.dump(signals_dict, f, indent=2, default=self._json_default)

            logger.info(f"✅ Sinais salvos: {SIGNALS_FILE}")
            logger.info(f"   Total: {len(signals_dict['signals'])} sinais")
            logger.info(
                "   Meta: regime=%s | min_conf=%.2f",
                signals_dict.get('regime'),
                signals_dict.get('min_confidence', self.base_min_confidence),
            )
            logger.info("   Sessão: %s", signals_dict.get('session_mode', 'unknown'))

        except Exception as e:
            logger.exception(f"❌ Erro ao salvar sinais: {e}")
    
    def run_scan_cycle(self):
        """Executar um ciclo completo de scan e geração de sinais."""
        logger.info("")
        logger.info("="*80)
        logger.info(f"🔍 CICLO DE SCAN #{self.total_signals_generated + 1}")
        logger.info("="*80)
        
        current_dt_cet = datetime.now(self.session_manager.timezone)
        mode = self.session_manager.get_active_mode(current_dt_cet)
        if mode != self.active_mode:
            logger.info(
                "🗓️ Mudança de modo: %s → %s",
                self.session_manager.describe_mode(self.active_mode),
                self.session_manager.describe_mode(mode),
            )
            self.active_mode = mode

        self.universe = self.session_manager.filter_universe(self.universe_full, self.active_mode)
        if not self.universe:
            logger.warning(
                "⚠️ Modo %s sem símbolos habilitados; aplicando fallback crypto",
                self.active_mode.value,
            )
            self.universe = self.session_manager.filter_universe(
                self.universe_full,
                MarketSessionMode.CRYPTO_ONLY,
            )
        logger.info("   Universo ativo (%s): %d símbolos", self.active_mode.value, len(self.universe))

        # 1. Buscar dados de mercado
        logger.info("📊 Buscando dados de mercado...")
        data_dict = self.fetch_market_data(self.universe)
        logger.info(f"   ✅ {len(data_dict)} ativos com dados")
        
        if len(data_dict) == 0:
            logger.warning("⚠️ Nenhum dado disponível - pulando ciclo")
            return

        bundles = self.last_data_bundles
        assessment = self.assess_regime(bundles)
        confidence_adjuster = assessment.confidence_adjuster if assessment else 1.0
        risk_multiplier = assessment.risk_multiplier if assessment else 1.0
        dynamic_min_conf = self._compute_dynamic_min_confidence(confidence_adjuster)

        if assessment:
            logger.info("📈 Regime detectado: %s", assessment.label)
            logger.info(
                "   Ajuste confiança: %.2f | Multiplicador de risco: %.2f",
                confidence_adjuster,
                risk_multiplier,
            )
        else:
            logger.info("📈 Regime não disponível - usando parâmetros padrão")
        
        # 2. Executar estratégias
        all_signals = []
        
        # Momentum Scanner
        logger.info("🚀 Executando Momentum Scanner...")
        momentum_signals = self.run_momentum_scanner(data_dict)
        if momentum_signals:
            # Adicionar tag de estratégia
            for sig in momentum_signals:
                sig['strategy'] = 'momentum'
                sig['confidence'] = float(
                    min(sig.get('confidence', 0.0) * confidence_adjuster, 0.99)
                )
            all_signals.append(momentum_signals)

        # Breakout Hunter
        logger.info("🔥 Executando Breakout Hunter...")
        breakout_signals = self.run_breakout_hunter(bundles)
        if breakout_signals:
            for sig in breakout_signals:
                sig['confidence'] = float(
                    min(sig.get('confidence', 0.0) * confidence_adjuster, 0.99)
                )
            all_signals.append(breakout_signals)

        # FX Mean Reversion
        logger.info("🔁 Executando FX Mean Reversion...")
        mean_reversion_signals = self.run_mean_reversion(bundles)
        if mean_reversion_signals:
            for sig in mean_reversion_signals:
                sig['confidence'] = float(
                    min(sig.get('confidence', 0.0) * confidence_adjuster, 0.99)
                )
            all_signals.append(mean_reversion_signals)
        
        # 3. Consolidar sinais
        logger.info("🔗 Consolidando sinais...")
        consolidated = self.consolidate_signals(all_signals)
        logger.info(f"   ✅ {len(consolidated)} sinais consolidados")
        
        # 4. Formatar e salvar
        if consolidated:
            self._rank_confidences(consolidated, dynamic_min_conf)
            formatted = self.format_signals_for_ea(
                consolidated,
                min_confidence=dynamic_min_conf,
                assessment=assessment,
                risk_multiplier=risk_multiplier,
            )
            self.save_signals(formatted)
            self.total_signals_generated += 1
            
            # Log resumo
            logger.info("")
            logger.info("📋 RESUMO DE SINAIS:")
            for sig in consolidated[:5]:  # Top 5
                logger.info(f"   {sig['symbol']}: {sig['action']} @ {sig['entry_price']:.2f} "
                          f"(conf: {sig['confidence']:.2f})")
        else:
            logger.warning("⚠️ Nenhum sinal gerado neste ciclo")
        
        logger.info("="*80)
        self.last_scan_time = datetime.now()
    
    def run(self):
        """Loop principal do servidor."""
        logger.info("")
        logger.info("🚀 INICIANDO SERVIDOR TÁTICO NUMEIA v6.0")
        logger.info("="*80)
        logger.info("📡 Aguardando ciclo de scan...")
        logger.info(f"   Intervalo: {self.scan_interval}s ({self.scan_interval/60:.1f} minutos)")
        logger.info("="*80)
        logger.info("")
        
        try:
            while True:
                # Verificar se é hora de fazer scan
                if (self.last_scan_time is None or 
                    (datetime.now() - self.last_scan_time).total_seconds() >= self.scan_interval):
                    self.run_scan_cycle()
                
                # Aguardar antes do próximo check
                time.sleep(10)  # Check a cada 10s
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("⏸️ Servidor interrompido pelo usuário")
            logger.info("="*80)
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
            import traceback
            logger.error(traceback.format_exc())

    @staticmethod
    def _json_default(obj):
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, (np.ndarray, list, tuple)):
            return [NumeiaV6TacticalServer._json_default(x) for x in obj]
        return str(obj)


def main():
    """Função principal."""
    server = NumeiaV6TacticalServer()
    server.run()


if __name__ == '__main__':
    main()

