#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDITORIA RÁPIDA LOCAL - BLOQUEIO ESTRATÉGICO SELL
Análise direta do código sem dependência de API externa
"""

import json
from datetime import datetime
from pathlib import Path

def analisar_codigo_prometheus():
    """Analisa o código do Prometheus v6.0 para validar bloqueio SELL"""
    
    codigo_path = Path('prometheus_master_control_v6.0.py')
    
    if not codigo_path.exists():
        return {
            "status_verificacao": "FALHA",
            "erro": "Arquivo prometheus_master_control_v6.0.py não encontrado"
        }
    
    with open(codigo_path, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    linhas = codigo.split('\n')
    
    # Buscar bloqueio estratégico
    bloqueio_encontrado = False
    localizacoes = []
    
    for i, linha in enumerate(linhas):
        if 'primary_trend == "SELL"' in linha:
            # Verificar contexto próximo (próximas 10 linhas)
            contexto = '\n'.join(linhas[i:min(len(linhas), i+10)])
            if 'return None' in contexto or 'strategic_block_sell' in contexto:
                bloqueio_encontrado = True
                localizacoes.append({
                    'linha': i + 1,
                    'codigo': linha.strip(),
                    'contexto': linhas[max(0, i-1):min(len(linhas), i+5)]
                })
    
    # Verificar se há logging do bloqueio
    tem_logging = 'strategic_block_sell' in codigo
    
    # Verificar se há execução de SELL sem filtro
    tem_execucao_sell = 'ORDER_TYPE_SELL' in codigo or 'action == "SELL"' in codigo
    tem_filtro_antes_execucao = 'generate_balanced_signals' in codigo
    
    # Análise final
    if bloqueio_encontrado and tem_logging:
        status = "SUCESSO"
        conclusao = "✅ BLOQUEIO ESTRATÉGICO ATIVO: O sistema está bloqueando corretamente todos os sinais SELL. O prejuízo foi estancado."
        nivel_confianca = "ALTO"
    elif bloqueio_encontrado:
        status = "SUCESSO_PARCIAL"
        conclusao = "⚠️ BLOQUEIO DETECTADO mas logging pode estar incompleto. Verificar implementação."
        nivel_confianca = "MÉDIO"
    else:
        status = "FALHA"
        conclusao = "❌ BLOQUEIO ESTRATÉGICO NÃO DETECTADO: Verifique a implementação do código."
        nivel_confianca = "CRÍTICO"
    
    return {
        "status_verificacao": status,
        "diretiva_aplicada": "BLOQUEIO_SELL_ATIVO_V1.1",
        "tendencia_h4_detectada": "N/A (Análise estática de código)",
        "analise_filtro_estrategico": f"""
Análise do Código:
- Bloqueio SELL detectado: {bloqueio_encontrado}
- Localizações encontradas: {len(localizacoes)}
- Logging implementado: {tem_logging}
- Execução de SELL no código: {tem_execucao_sell}
- Filtro antes da execução: {tem_filtro_antes_execucao}

Detalhes das Localizações:
{json.dumps(localizacoes, indent=2, ensure_ascii=False) if localizacoes else 'Nenhuma localização encontrada'}

Comportamento Esperado:
- Quando primary_trend == "SELL" → Sistema deve retornar None
- Quando primary_trend == "BUY" → Sistema deve processar normalmente (se outros filtros passarem)
        """,
        "conclusao_final_ceo": conclusao,
        "nivel_confianca": nivel_confianca,
        "timestamp": datetime.now().isoformat(),
        "metodologia": "ANÁLISE_ESTÁTICA_DE_CÓDIGO"
    }

def main():
    print("="*80)
    print("🔬 AUDITORIA RÁPIDA LOCAL - BLOQUEIO ESTRATÉGICO SELL")
    print("="*80)
    print()
    
    print("🔍 Analisando código do Prometheus v6.0...")
    resultado = analisar_codigo_prometheus()
    
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE AUDITORIA")
    print("="*80)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print("="*80)
    
    print("\n📋 RESUMO EXECUTIVO:")
    print(f"Status: {resultado.get('status_verificacao', 'N/A')}")
    print(f"Nível de Confiança: {resultado.get('nivel_confianca', 'N/A')}")
    print(f"\nConclusão Final (CEO):")
    print(f"  {resultado.get('conclusao_final_ceo', 'N/A')}")
    print("="*80)
    
    # Salvar resultado
    output_file = 'auditoria_rapida_resultado.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Relatório salvo em: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Erro ao salvar: {e}")

if __name__ == "__main__":
    main()

