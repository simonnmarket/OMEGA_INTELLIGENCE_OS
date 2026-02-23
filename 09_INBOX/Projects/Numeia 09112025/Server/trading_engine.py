#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOTOR DE TRADING - CÉREBRO DO SISTEMA
PROJETO: Prometheus v3.0.0
PROTOCOLO: Omega TIER-0
ARQUITETURA: Big Tech - Serviço Desacoplado

Motor principal que executa análises de mercado e gera sinais de trading.
Integrado com o NumeiaTradingSystem v3.0.
"""

import time
import logging
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import sys
from decimal import Decimal

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("TradingEngine")

# ============================================================================
# MOTOR DE TRADING
# ============================================================================
class TradingEngine:
    """
    Motor principal de análise e geração de sinais.
    Executa o NumeiaTradingSystem em loop contínuo.
    """
    
    def __init__(self):
        self.is_running = False
        self.signal_callback: Optional[Callable[[Dict], None]] = None
        self.numeia_system = None
        self.cycle_interval = 1.0  # Segundos entre ciclos de análise
        self.last_signal_time = {}
        self._async_loop = None
        self._async_thread = None
        
        # Tentar importar NumeiaTradingSystem
        try:
            # Importar componentes do Numeia
            from NumeiaTradingSystem_v3_0_FINAL import (
                HaleIntentionalityEngine,
                RossiDynamicKellyEngine,
                TanakaKalmanEngine,
                LeblancZKPEngine,
                MarketMastersPerfectionEngine,
                OilStrategyProvenV3,
                GoldenStrategyFuturesV3,
                CryptoQuantumMeanReversionV3
            )
            
            # Inicializar engines do Numeia
            self.hale_engine = HaleIntentionalityEngine()
            self.rossi_engine = RossiDynamicKellyEngine()
            self.tanaka_engine = TanakaKalmanEngine()
            self.leblanc_engine = LeblancZKPEngine()
            self.market_masters = MarketMastersPerfectionEngine()
            
            # Inicializar estratégias
            self.strategies = [
                OilStrategyProvenV3(
                    self.hale_engine, self.rossi_engine, self.tanaka_engine,
                    self.leblanc_engine, self.market_masters
                ),
                GoldenStrategyFuturesV3(
                    self.hale_engine, self.rossi_engine, self.tanaka_engine,
                    self.leblanc_engine, self.market_masters
                ),
                # Adicionar outras estratégias conforme necessário
            ]
            
            self.numeia_loaded = True
            logger.info("[OK] NumeiaTradingSystem v3.0 carregado com sucesso")
            logger.info(f"   Estratégias ativas: {len(self.strategies)}")
            
        except ImportError as e:
            logger.warning(f"[AVISO] NumeiaTradingSystem nao encontrado: {e}")
            logger.info("   Operando em modo simulador (sinais de teste)")
            self.numeia_loaded = False
            self.strategies = []
        
        logger.info("Motor de Trading inicializado")
    
    def set_signal_callback(self, callback: Callable[[Dict], None]):
        """
        Define callback para envio de sinais.
        Será chamado sempre que um novo sinal for gerado.
        """
        self.signal_callback = callback
        logger.debug("Callback de sinais configurado")
    
    def _simulate_signal_generation(self):
        """
        Gera sinais simulados quando NumeiaTradingSystem não está disponível.
        Para uso em testes e desenvolvimento.
        """
        import random
        
        # Simulação: 2% de chance de gerar sinal a cada ciclo
        if random.random() > 0.98:
            signals = [
                {
                    'id': f"sgm_sim_{int(time.time())}",
                    'asset': 'GBPUSD',  # OPERAÇÃO NOTURNA: apenas GBPUSD
                    'action': random.choice(['BUY', 'SELL']),
                    'volume': 0.01,
                    'stop_loss': None,
                    'take_profit': None,
                    'confidence': random.uniform(0.6, 0.95),
                    'timestamp': int(time.time() * 1000),
                    'source': 'simulator'
                }
            ]
            
            for signal in signals:
                self._emit_signal(signal)
    
    async def _run_numeia_cycle(self):
        """Executa um ciclo de análise do NumeiaTradingSystem."""
        try:
            # Preparar dados de mercado (simulado - substituir por dados reais)
            market_data = {
                'prices': [40000 + (time.time() % 1000) - 500],  # Simulação
                'macro': {
                    'geo_risk': 0.3,
                    'dxy': 100.5,
                    'inflation': 0.02
                }
            }
            
            # Executar todas as estratégias
            all_signals = []
            for strategy in self.strategies:
                try:
                    signals = await strategy.analyze(market_data)
                    if signals:
                        all_signals.extend(signals)
                except Exception as e:
                    logger.warning(f"Erro na estratégia {strategy.strategy_id}: {e}")
                    continue
            
            # Processar e emitir sinais
            for signal in all_signals:
                # Converter TradingSignalPerfeito para dict simples
                # Calcular volume usando rossi_engine (que está no TradingEngine, não no signal)
                volume_kelly = self.rossi_engine.update_and_calculate(Decimal('0'))
                
                signal_dict = {
                    'id': f"sgm_{signal.strategy_id}_{signal.timestamp}",
                    'asset': signal.asset,
                    'action': signal.action,
                    'volume': float(volume_kelly),
                    'confidence': float(signal.confidence),
                    'risk_score': float(signal.risk_score),
                    'timestamp': signal.timestamp,
                    'strategy_id': signal.strategy_id,
                    'metadata': signal.metadata,
                    'source': 'numeia'
                }
                
                # Adicionar stop_loss e take_profit se disponíveis
                if 'stop_loss' in signal.metadata:
                    signal_dict['stop_loss'] = signal.metadata['stop_loss']
                if 'take_profit' in signal.metadata:
                    signal_dict['take_profit'] = signal.metadata['take_profit']
                
                self._emit_signal(signal_dict)
                
        except Exception as e:
            logger.error(f"Erro no ciclo do Numeia: {e}")
    
    def _emit_signal(self, signal: Dict[str, Any]):
        """
        Emite um sinal de trading.
        Chama o callback configurado (socket_service).
        """
        signal_id = signal.get('id', 'unknown')
        
        # Verificar se já emitimos este sinal recentemente (evitar duplicatas)
        if signal_id in self.last_signal_time:
            elapsed = time.time() - self.last_signal_time[signal_id]
            if elapsed < 60:  # Não repetir sinal em menos de 60 segundos
                logger.debug(f"Sinal {signal_id} já emitido recentemente. Ignorando.")
                return
        
        self.last_signal_time[signal_id] = time.time()
        
        logger.info("=" * 70)
        logger.info(f"ALPHA GERADO: {signal_id}")
        logger.info(f"   Asset: {signal.get('asset')} | Action: {signal.get('action')}")
        logger.info(f"   Confidence: {signal.get('confidence', 0):.2%} | Source: {signal.get('source', 'unknown')}")
        logger.info("=" * 70)
        
        # Enviar sinal via callback
        if self.signal_callback:
            try:
                self.signal_callback(signal)
            except Exception as e:
                logger.error(f"Erro ao enviar sinal via callback: {e}")
        else:
            logger.warning("Nenhum callback configurado. Sinal não será transmitido.")
    
    def _start_async_loop(self):
        """Inicia loop assíncrono em thread separada."""
        def run_async_loop():
            self._async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_forever()
        
        self._async_thread = threading.Thread(target=run_async_loop, daemon=True)
        self._async_thread.start()
        
        # Aguardar loop iniciar
        time.sleep(0.5)
    
    def _stop_async_loop(self):
        """Para loop assíncrono."""
        if self._async_loop:
            self._async_loop.call_soon_threadsafe(self._async_loop.stop)
            if self._async_thread:
                self._async_thread.join(timeout=2)
            self._async_loop.close()
            self._async_loop = None
    
    def run(self):
        """Loop principal do motor de trading."""
        self.is_running = True
        
        logger.info("=" * 70)
        logger.info("🧠 MOTOR DE TRADING INICIADO")
        logger.info("=" * 70)
        logger.info("Buscando alphas no mercado...")
        logger.info(f"Modo: {'NumeiaTradingSystem' if self.numeia_loaded else 'Simulador'}")
        logger.info(f"Intervalo de ciclo: {self.cycle_interval}s")
        logger.info("=" * 70)
        
        # Iniciar loop assíncrono se necessário
        if self.numeia_loaded:
            self._start_async_loop()
        
        cycle_count = 0
        
        try:
            while self.is_running:
                cycle_start = time.time()
                cycle_count += 1
                
                try:
                    if self.numeia_loaded and self._async_loop:
                        # Executar ciclo assíncrono do Numeia
                        future = asyncio.run_coroutine_threadsafe(
                            self._run_numeia_cycle(),
                            self._async_loop
                        )
                        # Não aguardar conclusão (não-bloqueante)
                    else:
                        # Modo simulador
                        self._simulate_signal_generation()
                    
                except Exception as e:
                    logger.error(f"Erro no ciclo {cycle_count}: {e}")
                
                # Log periódico
                if cycle_count % 60 == 0:  # A cada 60 ciclos (~1 minuto)
                    logger.info(f"[OK] Motor ativo: {cycle_count} ciclos executados")
                
                # Controle de timing
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.cycle_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    logger.warning(f"Ciclo demorou {elapsed:.2f}s (mais que intervalo de {self.cycle_interval}s)")
                    
        except KeyboardInterrupt:
            logger.info("Interrupção recebida")
        except Exception as e:
            logger.critical(f"Erro crítico no loop principal: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Para o motor de trading."""
        logger.info("Parando motor de trading...")
        self.is_running = False
        
        if self.numeia_loaded:
            self._stop_async_loop()
        
        logger.info("[OK] Motor de Trading parado")
    
    def on_execution_report(self, report: Dict):
        """
        Callback para relatórios de execução do EA.
        Pode ser usado para feedback e aprendizado.
        """
        logger.info(f"[FEEDBACK] Relatório de execução recebido: {report.get('status')}")
        
        # Aqui você pode implementar:
        # - Atualização de modelos
        # - Ajuste de parâmetros
        # - Logging para análise
        # etc.

