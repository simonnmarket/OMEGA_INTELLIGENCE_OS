# -*- coding: utf-8 -*-
"""
PROTOCOLO DE SEGURANÇA E GOVERNANÇA PROMETHEUS V3.0
Implementação da Ordem de HARD STOP e Verificação dos Gatilhos do Conselho.
Este script executa a ordem de comando executivo para PARADA IMEDIATA.
"""

import json
import datetime
from dataclasses import dataclass
from typing import Dict, Any, List

# DADOS DE ENTRADA: Métrica de falha do Prometheus V2.5
# Estes dados ativam os gatilhos de HARD STOP
RELATORIO_CIENTIFICO_DADOS_ATUAIS = {
    "lucro_total": -36.94,              # Gatilho CEO Lexity: < -10.00
    "sharpe_ratio": -0.2426,            # Gatilho CIO Eesek: < 0.0
    "taxa_erros_excecoes": 52.19,       # Gatilho CTO Zai: > 5.0%
    "expectativa_matematica_observada": -0.0142 # Gatilho CIO Eesek: < 0.0
}

@dataclass
class RiskPolicy:
    """Regras de HARD STOP definidas pelo conselho (D.U.D.E.)."""
    max_loss_diaria: float = -10.00         
    max_taxa_erros: float = 5.0              
    min_sharpe_ratio: float = 0.0            
    min_expectativa_matematica: float = 0.0  

def decidir_operacao(dados: Dict[str, float], policy: RiskPolicy) -> Dict[str, Any]:
    """Aplica o Protocolo de Parada de Segurança (Hard Stop)."""
    
    motivos_stop: List[str] = []
    
    # 1. Risco de Capital (CEO Lexity)
    if dados['lucro_total'] < policy.max_loss_diaria:
        motivos_stop.append(f"LEXITY (Capital): Lucro Total ({dados['lucro_total']:.2f}) < Limite ({policy.max_loss_diaria:.2f}). CRÍTICA")
        
    # 2. Risco Técnico (CTO Zai)
    if dados['taxa_erros_excecoes'] > policy.max_taxa_erros:
        motivos_stop.append(f"ZAI (Instabilidade): Taxa de Erros ({dados['taxa_erros_excecoes']:.2f}%) > Limite ({policy.max_taxa_erros:.2f}%). CATASTRÓFICA")
        
    # 3. Risco Científico I (CIO Eesek - Rigor)
    if dados['sharpe_ratio'] < policy.min_sharpe_ratio:
        motivos_stop.append(f"EESEK (Sharpe Ratio): Sharpe Ratio ({dados['sharpe_ratio']:.4f}) < Mínimo ({policy.min_sharpe_ratio:.1f}). SISTÊMICA")

    # 4. Risco Científico II (CIO Eesek - Viabilidade)
    if dados['expectativa_matematica_observada'] < policy.min_expectativa_matematica:
        motivos_stop.append(f"CIENTÍFICO (E[X]): Expectativa Matemática ({dados['expectativa_matematica_observada']:.4f}) < Mínimo ({policy.min_expectativa_matematica:.1f}). FUNDAMENTAL")

    
    if motivos_stop:
        decisao = "HARD_STOP_SISTEMICO"
        recomendacao = "PARAR OPERAÇÃO E INICIAR PIVÔ CIENTÍFICO (D.U.D.E. ATIVADO)"
    else:
        decisao = "CONTINUAR_MONITORADO"
        recomendacao = "CONTINUAR OPERAÇÃO COM MONITORAMENTO RIGOROSO"
        
    return {
        "decisao": decisao,
        "recomendacao": recomendacao,
        "motivos_stop": motivos_stop,
    }

# ==============================================================================
# EXECUÇÃO DO PROTOCOLO
# ==============================================================================

def executar_protocolo():
    """Executa a verificação e emite o comando de parada."""
    
    policy = RiskPolicy()
    decisao_block = decidir_operacao(RELATORIO_CIENTIFICO_DADOS_ATUAIS, policy)
    
    relatorio_final = {
        "relatorio_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
        "VERSAO_PROTOCOLO": "V4.0 - Executivo",
        "DECISAO_FINAL_CONSELHO": decisao_block['decisao'],
        "STATUS_OPERACIONAL": "INTERROMPIDO POR ORDEM EXECUTIVA",
        "protocolo_detalhes": {
            "acao_recomendada": decisao_block['recomendacao'],
            "motivos_ativacao_stop": decisao_block['motivos_stop'],
        },
        "dados_criticos_que_ativaram_o_stop": RELATORIO_CIENTIFICO_DADOS_ATUAIS
    }
    
    print("=================================================================")
    print("COMANDO DE EXECUCAO: PROTOCOLO HARD STOP")
    print("=================================================================")
    print(json.dumps(relatorio_final, indent=4, ensure_ascii=False))
    print("=================================================================")
    
    if decisao_block['decisao'] == "HARD_STOP_SISTEMICO":
        print("\n[SUCESSO: Ordem de HARD STOP EXECUTADA. O sistema deve estar PARADO. Iniciar FASE ZERO: DEBUG TÉCNICO.]")
    else:
        print("\n[AVISO: Condições de Hard Stop NÃO ATIVADAS. Monitoramento Continuado.]")
    
    # Salvar relatório em arquivo
    with open("HARD_STOP_RELATORIO.json", "w", encoding="utf-8") as f:
        json.dump(relatorio_final, f, indent=4, ensure_ascii=False)
    
    return relatorio_final

if __name__ == "__main__":
    executar_protocolo()

