import json
import os
import re
import shutil
from datetime import datetime

def create_backup(filepath):
    """Cria um backup do arquivo original com timestamp."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo crítico não encontrado: {filepath}")
    
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(filepath)
    backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
    
    shutil.copy2(filepath, backup_path)
    print(f"[OK] Backup criado: {backup_path}")
    return backup_path

def remove_keys_from_dict(filepath, dict_name, keys_to_remove):
    """Remove chaves de um dicionário em um arquivo Python."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    inside_target_dict = False
    indent_level = 0

    for line in lines:
        stripped_line = line.strip()
        # Detecta o início do dicionário alvo
        if f"{dict_name} = {{" in stripped_line or f"{dict_name}={{" in stripped_line:
            inside_target_dict = True
            indent_level = len(line) - len(line.lstrip())
            new_lines.append(line)
            continue
        
        # Detecta o fim do dicionário
        if inside_target_dict and stripped_line == "}" and (len(line) - len(line.lstrip()) == indent_level):
            inside_target_dict = False
            new_lines.append(line)
            continue

        # Se estiver dentro do dicionário, verifica se a linha contém uma chave a ser removida
        if inside_target_dict:
            should_remove = False
            for key in keys_to_remove:
                # Procura por padrões como 'key': ou "key":
                if re.match(rf'^\s*["\']?{re.escape(key)}["\']?\s*:', stripped_line):
                    should_remove = True
                    print(f"  - Removendo chave: '{key}'")
                    break
            if not should_remove:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"[OK] Chaves removidas de '{dict_name}' em {filepath}")

def update_dict_values(filepath, dict_name, new_allocation):
    """Atualiza os valores de chaves específicas em um dicionário."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_content = content
    for key, new_value in new_allocation.items():
        # Regex para encontrar 'key': Decimal('old_value') e substituir
        pattern = rf"(\s*['\"]?{re.escape(key)}['\"]?\s*:\s*)Decimal\(['\"][\d,\.]+['\"]\)"
        replacement = f"\\1{new_value}"
        if re.search(pattern, updated_content):
            updated_content = re.sub(pattern, replacement, updated_content)
            print(f"  - Atualizando '{key}' para {new_value}")
        else:
            print(f"  - AVISO: Chave '{key}' não encontrada para atualização.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"[OK] Valores atualizados em '{dict_name}' em {filepath}")

def validate_allocation_sum(new_allocation, expected_sum_str):
    """Valida se a soma da nova alocação corresponde ao esperado."""
    from decimal import Decimal
    
    # Extrair valores numéricos dos strings Decimal
    total_sum = Decimal('0')
    for val in new_allocation.values():
        # Extrair número de dentro de Decimal('...')
        match = re.search(r"Decimal\(['\"](\d+)['\"]", val)
        if match:
            total_sum += Decimal(match.group(1))
    
    expected = Decimal(expected_sum_str)
    if total_sum != expected:
        raise ValueError(f"VALIDACAO FALHOU: A soma da nova alocacao ({total_sum}) nao e igual ao esperado ({expected}).")
    print(f"[OK] Validacao de soma de capital passou: {total_sum}")

def execute_directive(directive_path):
    """Função principal que lê e executa a diretiva."""
    print(">>> INICIANDO EXECUÇÃO DA DIRETIVA...")
    
    with open(directive_path, 'r', encoding='utf-8') as f:
        directive = json.load(f)

    print(f"ID da Diretiva: {directive['directive_id']}")
    print(f"Descrição: {directive['description']}\n")

    # --- Pré-execução Check ---
    print("--- FASE 1: VERIFICACAO PRE-EXECUCAO ---")
    for file_path in directive['pre_execution_check']['target_files_exist']:
        if not os.path.exists(file_path):
            print(f"[ERRO] Arquivo de destino nao encontrado: {file_path}")
            return
    print("[OK] Todos os arquivos de destino existem.\n")

    # --- Execucao das Acoes ---
    print("--- FASE 2: EXECUCAO DAS ACOES ---")
    for action in directive['actions']:
        print(f"Executando AÇÃO ID: {action['action_id']} - {action['description']}")
        target_file = action['target_file']
        create_backup(target_file)

        if action['type'] == 'REMOVE_FROM_STRATEGY_MAP' or action['type'] == 'DISABLE_FROM_STRATEGY_MAP':
            remove_keys_from_dict(
                filepath=target_file,
                dict_name=action['target_structure']['name'],
                keys_to_remove=action['keys_to_remove']
            )
        elif action['type'] == 'REALLOCATE_CAPITAL':
            validate_allocation_sum(action['new_allocation'], "500000")
            update_dict_values(
                filepath=target_file,
                dict_name=action['target_structure']['name'],
                new_allocation=action['new_allocation']
            )
        print("-" * 20)
    
    # --- Pos-execucao Report ---
    print("--- FASE 3: RELATORIO POS-EXECUCAO ---")
    log_file = "EXECUTION_LOG_F1-T3.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Log de Execução da Diretiva {directive['directive_id']}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("Ações executadas conforme descrito no arquivo JSON.\n")
        f.write("\nArquivos modificados:\n")
        for action in directive['actions']:
            f.write(f"  - {action['target_file']}\n")
    print(f"[OK] Relatorio de execucao salvo em {log_file}")
    print("\n>>> DIRETIVA EXECUTADA COM SUCESSO.")

if __name__ == "__main__":
    # O AIC deve executar este script a partir da linha de comando
    # Exemplo: python execute_directive.py AIC_DIRECTIVE_FASE1_T3_LIMPEZA.json
    import sys
    if len(sys.argv) != 2:
        print("Uso: python execute_directive.py <caminho_para_o_json>")
    else:
        execute_directive(sys.argv[1])

