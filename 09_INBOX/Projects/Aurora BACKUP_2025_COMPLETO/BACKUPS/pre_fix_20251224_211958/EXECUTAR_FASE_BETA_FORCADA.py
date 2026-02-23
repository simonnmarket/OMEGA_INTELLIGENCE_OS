#!/usr/bin/env python3
"""
EXECUTAR FASE BETA FORÇADA - Ignora resultado da FASE α
Executa teste de 24h mesmo se FASE α falhar (para teste de estresse)
"""

import sys
import asyncio
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar módulos necessários - ajustar nome do arquivo
import importlib.util
spec = importlib.util.spec_from_file_location(
    "aurora_executor",
    Path(__file__).parent / "AURORA_FINAL_EXECUCAO_AIC_V5.1.py"
)
aurora_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aurora_module)

AuroraInfrastructureValidator = aurora_module.AuroraInfrastructureValidator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("FORCE_BETA")

async def main():
    """Executa FASE β forçada (ignora resultado da FASE α)"""
    
    print("=" * 80)
    print("AURORA v5.1 - EXECUCAO FORCADA FASE BETA (24H)")
    print("=" * 80)
    print()
    print("⚠️  ATENCAO: Esta execucao IGNORA o resultado da FASE ALPHA")
    print("    Executando teste de 24h diretamente para validar infraestrutura")
    print()
    
    # Confirmar execução
    confirm = input("▶️  Executar FASE BETA (24h)? [s/N]: ").strip().lower()
    
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("⏹️  Execucao cancelada")
        return 0
    
    print()
    print("🚀 INICIANDO FASE BETA FORCADA...")
    print()
    
    # Criar validador
    validator = AuroraInfrastructureValidator()
    
    try:
        # Executar validação de 24h
        result = await validator.validate_24h_infrastructure()
        
        print()
        print("=" * 80)
        print("RESULTADO DA FASE BETA:")
        print("=" * 80)
        print()
        
        if result.get("infrastructure_valid"):
            print("✅ INFRAESTRUTURA VALIDADA")
        else:
            print("❌ INFRAESTRUTURA COM PROBLEMAS")
        
        print()
        print("Detalhes salvos em: aurora_beta_forced_result.json")
        
        # Salvar resultado
        import json
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"aurora_beta_forced_result_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return 0 if result.get("infrastructure_valid") else 1
        
    except Exception as e:
        logger.error(f"Erro na execucao: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

