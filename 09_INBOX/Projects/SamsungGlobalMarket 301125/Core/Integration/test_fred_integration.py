# -*- coding: utf-8 -*-
"""
TESTE DE INTEGRAÇÃO FRED API
DIRETIVA: F2-T1
DATA: 02-11-2025 22:15 CET

OBJETIVO:
- Validar que FRED API está instalado e funcional
- Testar busca de séries DGS10 e T10YIE
- Calcular taxa de juros real
- Confirmar que GoldModule pode operar
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Adicionar paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fred_integration():
    """
    Testa integração completa da FRED API
    
    Returns:
        bool: True se integração funcional
    """
    print("\n" + "="*80)
    print("TESTE: Integração FRED API")
    print("="*80 + "\n")
    
    # TESTE 1: IMPORTAR FREDAPI
    logger.info("1. TESTANDO IMPORTAÇÃO DA FREDAPI...")
    try:
        from fredapi import Fred
        logger.info("  ✅ fredapi importado com sucesso")
        fredapi_ok = True
    except Exception as e:
        logger.error(f"  ❌ ERRO ao importar: {e}")
        return False
    
    # TESTE 2: INICIALIZAR FRED
    logger.info("\n2. INICIALIZANDO FRED CLIENT...")
    try:
        # Nota: API key demo pode ter limitações
        # Para produção, usar: fred = Fred(api_key='SEU_API_KEY')
        fred = Fred(api_key='demo')
        logger.info("  ✅ FRED client inicializado")
        fred_ok = True
    except Exception as e:
        logger.error(f"  ❌ ERRO: {e}")
        return False
    
    # TESTE 3: BUSCAR DGS10 (10-Year Treasury)
    logger.info("\n3. BUSCANDO SÉRIE DGS10 (10-Year Treasury)...")
    try:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        dgs10 = fred.get_series('DGS10', observation_start=start_date)
        
        if dgs10 is not None and len(dgs10) > 0:
            logger.info(f"  ✅ DGS10 obtido: {len(dgs10)} observações")
            logger.info(f"     Última taxa: {dgs10.iloc[-1]:.2f}%")
            logger.info(f"     Média 1 ano: {dgs10.mean():.2f}%")
            dgs10_ok = True
        else:
            logger.warning("  ⚠️ DGS10: Sem dados")
            dgs10_ok = False
    except Exception as e:
        logger.error(f"  ❌ ERRO: {e}")
        dgs10_ok = False
    
    # TESTE 4: BUSCAR T10YIE (Breakeven Inflation)
    logger.info("\n4. BUSCANDO SÉRIE T10YIE (Breakeven Inflation)...")
    try:
        t10yie = fred.get_series('T10YIE', observation_start=start_date)
        
        if t10yie is not None and len(t10yie) > 0:
            logger.info(f"  ✅ T10YIE obtido: {len(t10yie)} observações")
            logger.info(f"     Breakeven atual: {t10yie.iloc[-1]:.2f}%")
            logger.info(f"     Média 1 ano: {t10yie.mean():.2f}%")
            t10yie_ok = True
        else:
            logger.warning("  ⚠️ T10YIE: Sem dados")
            t10yie_ok = False
    except Exception as e:
        logger.error(f"  ❌ ERRO: {e}")
        t10yie_ok = False
    
    # TESTE 5: CALCULAR TAXA DE JUROS REAL
    logger.info("\n5. CALCULANDO TAXA DE JUROS REAL...")
    if dgs10_ok and t10yie_ok:
        try:
            import pandas as pd
            aligned = pd.DataFrame({
                'nominal': dgs10,
                'breakeven': t10yie
            }).dropna()
            
            real_rate = aligned['nominal'] - aligned['breakeven']
            
            logger.info(f"  ✅ Taxa real calculada: {len(real_rate)} dias")
            logger.info(f"     Taxa real atual: {real_rate.iloc[-1]:.2f}%")
            logger.info(f"     Taxa real média: {real_rate.mean():.2f}%")
            
            # Análise para Gold
            if real_rate.iloc[-1] < 0:
                logger.info("     🟡 Taxa real NEGATIVA → BULLISH para Gold")
            else:
                logger.info("     🔵 Taxa real POSITIVA → BEARISH para Gold")
            
            real_rate_ok = True
        except Exception as e:
            logger.error(f"  ❌ ERRO: {e}")
            real_rate_ok = False
    else:
        logger.error("  ❌ Não é possível calcular (dados faltando)")
        real_rate_ok = False
    
    # TESTE 6: TESTAR UNIFIEDDATAFETCHER
    logger.info("\n6. TESTANDO UNIFIEDDATAFETCHER COM FRED...")
    try:
        from SystemOrchestrator_v3_1 import UnifiedDataFetcher
        
        fetcher = UnifiedDataFetcher(fred_api_key='demo')
        
        if fetcher.fred_available:
            logger.info("  ✅ UnifiedDataFetcher com FRED habilitado")
            
            # Testar método get_real_interest_rate
            real_rate_test = fetcher.get_real_interest_rate()
            
            if len(real_rate_test) > 0:
                logger.info(f"  ✅ get_real_interest_rate() funcional")
                logger.info(f"     {len(real_rate_test)} dias de dados")
                fetcher_ok = True
            else:
                logger.warning("  ⚠️ get_real_interest_rate() retornou vazio")
                fetcher_ok = False
        else:
            logger.error("  ❌ FRED não disponível no UnifiedDataFetcher")
            fetcher_ok = False
            
    except Exception as e:
        logger.error(f"  ❌ ERRO: {e}")
        import traceback
        logger.error(traceback.format_exc())
        fetcher_ok = False
    
    # RESULTADO FINAL
    print("\n" + "="*80)
    print("RESULTADO DA INTEGRAÇÃO FRED:")
    print(f"  fredapi instalado: {'✅ OK' if fredapi_ok else '❌ FALHA'}")
    print(f"  FRED client: {'✅ OK' if fred_ok else '❌ FALHA'}")
    print(f"  DGS10 (Treasury): {'✅ OK' if dgs10_ok else '❌ FALHA'}")
    print(f"  T10YIE (Breakeven): {'✅ OK' if t10yie_ok else '❌ FALHA'}")
    print(f"  Taxa real calculada: {'✅ OK' if real_rate_ok else '❌ FALHA'}")
    print(f"  UnifiedDataFetcher: {'✅ OK' if fetcher_ok else '❌ FALHA'}")
    print("="*80 + "\n")
    
    all_ok = fredapi_ok and fred_ok and dgs10_ok and t10yie_ok and real_rate_ok and fetcher_ok
    
    if all_ok:
        print("✅ INTEGRAÇÃO FRED COMPLETA E FUNCIONAL")
        print("✅ GoldModule pode operar plenamente")
        print("✅ EUR 100,000 DESBLOQUEADOS")
        return True
    else:
        print("❌ INTEGRAÇÃO FRED TEM PROBLEMAS")
        return False

if __name__ == "__main__":
    success = test_fred_integration()
    
    import json
    result = {
        'test': 'FRED Integration',
        'passed': success,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('test_fred_integration_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResultado salvo em: test_fred_integration_result.json\n")

