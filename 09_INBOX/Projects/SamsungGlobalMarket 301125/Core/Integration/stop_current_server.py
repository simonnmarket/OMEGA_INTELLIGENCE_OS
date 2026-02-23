# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 1.1
Parar Servidor Atual

FUNÇÃO: _stop_current_server()
OBJETIVO: Parar processo SERVIDOR_COMPLETO_FINAL.py com segurança
TESTÁVEL: Sim - retorna True/False
"""

import subprocess
import logging
import time
import psutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _stop_current_server() -> bool:
    """
    Parar o processo do servidor atual (SERVIDOR_COMPLETO_FINAL.py)
    
    Returns:
        bool: True se parou com sucesso, False se falhou ou não encontrado
    
    VALIDAÇÃO:
    - Verifica se processo existe
    - Tenta parar com segurança
    - Confirma que processo realmente parou
    - Registra todas as ações
    """
    try:
        logger.info("="*80)
        logger.info("FASE 1.1: Parando servidor atual")
        logger.info("="*80)
        
        # Lista de nomes de servidores que podem estar rodando
        server_names = [
            'SERVIDOR_COMPLETO_FINAL.py',
            'crypto_FORCA_TOTAL_v3_3.py',
            'crypto_simple_FUNCIONAL.py',
            'crypto_URGENTE_OPERACIONAL.py'
        ]
        
        processes_stopped = 0
        
        # Procurar processos Python
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Verificar se é processo Python
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    
                    # Verificar se é um dos nossos servidores
                    for server_name in server_names:
                        if cmdline and any(server_name in arg for arg in cmdline):
                            pid = proc.info['pid']
                            logger.info(f"Encontrado servidor: {server_name} (PID: {pid})")
                            
                            # Parar processo
                            process = psutil.Process(pid)
                            process.terminate()  # Tentar terminar gracefully
                            
                            # Aguardar até 5 segundos
                            try:
                                process.wait(timeout=5)
                                logger.info(f"  ✅ Servidor {server_name} (PID: {pid}) parado com sucesso")
                                processes_stopped += 1
                            except psutil.TimeoutExpired:
                                # Se não parou, forçar
                                logger.warning(f"  ⚠️ Servidor não parou gracefully - forçando...")
                                process.kill()
                                time.sleep(1)
                                logger.info(f"  ✅ Servidor {server_name} (PID: {pid}) forçado a parar")
                                processes_stopped += 1
                            
                            break  # Encontrou e parou
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Verificar resultado
        if processes_stopped > 0:
            logger.info(f"✅ Total de {processes_stopped} servidor(es) parado(s)")
            
            # Validar que realmente pararam
            time.sleep(2)
            still_running = _check_servers_still_running(server_names)
            
            if still_running:
                logger.error(f"❌ FALHA: {len(still_running)} servidor(es) ainda rodando: {still_running}")
                return False
            else:
                logger.info("✅ VALIDAÇÃO: Nenhum servidor rodando")
                return True
        else:
            logger.info("ℹ️ Nenhum servidor encontrado rodando")
            return True  # True porque objetivo foi alcançado (nenhum servidor ativo)
    
    except Exception as e:
        logger.error(f"❌ ERRO ao parar servidor: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def _check_servers_still_running(server_names: list) -> list:
    """
    Verificar se algum servidor ainda está rodando
    
    Args:
        server_names: Lista de nomes de servidores para verificar
    
    Returns:
        list: Lista de servidores ainda rodando (vazia se nenhum)
    """
    still_running = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                
                for server_name in server_names:
                    if cmdline and any(server_name in arg for arg in cmdline):
                        still_running.append(f"{server_name} (PID: {proc.info['pid']})")
        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return still_running

# =====================================================
# TESTE DA FUNÇÃO
# =====================================================

def test_stop_server():
    """
    Teste para validar que o servidor foi parado
    
    Returns:
        dict: Resultado do teste com status e detalhes
    """
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _stop_current_server()")
    logger.info("="*80)
    
    # Executar função
    result = _stop_current_server()
    
    # Validar resultado
    test_result = {
        'function': '_stop_current_server()',
        'passed': result,
        'timestamp': datetime.now().isoformat(),
        'details': {}
    }
    
    if result:
        test_result['details']['message'] = "Servidor(es) parado(s) com sucesso ou nenhum servidor encontrado"
        test_result['details']['validation'] = "Nenhum processo servidor detectado após parada"
        logger.info("✅ TESTE PASSOU")
    else:
        test_result['details']['message'] = "Falha ao parar servidor(es)"
        test_result['details']['validation'] = "Processo(s) ainda rodando ou erro"
        logger.error("❌ TESTE FALHOU")
    
    logger.info("="*80)
    
    return test_result

if __name__ == "__main__":
    """Executar teste quando rodar este arquivo"""
    from datetime import datetime
    
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 1.1")
    print("Função: _stop_current_server()")
    print("="*80 + "\n")
    
    # Executar teste
    result = test_stop_server()
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print("="*80)
    print(f"Função: {result['function']}")
    print(f"Passou: {result['passed']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Detalhes: {result['details']}")
    print("="*80 + "\n")
    
    # Salvar resultado
    import json
    with open('test_result_phase_1_1.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Resultado salvo em: test_result_phase_1_1.json\n")

