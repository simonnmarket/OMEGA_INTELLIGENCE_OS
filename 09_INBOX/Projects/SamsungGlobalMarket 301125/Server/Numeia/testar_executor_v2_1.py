#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE COMPLETO: Executor Serial v2.1 - Numeia
Data: 2025-11-21
Protocolo: ASC-AQ (Análise de Sistemas Críticos)

Este script valida TODOS os componentes do executor_serial_v2.py conforme
STATUS_IMPLEMENTACAO_V2.1.md e DIRETIVA_EXECUTIVA_V2.1.md
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import MetaTrader5 as mt5
    import pandas as pd
    from pydantic import ValidationError
except ImportError as e:
    print(f"❌ ERRO: Dependência não instalada: {e}")
    print("Execute: pip install MetaTrader5 pandas pydantic")
    sys.exit(1)

# Caminhos
_BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = str(_BASE_DIR / "config.json")
HEARTBEAT_FILE = Path(__file__).parent / "executor_heartbeat.tmp"
LOG_FILE = Path(__file__).parent / "numeia_execution.jsonl"
EXECUTOR_SCRIPT = Path(__file__).parent / "executor_serial_v2.py"

class TestResult:
    """Armazena resultado de um teste individual"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}
    
    def success(self, message: str = "", details: Dict = None):
        self.passed = True
        self.message = message
        self.details = details or {}
    
    def failure(self, message: str, details: Dict = None):
        self.passed = False
        self.message = message
        self.details = details or {}

class TestSuite:
    """Suite completa de testes para executor_serial_v2.py"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.mt5_initialized = False
    
    def run_all(self) -> bool:
        """Executa todos os testes"""
        print("=" * 80)
        print("TESTE COMPLETO: EXECUTOR SERIAL v2.1 - NUMEIA")
        print("=" * 80)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Protocolo: ASC-AQ (Análise de Sistemas Críticos)")
        print("=" * 80)
        
        # Sequência de testes
        tests = [
            ("Estrutura de Arquivos", self.test_file_structure),
            ("Configuração JSON", self.test_config_json),
            ("Conexão MT5", self.test_mt5_connection),
            ("Validação Config Pydantic", self.test_config_validation),
            ("Geração de Sinais MA", self.test_signal_generation),
            ("Validação de Símbolos", self.test_symbol_validation),
            ("Heartbeat File", self.test_heartbeat_file),
            ("Log File", self.test_log_file),
            ("Estrutura do Executor", self.test_executor_structure),
        ]
        
        for test_name, test_func in tests:
            result = TestResult(test_name)
            try:
                test_func(result)
            except Exception as e:
                result.failure(f"Exceção não tratada: {str(e)}", {"exception": str(e)})
            self.results.append(result)
            self._print_result(result)
        
        # Limpeza
        if self.mt5_initialized:
            mt5.shutdown()
        
        # Resumo final
        return self._print_summary()
    
    def test_file_structure(self, result: TestResult):
        """Teste 1: Verifica se todos os arquivos necessários existem"""
        required_files = {
            "executor_serial_v2.py": EXECUTOR_SCRIPT,
            "config.json": Path(CONFIG_PATH),
        }
        
        missing = []
        for name, path in required_files.items():
            if not path.exists():
                missing.append(name)
        
        if missing:
            result.failure(f"Arquivos faltando: {', '.join(missing)}", {"missing": missing})
        else:
            result.success("Todos os arquivos necessários existem", {
                "files": list(required_files.keys())
            })
    
    def test_config_json(self, result: TestResult):
        """Teste 2: Valida estrutura do config.json"""
        try:
            with open(CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
            
            required_fields = [
                "EXECUTION_CYCLE_SECONDS",
                "TRADING_SYMBOLS",
                "ORDER_VOLUME",
                "MAX_ORDER_ATTEMPTS",
                "MAPeriodFast",
                "MAPeriodSlow"
            ]
            
            missing_fields = [f for f in required_fields if f not in config_data]
            
            if missing_fields:
                result.failure(f"Campos faltando no config.json: {', '.join(missing_fields)}", {
                    "missing": missing_fields
                })
            else:
                result.success("Config.json válido", {
                    "cycle_seconds": config_data.get("EXECUTION_CYCLE_SECONDS"),
                    "symbols_count": len(config_data.get("TRADING_SYMBOLS", [])),
                    "volume": config_data.get("ORDER_VOLUME"),
                    "ma_fast": config_data.get("MAPeriodFast"),
                    "ma_slow": config_data.get("MAPeriodSlow"),
                })
        except FileNotFoundError:
            result.failure(f"Arquivo config.json não encontrado: {CONFIG_PATH}")
        except json.JSONDecodeError as e:
            result.failure(f"Erro ao decodificar JSON: {str(e)}")
        except Exception as e:
            result.failure(f"Erro inesperado: {str(e)}")
    
    def test_mt5_connection(self, result: TestResult):
        """Teste 3: Verifica conexão com MetaTrader 5"""
        try:
            if not mt5.initialize():
                error = mt5.last_error()
                result.failure(f"Falha ao inicializar MT5: {error}", {"error": str(error)})
                return
            
            self.mt5_initialized = True
            
            account_info = mt5.account_info()
            if account_info is None:
                result.failure("Não foi possível obter informações da conta")
                mt5.shutdown()
                self.mt5_initialized = False
                return
            
            terminal_info = mt5.terminal_info()
            if terminal_info is None or not terminal_info.connected:
                result.failure("MT5 não está conectado ao servidor")
                return
            
            result.success("Conexão MT5 estabelecida", {
                "account": account_info.login,
                "server": account_info.server,
                "balance": account_info.balance,
                "connected": terminal_info.connected
            })
        except Exception as e:
            result.failure(f"Erro ao conectar MT5: {str(e)}")
    
    def test_config_validation(self, result: TestResult):
        """Teste 4: Valida configuração usando Pydantic (como no executor)"""
        try:
            # Simula a validação do executor_serial_v2.py
            from pydantic import BaseModel, Field
            
            class Config(BaseModel):
                EXECUTION_CYCLE_SECONDS: int = Field(15, ge=5, le=600)
                TRADING_SYMBOLS: List[str] = Field(default_factory=lambda: ["EURUSD"])
                ORDER_VOLUME: float = Field(0.01)
                MAX_ORDER_ATTEMPTS: int = Field(3)
                MAPeriodFast: int = Field(20)
                MAPeriodSlow: int = Field(50)
            
            with open(CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
            
            config = Config(**config_data)
            
            result.success("Configuração validada com Pydantic", {
                "cycle_seconds": config.EXECUTION_CYCLE_SECONDS,
                "symbols": config.TRADING_SYMBOLS,
                "volume": config.ORDER_VOLUME,
            })
        except ValidationError as e:
            result.failure(f"Erro de validação Pydantic: {str(e)}", {"errors": str(e)})
        except Exception as e:
            result.failure(f"Erro ao validar config: {str(e)}")
    
    def test_signal_generation(self, result: TestResult):
        """Teste 5: Testa geração de sinais baseada em MA20/MA50"""
        if not self.mt5_initialized:
            result.failure("MT5 não inicializado - pulando teste")
            return
        
        try:
            # Carrega config
            with open(CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
            
            symbols = config_data.get("TRADING_SYMBOLS", [])[:3]  # Testa apenas 3 primeiros
            ma_fast = config_data.get("MAPeriodFast", 20)
            ma_slow = config_data.get("MAPeriodSlow", 50)
            
            signals_found = 0
            symbols_tested = 0
            errors = []
            
            for symbol in symbols:
                try:
                    # Obtém dados (mesma lógica do executor)
                    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
                    if rates is None or len(rates) < ma_slow:
                        errors.append(f"{symbol}: Dados insuficientes ({len(rates) if rates else 0} candles)")
                        continue
                    
                    df = pd.DataFrame(rates)
                    df['ma_fast'] = df['close'].rolling(window=ma_fast).mean()
                    df['ma_slow'] = df['close'].rolling(window=ma_slow).mean()
                    
                    if len(df) < 2 or df.iloc[-2:]['ma_fast'].isna().any() or df.iloc[-2:]['ma_slow'].isna().any():
                        errors.append(f"{symbol}: MAs não prontas")
                        continue
                    
                    symbols_tested += 1
                    
                    # Verifica cruzamento (mesma lógica do executor)
                    prev_fast = df.iloc[-2]['ma_fast']
                    prev_slow = df.iloc[-2]['ma_slow']
                    curr_fast = df.iloc[-1]['ma_fast']
                    curr_slow = df.iloc[-1]['ma_slow']
                    
                    if prev_fast < prev_slow and curr_fast > curr_slow:
                        signals_found += 1
                    elif prev_fast > prev_slow and curr_fast < curr_slow:
                        signals_found += 1
                
                except Exception as e:
                    errors.append(f"{symbol}: {str(e)}")
            
            if symbols_tested == 0:
                result.failure("Nenhum símbolo pôde ser testado", {"errors": errors})
            else:
                result.success(f"Geração de sinais funcionando ({signals_found} sinais em {symbols_tested} símbolos)", {
                    "signals_found": signals_found,
                    "symbols_tested": symbols_tested,
                    "errors": errors if errors else None
                })
        except Exception as e:
            result.failure(f"Erro ao testar geração de sinais: {str(e)}")
    
    def test_symbol_validation(self, result: TestResult):
        """Teste 6: Valida se símbolos estão disponíveis no MT5"""
        if not self.mt5_initialized:
            result.failure("MT5 não inicializado - pulando teste")
            return
        
        try:
            with open(CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
            
            symbols = config_data.get("TRADING_SYMBOLS", [])
            available = []
            unavailable = []
            
            for symbol in symbols:
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    unavailable.append(symbol)
                elif not symbol_info.visible:
                    unavailable.append(f"{symbol} (não visível)")
                else:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick and tick.ask > 0:
                        available.append(symbol)
                    else:
                        unavailable.append(f"{symbol} (sem tick)")
            
            if unavailable:
                result.failure(f"{len(unavailable)} símbolos indisponíveis", {
                    "available": available,
                    "unavailable": unavailable
                })
            else:
                result.success(f"Todos os {len(available)} símbolos disponíveis", {
                    "symbols": available
                })
        except Exception as e:
            result.failure(f"Erro ao validar símbolos: {str(e)}")
    
    def test_heartbeat_file(self, result: TestResult):
        """Teste 7: Verifica se heartbeat file pode ser criado/atualizado"""
        try:
            # Tenta criar/atualizar heartbeat (mesma lógica do executor)
            with open(HEARTBEAT_FILE, 'w') as f:
                f.write(str(time.time()))
            
            if not HEARTBEAT_FILE.exists():
                result.failure("Heartbeat file não foi criado")
                return
            
            # Verifica se pode ler
            with open(HEARTBEAT_FILE, 'r') as f:
                timestamp = f.read().strip()
            
            if not timestamp:
                result.failure("Heartbeat file está vazio")
                return
            
            # Verifica se é um número válido
            try:
                float(timestamp)
                result.success("Heartbeat file funcionando", {
                    "file": str(HEARTBEAT_FILE),
                    "timestamp": timestamp
                })
            except ValueError:
                result.failure("Heartbeat file contém valor inválido")
        except Exception as e:
            result.failure(f"Erro ao testar heartbeat: {str(e)}")
    
    def test_log_file(self, result: TestResult):
        """Teste 8: Verifica se log file pode ser criado/escrito"""
        try:
            # Tenta escrever um log de teste
            test_log = {
                "time": datetime.now().isoformat(),
                "level": "INFO",
                "message": json.dumps({"event": "test_log", "test": True})
            }
            
            with open(LOG_FILE, 'a') as f:
                f.write(f'{{"time":"{test_log["time"]}","level":"{test_log["level"]}","message":{test_log["message"]}}}\n')
            
            if not LOG_FILE.exists():
                result.failure("Log file não foi criado")
                return
            
            # Verifica se pode ler
            if LOG_FILE.stat().st_size > 0:
                with open(LOG_FILE, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        try:
                            json.loads(last_line)
                            result.success("Log file funcionando", {
                                "file": str(LOG_FILE),
                                "size_bytes": LOG_FILE.stat().st_size,
                                "lines": len(lines)
                            })
                        except json.JSONDecodeError:
                            result.failure("Log file contém JSON inválido")
                    else:
                        result.failure("Log file está vazio")
            else:
                result.success("Log file criado (vazio)", {"file": str(LOG_FILE)})
        except Exception as e:
            result.failure(f"Erro ao testar log file: {str(e)}")
    
    def test_executor_structure(self, result: TestResult):
        """Teste 9: Valida estrutura do código executor_serial_v2.py"""
        try:
            with open(EXECUTOR_SCRIPT, 'r', encoding='utf-8') as f:
                code = f.read()
            
            required_functions = [
                "check_mt5_connection",
                "generate_real_signals",
                "send_order",
                "update_heartbeat",
                "signal_handler"
            ]
            
            required_imports = [
                "MetaTrader5",
                "pandas",
                "pydantic"
            ]
            
            missing_functions = [f for f in required_functions if f"def {f}" not in code]
            missing_imports = [i for i in required_imports if i.lower() not in code.lower()]
            
            # Verifica se tem loop principal
            has_main_loop = "while True" in code or "__main__" in code
            
            if missing_functions or missing_imports or not has_main_loop:
                issues = []
                if missing_functions:
                    issues.append(f"Funções faltando: {', '.join(missing_functions)}")
                if missing_imports:
                    issues.append(f"Imports faltando: {', '.join(missing_imports)}")
                if not has_main_loop:
                    issues.append("Loop principal não encontrado")
                
                result.failure("; ".join(issues), {
                    "missing_functions": missing_functions,
                    "missing_imports": missing_imports,
                    "has_main_loop": has_main_loop
                })
            else:
                result.success("Estrutura do executor válida", {
                    "functions": required_functions,
                    "imports": required_imports,
                    "has_main_loop": True
                })
        except Exception as e:
            result.failure(f"Erro ao validar estrutura: {str(e)}")
    
    def _print_result(self, result: TestResult):
        """Imprime resultado de um teste"""
        status = "✅ PASSOU" if result.passed else "❌ FALHOU"
        print(f"\n[{len(self.results)}] {result.name}: {status}")
        print(f"    {result.message}")
        if result.details and not result.passed:
            for key, value in result.details.items():
                if value:
                    print(f"    - {key}: {value}")
    
    def _print_summary(self) -> bool:
        """Imprime resumo final e retorna True se todos passaram"""
        print("\n" + "=" * 80)
        print("RESUMO DOS TESTES")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print(f"Total: {total} testes")
        print(f"Passou: {passed} ✅")
        print(f"Falhou: {total - passed} ❌")
        print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n✅ TODOS OS TESTES PASSARAM - SISTEMA PRONTO PARA EXECUÇÃO")
            print("=" * 80)
            return True
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM - REVISAR ANTES DE EXECUTAR")
            print("=" * 80)
            failed = [r.name for r in self.results if not r.passed]
            print(f"Testes que falharam: {', '.join(failed)}")
            return False

if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run_all()
    sys.exit(0 if success else 1)

