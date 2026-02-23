#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualizador de Checklist - AURORA v5.1
Atualiza status dos itens do checklist conforme protocolo de governança

🚨 PROTEÇÃO ANTIFRAUDE INTEGRADA
Este script NÃO permite atualizar status "CONCLUÍDO" sem validação real.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Importar protocolo antifraude
try:
    from PROTOCOLO_ANTIFRAUDE import validar_antes_atualizar_checklist
    PROTOCOLO_ATIVO = True
except ImportError:
    print("⚠️ AVISO: PROTOCOLO_ANTIFRAUDE não encontrado. Executando sem proteção.")
    PROTOCOLO_ATIVO = False

CHECKLIST_FILE = Path(__file__).parent / "CHECKLIST_SISTEMA_AURORA.md"

def atualizar_status_item(item_id: str, novo_status: str, evidencia: str = ""):
    """
    Atualiza status de um item do checklist.
    
    🚨 PROTEÇÃO ANTIFRAUDE: Valida execução real antes de permitir "CONCLUÍDO"
    
    Args:
        item_id: ID do item (ex: CRIT-001)
        novo_status: Novo status (PENDENTE, EM ANDAMENTO, CONCLUÍDO, VALIDADO, BLOQUEADO)
        evidencia: Evidência da conclusão (opcional)
    """
    # 🚨 VALIDAÇÃO ANTIFRAUDE OBRIGATÓRIA
    if PROTOCOLO_ATIVO:
        permitido, mensagem = validar_antes_atualizar_checklist(item_id, novo_status, evidencia)
        if not permitido:
            print("=" * 80)
            print("🚨 BLOQUEADO PELO PROTOCOLO ANTIFRAUDE")
            print("=" * 80)
            print(f"Item: {item_id}")
            print(f"Status solicitado: {novo_status}")
            print(f"Motivo do bloqueio: {mensagem}")
            print("")
            print("❌ ATUALIZAÇÃO NÃO PERMITIDA")
            print("=" * 80)
            return False
    
    if not CHECKLIST_FILE.exists():
        print(f"❌ Checklist não encontrado: {CHECKLIST_FILE}")
        return False
    
    # Ler arquivo
    with open(CHECKLIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Atualizar status na tabela
    pattern = f"\\|\\s*\\d+\\s*\\|\\s*{re.escape(item_id)}\\s*\\|.*?\\|\\s*([^|]+)\\s*\\|"
    replacement = f"| {item_id} | ... | {novo_status} |"
    content = re.sub(pattern, replacement, content)
    
    # Atualizar status na seção detalhada
    section_pattern = f"### {re.escape(item_id)}:.*?\\*\\*Status:\\*\\*\\s*([A-Z_]+)"
    section_replacement = f"### {item_id}: ...\n- **Status:** {novo_status}"
    content = re.sub(section_pattern, section_replacement, content, flags=re.DOTALL)
    
    # Adicionar evidência se fornecida
    if evidencia and novo_status in ["CONCLUÍDO", "VALIDADO"]:
        evidencia_section = f"\n- **Evidência Adicionada:** {evidencia} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        content = re.sub(
            f"(### {re.escape(item_id)}:.*?\\*\\*Status:\\*\\*\\s*{novo_status})",
            f"\\1{evidencia_section}",
            content,
            flags=re.DOTALL
        )
    
    # Atualizar métricas
    status_counts = {
        "PENDENTE": len(re.findall(r'\|\s*PENDENTE\s*\|', content)),
        "EM ANDAMENTO": len(re.findall(r'\|\s*EM ANDAMENTO\s*\|', content)),
        "CONCLUÍDO": len(re.findall(r'\|\s*CONCLUÍDO\s*\|', content)),
        "VALIDADO": len(re.findall(r'\|\s*VALIDADO\s*\|', content)),
        "BLOQUEADO": len(re.findall(r'\|\s*BLOQUEADO\s*\|', content)),
    }
    
    total = sum(status_counts.values())
    metrics_section = f"""### Distribuição por Status:

- **PENDENTE:** {status_counts['PENDENTE']} itens ({status_counts['PENDENTE']/total*100:.1f}%)
- **EM ANDAMENTO:** {status_counts['EM ANDAMENTO']} itens ({status_counts['EM ANDAMENTO']/total*100:.1f}%)
- **CONCLUÍDO:** {status_counts['CONCLUÍDO']} itens ({status_counts['CONCLUÍDO']/total*100:.1f}%)
- **VALIDADO:** {status_counts['VALIDADO']} itens ({status_counts['VALIDADO']/total*100:.1f}%)
- **BLOQUEADO:** {status_counts['BLOQUEADO']} itens ({status_counts['BLOQUEADO']/total*100:.1f}%)"""
    
    content = re.sub(
        r"### Distribuição por Status:.*?- \*\*BLOQUEADO:\*\*.*?%\)",
        metrics_section,
        content,
        flags=re.DOTALL
    )
    
    # Atualizar timestamp
    content = re.sub(
        r"DATA: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        f"DATA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        content
    )
    
    # Salvar
    with open(CHECKLIST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Status de {item_id} atualizado para: {novo_status}")
    return True

def obter_proximo_item():
    """Retorna o próximo item prioritário a ser executado."""
    if not CHECKLIST_FILE.exists():
        return None
    
    with open(CHECKLIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar primeiro item PENDENTE na tabela
    pattern = r'\|\s*(\d+)\s*\|\s*([A-Z]+-\d+)\s*\|.*?\|\s*PENDENTE\s*\|'
    match = re.search(pattern, content)
    
    if match:
        return {
            "number": match.group(1),
            "id": match.group(2),
        }
    
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python ATUALIZAR_CHECKLIST.py <ITEM_ID> <NOVO_STATUS> [EVIDENCIA]")
        print("Exemplo: python ATUALIZAR_CHECKLIST.py CRIT-001 CONCLUÍDO 'BOM removido com sucesso'")
        sys.exit(1)
    
    item_id = sys.argv[1]
    novo_status = sys.argv[2]
    evidencia = sys.argv[3] if len(sys.argv) > 3 else ""
    
    atualizar_status_item(item_id, novo_status, evidencia)
    
    # Mostrar próximo item
    proximo = obter_proximo_item()
    if proximo:
        print(f"\n📋 Próximo item: {proximo['id']} (#{proximo['number']})")

