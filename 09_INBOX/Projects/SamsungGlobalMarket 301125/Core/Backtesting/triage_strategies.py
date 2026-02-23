# -*- coding: utf-8 -*-
"""
SAMSUNG GLOBAL MARKET - PROMETHEUS v3.0
TRIAGE DE ESTRATÉGIAS - AUDITORIA DE LEGADO
METODOLOGIA: Backtest rápido simplificado com classificação automática

DIRETIVA: CEO UNIVERSAL v1.0 | Prometheus v3.0.0 | TIER-0
DATA: 16 de Novembro de 2025 (CET/Berlin)
AUTOR: Sistema Prometheus
STATUS: ✅ PRODUÇÃO

OBJETIVO:
Este script é nossa ferramenta de avaliação de ativos.
Ele deve ser impiedoso na sua classificação e focado em gerar o triage_report.csv.

COMPLIANCE:
- Análise cirúrgica e rigorosa dos dados (CEO UNIVERSAL)
- Questionamento constante das premissas
- Decisões baseadas em métricas quantitativas sólidas
- Logs estruturados ISO 8601

FUNCIONALIDADE:
- Varre diretórios de estratégias (Core/Strategies/)
- Identifica scripts de estratégias automaticamente
- Extrai parâmetros essenciais
- Executa backtest rápido simplificado
- Calcula métricas: total_return e max_drawdown
- Classifica como: PROMISSOR / ANÊMICO / MORTO
- Gera triage_report.csv com resumo de classificações
"""

import ast
import importlib.util
import inspect
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import csv
import json
import traceback
from datetime import datetime
import pandas as pd
import numpy as np

# Configuração de logging estruturado (ISO 8601)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)
logger = logging.getLogger(__name__)

# =====================================================
# PARÂMETROS DE CLASSIFICAÇÃO
# =====================================================

# Thresholds para classificação
THRESHOLD_PROMISSOR_RETURN = 1000.0  # USD
THRESHOLD_PROMISSOR_SHARPE = 0.5
THRESHOLD_PROMISSOR_WIN_RATE = 0.45

THRESHOLD_ANEMICO_RETURN = 0.0  # USD
THRESHOLD_ANEMICO_SHARPE = 0.0
THRESHOLD_ANEMICO_WIN_RATE = 0.35

# Se abaixo de ANEMICO = MORTO

# =====================================================
# DESCOBERTA DE ESTRATÉGIAS
# =====================================================

def discover_strategy_files(base_dir: Path) -> List[Dict[str, Any]]:
    """
    Descobre arquivos de estratégias nos diretórios
    
    Args:
        base_dir: Diretório base para busca (ex: Core/Strategies/)
    
    Returns:
        Lista de dicionários com informações de cada arquivo de estratégia
    """
    logger.info(f"DESCOBERTA: Varrendo diretório {base_dir}")
    
    strategies = []
    
    # Padrões de nomes de arquivos de estratégia
    strategy_patterns = [
        r'.*Strategy.*\.py$',
        r'.*Strategy.*Scientific.*\.py$',
        r'.*Strategy.*Backtest.*\.py$',
        r'.*_Scientific\.py$',
        r'.*_Backtest\.py$'
    ]
    
    # Excluir arquivos específicos
    exclude_patterns = [
        r'.*Adapter.*\.py$',
        r'.*Manager.*\.py$',
        r'.*validate.*\.py$',
        r'.*test.*\.py$',
        r'.*__init__\.py$',
        r'.*__pycache__.*'
    ]
    
    if not base_dir.exists():
        logger.warning(f"Diretório não existe: {base_dir}")
        return strategies
    
    for py_file in base_dir.rglob('*.py'):
        # Verifica se deve ser excluído
        should_exclude = any(re.match(pattern, py_file.name, re.IGNORECASE) for pattern in exclude_patterns)
        if should_exclude:
            continue
        
        # Verifica se é uma estratégia
        is_strategy = any(re.match(pattern, py_file.name, re.IGNORECASE) for pattern in strategy_patterns)
        
        if is_strategy:
            rel_path = py_file.relative_to(base_dir.parent.parent)
            
            strategies.append({
                'file_path': str(py_file),
                'relative_path': str(rel_path),
                'file_name': py_file.name,
                'module_name': py_file.stem,
                'directory': str(py_file.parent.relative_to(base_dir)),
                'category': py_file.parent.name if py_file.parent.name != 'Strategies' else py_file.parent.parent.name
            })
    
    logger.info(f"DESCOBERTA CONCLUÍDA: {len(strategies)} arquivos de estratégia encontrados")
    return strategies


# =====================================================
# EXTRAÇÃO DE PARÂMETROS
# =====================================================

def extract_strategy_parameters(file_path: Path) -> Dict[str, Any]:
    """
    Extrai parâmetros essenciais de um arquivo de estratégia
    
    Args:
        file_path: Caminho do arquivo Python
    
    Returns:
        Dicionário com parâmetros extraídos
    """
    params = {
        'symbol': None,
        'timeframe': None,
        'sma_period': None,
        'stop_loss_pips': None,
        'take_profit_pips': None,
        'lot_size': None,
        'has_backtest_function': False,
        'has_strategy_class': False,
        'classes': [],
        'functions': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST para extrair informações
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Erro de sintaxe em {file_path.name}: {e}")
            return params
        
        # Extrai classes e funções
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                params['classes'].append(node.name)
                if 'Strategy' in node.name or 'Strategy' in str(node.bases):
                    params['has_strategy_class'] = True
            
            if isinstance(node, ast.FunctionDef):
                params['functions'].append(node.name)
                if 'backtest' in node.name.lower() or 'run_backtest' in node.name.lower():
                    params['has_backtest_function'] = True
        
        # Extrai parâmetros via regex (simplificado)
        symbol_match = re.search(r'SYMBOL\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
        if symbol_match:
            params['symbol'] = symbol_match.group(1)
        
        sma_match = re.search(r'SMA_PERIOD\s*=\s*(\d+)', content, re.IGNORECASE)
        if sma_match:
            params['sma_period'] = int(sma_match.group(1))
        
        sl_match = re.search(r'STOP_LOSS[_\s]*PIPS?\s*=\s*(\d+)', content, re.IGNORECASE)
        if sl_match:
            params['stop_loss_pips'] = int(sl_match.group(1))
        
        tp_match = re.search(r'TAKE_PROFIT[_\s]*PIPS?\s*=\s*(\d+)', content, re.IGNORECASE)
        if tp_match:
            params['take_profit_pips'] = int(tp_match.group(1))
        
        lot_match = re.search(r'LOT[_\s]*SIZE\s*=\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if lot_match:
            params['lot_size'] = float(lot_match.group(1))
        
        tf_match = re.search(r'TIMEFRAME\s*=\s*mt5\.TIMEFRAME_(\w+)', content, re.IGNORECASE)
        if tf_match:
            params['timeframe'] = tf_match.group(1)
        
    except Exception as e:
        logger.warning(f"Erro ao extrair parâmetros de {file_path.name}: {e}")
    
    return params


# =====================================================
# BACKTEST RÁPIDO SIMPLIFICADO
# =====================================================

def run_quick_backtest(strategy_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa backtest rápido simplificado para uma estratégia
    
    Args:
        strategy_info: Informações da estratégia descoberta
    
    Returns:
        Dicionário com métricas calculadas
    """
    file_path = Path(strategy_info['file_path'])
    
    logger.info(f"BACKTEST RÁPIDO: {strategy_info['file_name']}")
    
    try:
        # Tenta importar e executar a estratégia
        spec = importlib.util.spec_from_file_location(strategy_info['module_name'], file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Não foi possível carregar {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Adiciona caminho para imports
        sys.path.insert(0, str(file_path.parent))
        sys.path.insert(0, str(file_path.parent.parent))
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warning(f"Erro ao carregar módulo {file_path.name}: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'win_rate': 0.0,
                'total_trades': 0
            }
        
        # Tenta encontrar e executar função de backtest
        backtest_func = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if inspect.isfunction(attr):
                if 'backtest' in attr_name.lower() or 'run' in attr_name.lower():
                    if callable(attr):
                        try:
                            # Tenta executar com dados sintéticos mínimos
                            # Se a estratégia requer MT5 ou dados reais, isso falhará
                            # Mas capturamos o erro e classificamos como ANÊMICO/MORTO
                            result = attr()
                            
                            # Se retornou resultados, tenta extrair métricas
                            if isinstance(result, dict):
                                total_return = result.get('total_return', result.get('total_profit', 0.0))
                                max_dd = abs(result.get('max_drawdown', result.get('max_dd', 0.0)))
                                sharpe = result.get('sharpe_ratio', result.get('sharpe', 0.0))
                                win_rate = result.get('win_rate', result.get('winrate', 0.0))
                                trades = result.get('total_trades', result.get('trades', 0))
                                
                                return {
                                    'status': 'SUCCESS',
                                    'total_return': float(total_return) if total_return else 0.0,
                                    'max_drawdown': float(max_dd) if max_dd else 0.0,
                                    'sharpe_ratio': float(sharpe) if sharpe else 0.0,
                                    'win_rate': float(win_rate) if win_rate else 0.0,
                                    'total_trades': int(trades) if trades else 0
                                }
                        except Exception as e:
                            logger.debug(f"Erro ao executar {attr_name} em {file_path.name}: {e}")
                            continue
        
        # Se não encontrou função executável, classifica como não testável
        return {
            'status': 'NOT_TESTABLE',
            'error': 'Nenhuma função de backtest encontrada ou executável',
            'total_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0,
            'total_trades': 0
        }
        
    except Exception as e:
        logger.warning(f"Erro ao executar backtest rápido de {file_path.name}: {e}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'total_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0,
            'total_trades': 0
        }


# =====================================================
# CLASSIFICAÇÃO DE ESTRATÉGIAS
# =====================================================

def classify_strategy(metrics: Dict[str, Any]) -> str:
    """
    Classifica estratégia como PROMISSOR / ANÊMICO / MORTO
    
    Critérios:
    - PROMISSOR: Return > threshold E Sharpe > threshold E Win Rate > threshold
    - ANÊMICO: Return >= 0 OU (Return > -1000 E Win Rate >= 0.35)
    - MORTO: Return < -1000 OU Win Rate < 0.35 OU erro fatal
    
    Args:
        metrics: Dicionário com métricas calculadas
    
    Returns:
        Classificação: 'PROMISSOR', 'ANÊMICO' ou 'MORTO'
    """
    status = metrics.get('status', 'ERROR')
    total_return = metrics.get('total_return', 0.0)
    sharpe_ratio = metrics.get('sharpe_ratio', 0.0)
    win_rate = metrics.get('win_rate', 0.0)
    max_drawdown = metrics.get('max_drawdown', 0.0)
    
    # Se teve erro fatal ou não é testável
    if status in ['ERROR', 'NOT_TESTABLE']:
        return 'MORTO'
    
    # PROMISSOR: Performance excelente
    if (total_return >= THRESHOLD_PROMISSOR_RETURN and 
        sharpe_ratio >= THRESHOLD_PROMISSOR_SHARPE and 
        win_rate >= THRESHOLD_PROMISSOR_WIN_RATE):
        return 'PROMISSOR'
    
    # MORTO: Performance muito ruim
    if (total_return < -1000.0 or 
        win_rate < THRESHOLD_ANEMICO_WIN_RATE or 
        sharpe_ratio < -1.0):
        return 'MORTO'
    
    # ANÊMICO: Performance mediana
    if (total_return >= THRESHOLD_ANEMICO_RETURN or 
        (total_return > -1000.0 and win_rate >= THRESHOLD_ANEMICO_WIN_RATE)):
        return 'ANÊMICO'
    
    # Default: MORTO se não se encaixa em nenhum critério
    return 'MORTO'


# =====================================================
# GERAÇÃO DE RELATÓRIO DE TRIAGE
# =====================================================

def generate_triage_report(
    strategies: List[Dict[str, Any]],
    output_path: Optional[Path] = None
) -> Path:
    """
    Gera relatório de triage em formato CSV
    
    Args:
        strategies: Lista de estratégias analisadas
        output_path: Caminho para salvar relatório (opcional)
    
    Returns:
        Caminho do arquivo gerado
    """
    output_dir = Path(__file__).parent.parent.parent / "Output" / "Backtests" / "Triage"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_path is None:
        output_path = output_dir / f"triage_report_{timestamp}.csv"
    
    # Ordena por classificação (PROMISSOR > ANÊMICO > MORTO)
    classification_order = {'PROMISSOR': 1, 'ANÊMICO': 2, 'MORTO': 3}
    strategies_sorted = sorted(
        strategies,
        key=lambda x: (classification_order.get(x.get('classification', 'MORTO'), 3), 
                      x.get('metrics', {}).get('total_return', 0.0)),
        reverse=False
    )
    
    # Gera CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'classification', 'file_name', 'relative_path', 'category', 'directory',
            'status', 'total_return', 'max_drawdown', 'sharpe_ratio', 'win_rate', 
            'total_trades', 'symbol', 'timeframe', 'sma_period', 'stop_loss_pips',
            'take_profit_pips', 'lot_size', 'has_backtest_function', 'has_strategy_class',
            'error'
        ])
        
        # Resumo por classificação
        promissor_count = sum(1 for s in strategies if s.get('classification') == 'PROMISSOR')
        anemico_count = sum(1 for s in strategies if s.get('classification') == 'ANÊMICO')
        morto_count = sum(1 for s in strategies if s.get('classification') == 'MORTO')
        
        writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['SUMMARY', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['total_strategies', len(strategies), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['PROMISSOR', promissor_count, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['ANÊMICO', anemico_count, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['MORTO', morto_count, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['DETAILS', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        
        # Dados das estratégias
        for strategy in strategies_sorted:
            params = strategy.get('parameters', {})
            metrics = strategy.get('metrics', {})
            
            writer.writerow([
                strategy.get('classification', 'UNKNOWN'),
                strategy.get('file_name', ''),
                strategy.get('relative_path', ''),
                strategy.get('category', ''),
                strategy.get('directory', ''),
                metrics.get('status', 'UNKNOWN'),
                f"{metrics.get('total_return', 0.0):.2f}",
                f"{metrics.get('max_drawdown', 0.0):.2f}",
                f"{metrics.get('sharpe_ratio', 0.0):.2f}",
                f"{metrics.get('win_rate', 0.0):.4f}",
                metrics.get('total_trades', 0),
                params.get('symbol', ''),
                params.get('timeframe', ''),
                params.get('sma_period', ''),
                params.get('stop_loss_pips', ''),
                params.get('take_profit_pips', ''),
                params.get('lot_size', ''),
                params.get('has_backtest_function', False),
                params.get('has_strategy_class', False),
                metrics.get('error', '')
            ])
    
    logger.info(f"RELATÓRIO DE TRIAGE GERADO: {output_path}")
    logger.info(f"RESUMO: {promissor_count} PROMISSOR, {anemico_count} ANÊMICO, {morto_count} MORTO")
    
    return output_path


# =====================================================
# BLOCO PRINCIPAL DE EXECUÇÃO
# =====================================================

def main():
    """
    Função principal de execução do triage de estratégias
    """
    logger.info("=" * 80)
    logger.info("TRIAGE DE ESTRATÉGIAS - AUDITORIA DE LEGADO")
    logger.info("Protocolo: CEO UNIVERSAL v1.0 | Prometheus v3.0.0 | TIER-0")
    logger.info("=" * 80)
    
    try:
        # 1. Descobrir arquivos de estratégias
        logger.info("ETAPA 1: Descoberta de arquivos de estratégias")
        project_root = Path(__file__).parent.parent.parent
        strategies_dir = project_root / "Core" / "Strategies"
        
        if not strategies_dir.exists():
            logger.error(f"Diretório não encontrado: {strategies_dir}")
            return {'success': False, 'error': f'Diretório não encontrado: {strategies_dir}'}
        
        strategy_files = discover_strategy_files(strategies_dir)
        
        if not strategy_files:
            logger.warning("Nenhum arquivo de estratégia encontrado")
            return {'success': False, 'error': 'Nenhum arquivo de estratégia encontrado'}
        
        logger.info(f"ETAPA 1 CONCLUÍDA: {len(strategy_files)} arquivos encontrados")
        
        # 2. Extrair parâmetros e executar backtests rápidos
        logger.info("ETAPA 2: Extração de parâmetros e execução de backtests rápidos")
        strategies_analyzed = []
        
        for i, strategy_info in enumerate(strategy_files, 1):
            logger.info(f"[{i}/{len(strategy_files)}] Analisando: {strategy_info['file_name']}")
            
            # Extrai parâmetros
            params = extract_strategy_parameters(Path(strategy_info['file_path']))
            strategy_info['parameters'] = params
            
            # Executa backtest rápido
            metrics = run_quick_backtest(strategy_info)
            strategy_info['metrics'] = metrics
            
            # Classifica estratégia
            classification = classify_strategy(metrics)
            strategy_info['classification'] = classification
            
            strategies_analyzed.append(strategy_info)
            
            logger.info(
                f"  Classificação: {classification} | "
                f"Return: ${metrics.get('total_return', 0.0):.2f} | "
                f"Win Rate: {metrics.get('win_rate', 0.0):.2%} | "
                f"Status: {metrics.get('status', 'UNKNOWN')}"
            )
        
        logger.info(f"ETAPA 2 CONCLUÍDA: {len(strategies_analyzed)} estratégias analisadas")
        
        # 3. Geração de relatório de triage
        logger.info("ETAPA 3: Geração de relatório de triage")
        report_path = generate_triage_report(strategies_analyzed)
        
        # 4. Resumo final
        promissor = sum(1 for s in strategies_analyzed if s.get('classification') == 'PROMISSOR')
        anemico = sum(1 for s in strategies_analyzed if s.get('classification') == 'ANÊMICO')
        morto = sum(1 for s in strategies_analyzed if s.get('classification') == 'MORTO')
        
        logger.info("=" * 80)
        logger.info("RESULTADOS DO TRIAGE DE ESTRATÉGIAS")
        logger.info("=" * 80)
        logger.info(f"Total de Estratégias: {len(strategies_analyzed)}")
        logger.info(f"PROMISSOR: {promissor} ({promissor/len(strategies_analyzed)*100:.1f}%)")
        logger.info(f"ANÊMICO: {anemico} ({anemico/len(strategies_analyzed)*100:.1f}%)")
        logger.info(f"MORTO: {morto} ({morto/len(strategies_analyzed)*100:.1f}%)")
        logger.info("=" * 80)
        logger.info(f"RELATÓRIO GERADO: {report_path}")
        logger.info("TRIAGE CONCLUÍDO COM SUCESSO!")
        
        return {
            'success': True,
            'report_path': str(report_path),
            'total_strategies': len(strategies_analyzed),
            'promissor': promissor,
            'anemico': anemico,
            'morto': morto
        }
        
    except Exception as e:
        logger.exception(f"ERRO durante execução do triage: {e}")
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


if __name__ == "__main__":
    result = main()
    if result['success']:
        print(f"\n✅ Triage concluído!")
        print(f"📊 Relatório: {result['report_path']}")
        print(f"📈 Resumo: {result['promissor']} PROMISSOR, {result['anemico']} ANÊMICO, {result['morto']} MORTO")
    else:
        print(f"\n❌ Erro: {result.get('error', 'Desconhecido')}")
        exit(1)

