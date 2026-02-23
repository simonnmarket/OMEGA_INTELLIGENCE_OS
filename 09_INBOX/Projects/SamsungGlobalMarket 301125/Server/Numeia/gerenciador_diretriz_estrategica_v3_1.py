#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERENCIADOR DE DIRETRIZ ESTRATÉGICA (CEO-CIENTISTA-CHEFE)
VERSÃO: V3.1 - FOCO NO BLOQUEIO SELL

Objetivo: Gerar o arquivo 'prompt_ceo_cientista_final.txt' contendo a diretriz
estratégica que servirá como System Instruction para o Agente de Auditoria Rápida (RAA)
do Gemini. A diretriz foca em validar o bloqueio estratégico de ordens SELL.
"""

import os
from pathlib import Path

# --------------------------------------------------------------------------------
# 1. DEFINIÇÃO DA DIRETRIZ FINAL DO CEO-CIENTISTA-CHEFE
# --------------------------------------------------------------------------------

DIRETRIZ_ESTRATEGICA_CEO = """
Você é o Agente de Auditoria Rápida (RAA), o braço de validação científica da Corretora Alpha.
Sua missão é estancar o prejuízo e garantir a segurança do capital.

DIRETIVA CRÍTICA CEO (V1.1):

1.  FALHA ERRADICADA: O sistema Prometheus v6.0 implementou um bloqueio total e irrefutável (if primary_trend == 'SELL': return None) para ordens de VENDA (SELL).

2.  RESTRIÇÃO DE OPERAÇÃO: O sistema só deve operar em tendências de ALTA (BUY/TREND_UP).

3.  AÇÃO: Use o Google Search (Grounding) para determinar a **tendência atual de 4 horas (H4) do par EUR/USD**.

4.  ANÁLISE ESTRATÉGICA: Baseado na tendência detectada, simule o comportamento do Prometheus v6.0 e emita um veredito.

    - Se a tendência for SELL/FLAT, o filtro **DEVE** bloquear (SUCESSO na validação).

    - Se a tendência for BUY, o filtro **DEVE** permitir o sinal (SUCESSO na validação, pois a intenção é permitir BUY).

FORMATO DE SAÍDA (JSON):

Você DEVE retornar a sua resposta estritamente no formato JSON, usando o seguinte esquema:

{
  "status_verificacao": "[SUCESSO | FALHA]",
  "diretiva_aplicada": "BLOQUEIO_SELL_ATIVO_V1.1",
  "tendencia_h4_detectada": "[BUY | SELL | FLAT]",
  "analise_filtro_estrategico": "Descrição de como o filtro estratégico do Prometheus v6.0 reagiria à tendência H4 detectada.",
  "conclusao_final_ceo": "Conclusão final de 1 linha sobre a correção da rota (se o prejuízo foi estancado)."
}
"""

# --------------------------------------------------------------------------------
# 2. FUNÇÃO DE GERAÇÃO DE ARQUIVO
# --------------------------------------------------------------------------------

def generate_prompt_file(filepath: str, content: str):
    """Gera o arquivo de prompt para ser lido pelo script de execução."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        # Verificar se foi salvo corretamente
        if Path(filepath).exists():
            tamanho = Path(filepath).stat().st_size
            print(f"✅ SUCESSO: Diretriz do CEO-Cientista-Chefe salva em '{filepath}'")
            print(f"   Tamanho: {tamanho} bytes")
            print("   -> O script de auditoria (raa_auditoria_v3_1.py) agora pode ser executado.")
            return True
        else:
            print(f"❌ ERRO: Arquivo não foi criado: '{filepath}'")
            return False
    except Exception as e:
        print(f"❌ ERRO: Não foi possível salvar o arquivo '{filepath}'. Erro: {e}")
        return False

# --------------------------------------------------------------------------------
# 3. EXECUÇÃO
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    print("="*80)
    print("GERENCIADOR DE DIRETRIZ ESTRATÉGICA - CEO-CIENTISTA-CHEFE V3.1")
    print("="*80)
    print()
    
    PROMPT_FILEPATH = 'prompt_ceo_cientista_final.txt'
    
    sucesso = generate_prompt_file(PROMPT_FILEPATH, DIRETRIZ_ESTRATEGICA_CEO)
    
    if sucesso:
        print()
        print("="*80)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO")
        print("="*80)
        print()
        print("Próximo passo: Execute o script de auditoria:")
        print("  python raa_auditoria_v3_1.py")
        print()
    else:
        print()
        print("="*80)
        print("❌ FALHA NA GERAÇÃO DO ARQUIVO")
        print("="*80)

