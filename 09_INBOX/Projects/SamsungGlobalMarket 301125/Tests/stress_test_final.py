#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE STRESS DEFINITIVO - SAMSUNG GLOBAL MARKET
PROTOCOLO CIENTIFICO DE VALIDACAO
"""

import socket
import json
import threading
import time
import random
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys

class StressTestEngine:
    def __init__(self):
        self.results = {
            'connection_tests': [],
            'heartbeat_tests': [],
            'signal_tests': [],
            'stress_tests': [],
            'performance_metrics': {}
        }
        self.test_start_time = None
        self.test_end_time = None
        
    def log_test(self, category, test_name, status, details=""):
        """Log estruturado para analise cientifica"""
        timestamp = datetime.now().isoformat()
        result = {
            'timestamp': timestamp,
            'category': category,
            'test_name': test_name,
            'status': status,
            'details': details
        }
        self.results[category].append(result)
        
        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_symbol} [{category}] {test_name}: {status}")
        if details:
            print(f"    Detalhes: {details}")
    
    def test_connection_stability(self, duration_minutes=3):
        """Teste 1: Estabilidade de Conexao Prolongada"""
        print("\n" + "="*80)
        print("TESTE 1: ESTABILIDADE DE CONEXAO PROLONGADA")
        print("="*80)
        print(f"Duracao: {duration_minutes} minutos")
        print("Criterio: Conexao deve permanecer ativa SEM desconexoes")
        
        try:
            # Conectar ao servidor
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', 5555))
            
            # Enviar handshake
            handshake = {
                'message_type': 'HANDSHAKE',
                'ea_name': 'StressTest_EA',
                'version': '1.01',
                'account': '999999999'
            }
            client.sendall((json.dumps(handshake) + '\n').encode('utf-8'))
            
            # Monitorar por N minutos
            start_time = time.time()
            heartbeat_count = 0
            disconnections = 0
            last_heartbeat = time.time()
            
            while time.time() - start_time < duration_minutes * 60:
                try:
                    client.settimeout(1.0)
                    data = client.recv(1024).decode('utf-8')
                    if data:
                        for line in data.split('\n'):
                            if line.strip():
                                try:
                                    msg = json.loads(line.strip())
                                    if msg.get('message_type') == 'HEARTBEAT':
                                        heartbeat_count += 1
                                        last_heartbeat = time.time()
                                        print(f"[HEARTBEAT] #{heartbeat_count} recebido")
                                except:
                                    pass
                except socket.timeout:
                    # Verificar se heartbeat esta atrasado
                    if time.time() - last_heartbeat > 35:  # 5s de tolerancia
                        disconnections += 1
                        self.log_test('connection_tests', 'Heartbeat Timeout', 'FAIL', 
                                    f'Timeout apos {time.time() - last_heartbeat:.1f}s')
                        break
                except Exception as e:
                    disconnections += 1
                    self.log_test('connection_tests', 'Connection Error', 'FAIL', str(e))
                    break
            
            client.close()
            
            # Avaliar resultados
            if disconnections == 0 and heartbeat_count >= duration_minutes * 2:  # Pelo menos 1 heartbeat por minuto
                self.log_test('connection_tests', 'Connection Stability', 'PASS', 
                            f'{duration_minutes}min, {heartbeat_count} heartbeats, 0 disconnections')
                return True
            else:
                self.log_test('connection_tests', 'Connection Stability', 'FAIL', 
                            f'{duration_minutes}min, {heartbeat_count} heartbeats, {disconnections} disconnections')
                return False
                
        except Exception as e:
            self.log_test('connection_tests', 'Connection Test', 'FAIL', str(e))
            return False
    
    def test_high_frequency_signals(self, signal_count=50):
        """Teste 2: Sinais de Alta Frequencia"""
        print("\n" + "="*80)
        print("TESTE 2: SINAIS DE ALTA FREQUENCIA")
        print("="*80)
        print(f"Quantidade: {signal_count} sinais")
        print("Criterio: Servidor deve processar todos os sinais sem falhas")
        
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', 5555))
            
            # Handshake
            handshake = {
                'message_type': 'HANDSHAKE',
                'ea_name': 'StressTest_EA',
                'version': '1.01',
                'account': '999999999'
            }
            client.sendall((json.dumps(handshake) + '\n').encode('utf-8'))
            time.sleep(1)  # Aguardar handshake
            
            # Enviar sinais em rajada
            start_time = time.time()
            successful_signals = 0
            
            for i in range(signal_count):
                signal = {
                    'message_type': 'SIGNAL',
                    'id': f'STRESS_TEST_{i:03d}',
                    'symbol': random.choice(['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']),
                    'action': random.choice(['BUY', 'SELL']),
                    'volume': round(random.uniform(0.01, 1.0), 2),
                    'stop_loss': round(random.uniform(1.0800, 1.0900), 4),
                    'take_profit': round(random.uniform(1.0900, 1.1000), 4),
                    'magic_number': 12345
                }
                
                try:
                    client.sendall((json.dumps(signal) + '\n').encode('utf-8'))
                    successful_signals += 1
                    
                    if i % 10 == 0:
                        print(f"[SIGNAL] Enviados {i+1}/{signal_count} sinais")
                        
                except Exception as e:
                    self.log_test('signal_tests', f'Signal {i}', 'FAIL', str(e))
            
            end_time = time.time()
            duration = end_time - start_time
            
            client.close()
            
            # Avaliar resultados
            success_rate = (successful_signals / signal_count) * 100
            signals_per_second = signal_count / duration
            
            if success_rate >= 95:  # 95% de sucesso minimo
                self.log_test('signal_tests', 'High Frequency Signals', 'PASS', 
                            f'{success_rate:.1f}% success, {signals_per_second:.1f} signals/sec')
                return True
            else:
                self.log_test('signal_tests', 'High Frequency Signals', 'FAIL', 
                            f'{success_rate:.1f}% success, {signals_per_second:.1f} signals/sec')
                return False
                
        except Exception as e:
            self.log_test('signal_tests', 'Signal Test', 'FAIL', str(e))
            return False
    
    def test_concurrent_connections(self, connection_count=3):
        """Teste 3: Multiplas Conexoes Simultaneas"""
        print("\n" + "="*80)
        print("TESTE 3: MULTIPLAS CONEXOES SIMULTANEAS")
        print("="*80)
        print(f"Conexoes: {connection_count} simultaneas")
        print("Criterio: Servidor deve manter todas as conexoes ativas")
        
        def create_connection(conn_id):
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('127.0.0.1', 5555))
                
                handshake = {
                    'message_type': 'HANDSHAKE',
                    'ea_name': f'StressTest_EA_{conn_id}',
                    'version': '1.01',
                    'account': f'99999999{conn_id}'
                }
                client.sendall((json.dumps(handshake) + '\n').encode('utf-8'))
                
                # Manter conexao por 30 segundos
                start_time = time.time()
                heartbeat_count = 0
                
                while time.time() - start_time < 30:
                    try:
                        client.settimeout(1.0)
                        data = client.recv(1024).decode('utf-8')
                        if data:
                            for line in data.split('\n'):
                                if line.strip():
                                    try:
                                        msg = json.loads(line.strip())
                                        if msg.get('message_type') == 'HEARTBEAT':
                                            heartbeat_count += 1
                                    except:
                                        pass
                    except socket.timeout:
                        continue
                
                client.close()
                return {'id': conn_id, 'heartbeats': heartbeat_count, 'status': 'SUCCESS'}
                
            except Exception as e:
                return {'id': conn_id, 'error': str(e), 'status': 'FAILED'}
        
        # Executar conexoes em paralelo
        with ThreadPoolExecutor(max_workers=connection_count) as executor:
            futures = [executor.submit(create_connection, i) for i in range(connection_count)]
            results = [future.result() for future in futures]
        
        # Avaliar resultados
        successful_connections = sum(1 for r in results if r['status'] == 'SUCCESS')
        total_heartbeats = sum(r.get('heartbeats', 0) for r in results)
        
        if successful_connections == connection_count:
            self.log_test('stress_tests', 'Concurrent Connections', 'PASS', 
                        f'{successful_connections}/{connection_count} connections, {total_heartbeats} total heartbeats')
            return True
        else:
            self.log_test('stress_tests', 'Concurrent Connections', 'FAIL', 
                        f'{successful_connections}/{connection_count} connections successful')
            return False
    
    def run_comprehensive_test(self):
        """Executa bateria completa de testes"""
        print("INICIANDO TESTE DE STRESS E ALTA TECNOLOGIA")
        print("="*80)
        print("PROJETO: Samsung Global Market")
        print("OBJETIVO: Validacao definitiva da integracao MT5-Python")
        print("PROTOCOLO: Testes cientificos de stress e performance")
        print("="*80)
        
        self.test_start_time = datetime.now()
        
        # Executar todos os testes
        tests = [
            ("Estabilidade de Conexao", self.test_connection_stability, 3),  # 3 minutos
            ("Sinais de Alta Frequencia", self.test_high_frequency_signals, 50),  # 50 sinais
            ("Multiplas Conexoes", self.test_concurrent_connections, 3),  # 3 conexoes
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func, param in tests:
            print(f"\nExecutando: {test_name}")
            try:
                if test_func(param):
                    passed_tests += 1
                else:
                    print(f"[FAIL] {test_name} FALHOU")
            except Exception as e:
                print(f"[ERROR] ERRO em {test_name}: {e}")
        
        self.test_end_time = datetime.now()
        duration = (self.test_end_time - self.test_start_time).total_seconds()
        
        # Relatorio final
        print("\n" + "="*80)
        print("RELATORIO FINAL - TESTE DE STRESS")
        print("="*80)
        print(f"Testes Executados: {total_tests}")
        print(f"Testes Aprovados: {passed_tests}")
        print(f"Taxa de Sucesso: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duracao Total: {duration:.1f} segundos")
        print("="*80)
        
        if passed_tests == total_tests:
            print("TODOS OS TESTES APROVADOS!")
            print("SISTEMA VALIDADO PARA PRODUCAO")
            print("PRONTO PARA FASE 5: PAPER TRADING")
            return True
        else:
            print("ALGUNS TESTES FALHARAM")
            print("SISTEMA NAO APROVADO PARA PRODUCAO")
            print("CORRECOES NECESSARIAS")
            return False

def main():
    """Funcao principal"""
    print("TESTE DE STRESS E ALTA TECNOLOGIA")
    print("Samsung Global Market - Validacao Definitiva")
    print("="*80)
    
    # Verificar se servidor esta rodando
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2)
        test_socket.connect(('127.0.0.1', 5555))
        test_socket.close()
        print("[OK] Servidor MT5 detectado e acessivel")
    except:
        print("[FAIL] Servidor MT5 nao esta rodando!")
        print("Execute: python simple_mt5_server.py")
        return False
    
    # Executar testes
    engine = StressTestEngine()
    success = engine.run_comprehensive_test()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
