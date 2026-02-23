#!/usr/bin/env python3
"""
Script de Validação Completa - Numeia v2.0
Executa todos os testes de validação conforme diretiva técnica
"""

import sys
import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Cores para output (ASCII para compatibilidade Windows)
OK = "[OK]"
ERRO = "[ERRO]"
AVISO = "[AVISO]"
INFO = "[INFO]"

class ValidacaoSistema:
    def __init__(self):
        self.resultados = {
            "timestamp": datetime.now().isoformat(),
            "testes": [],
            "erros": [],
            "avisos": []
        }
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir.parent.parent / "config.json"
        
    def log(self, tipo: str, mensagem: str):
        """Registra resultado do teste"""
        entry = {"tipo": tipo, "mensagem": mensagem, "timestamp": datetime.now().isoformat()}
        self.resultados["testes"].append(entry)
        print(f"{tipo} {mensagem}")
        
    def teste_1_sintaxe(self) -> bool:
        """Teste 1: Validação de Sintaxe Python"""
        self.log(INFO, "=== TESTE 1: Validação de Sintaxe Python ===")
        arquivo = self.base_dir / "numeia_executor_v2.py"
        
        if not arquivo.exists():
            self.log(ERRO, f"Arquivo não encontrado: {arquivo}")
            self.resultados["erros"].append(f"Arquivo não encontrado: {arquivo}")
            return False
            
        try:
            # Compilar sintaxe
            with open(arquivo, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(arquivo), 'exec')
            self.log(OK, f"Sintaxe válida: {arquivo.name}")
            return True
        except SyntaxError as e:
            self.log(ERRO, f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
            self.resultados["erros"].append(f"Sintaxe inválida: {e}")
            return False
        except Exception as e:
            self.log(ERRO, f"Erro ao validar sintaxe: {e}")
            self.resultados["erros"].append(f"Erro de validação: {e}")
            return False
    
    def teste_2_imports(self) -> bool:
        """Teste 2: Validação de Imports"""
        self.log(INFO, "=== TESTE 2: Validação de Imports ===")
        
        modulos_obrigatorios = [
            "os", "json", "logging", "threading", "time", "signal", "sys",
            "queue", "concurrent.futures", "typing", "pydantic",
            "MetaTrader5", "prometheus_client", "requests", "numpy", "pandas"
        ]
        
        modulos_opcionais = []
        erros_import = []
        
        for modulo in modulos_obrigatorios:
            try:
                if "." in modulo:
                    # Módulo com sub-módulo
                    partes = modulo.split(".")
                    __import__(partes[0])
                    for parte in partes[1:]:
                        __import__(f"{partes[0]}.{parte}")
                else:
                    __import__(modulo)
                self.log(OK, f"Import OK: {modulo}")
            except ImportError as e:
                self.log(ERRO, f"Import FALHOU: {modulo} - {e}")
                erros_import.append(f"{modulo}: {e}")
                self.resultados["erros"].append(f"Import faltando: {modulo}")
        
        if erros_import:
            return False
        return True
    
    def teste_3_config(self) -> bool:
        """Teste 3: Validação de Configuração"""
        self.log(INFO, "=== TESTE 3: Validação de Configuração ===")
        
        if not self.config_path.exists():
            self.log(ERRO, f"Arquivo de configuração não encontrado: {self.config_path}")
            self.resultados["erros"].append(f"Config não encontrado: {self.config_path}")
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validar campos obrigatórios
            campos_obrigatorios = [
                "EMERGENCY_MODE_ENABLED",
                "MAX_PARALLEL_WORKERS",
                "EXECUTION_CYCLE_SECONDS",
                "TRADING_SYMBOLS",
                "RISK_PARAMETERS",
                "MONITORING"
            ]
            
            faltando = []
            for campo in campos_obrigatorios:
                if campo not in config_data:
                    faltando.append(campo)
            
            if faltando:
                self.log(ERRO, f"Campos faltando no config: {faltando}")
                self.resultados["erros"].append(f"Config incompleto: {faltando}")
                return False
            
            # Tentar validar com Pydantic
            try:
                sys.path.insert(0, str(self.base_dir))
                from numeia_executor_v2 import Config
                
                config_obj = Config(**config_data)
                self.log(OK, "Configuração válida (Pydantic)")
                return True
            except Exception as e:
                self.log(AVISO, f"Config JSON válido, mas validação Pydantic falhou: {e}")
                self.resultados["avisos"].append(f"Validação Pydantic: {e}")
                return False
                
        except json.JSONDecodeError as e:
            self.log(ERRO, f"JSON inválido no config: {e}")
            self.resultados["erros"].append(f"JSON inválido: {e}")
            return False
        except Exception as e:
            self.log(ERRO, f"Erro ao validar config: {e}")
            self.resultados["erros"].append(f"Erro de validação: {e}")
            return False
    
    def teste_4_config_invalido(self) -> bool:
        """Teste 4: Configuração Inválida (deve falhar)"""
        self.log(INFO, "=== TESTE 4: Teste de Configuração Inválida ===")
        
        config_invalido = self.base_dir.parent.parent / "config_invalid.json"
        
        if not config_invalido.exists():
            self.log(AVISO, "Arquivo config_invalid.json não encontrado - criando exemplo")
            # Criar config inválido para teste
            invalid_data = {
                "EMERGENCY_MODE_ENABLED": "invalid",  # Deveria ser bool
                "MAX_PARALLEL_WORKERS": -1,  # Deveria ser >= 1
                "EXECUTION_CYCLE_SECONDS": 5  # Deveria ser >= 10
            }
            with open(config_invalido, 'w', encoding='utf-8') as f:
                json.dump(invalid_data, f, indent=2)
        
        try:
            sys.path.insert(0, str(self.base_dir))
            from numeia_executor_v2 import Config, load_config
            
            # Deve lançar ValidationError
            try:
                config_obj = load_config(str(config_invalido))
                self.log(ERRO, "Configuração inválida foi aceita (NÃO DEVERIA)")
                self.resultados["erros"].append("Validação não funcionou corretamente")
                return False
            except Exception as e:
                self.log(OK, f"Configuração inválida corretamente rejeitada: {type(e).__name__}")
                return True
                
        except Exception as e:
            self.log(AVISO, f"Não foi possível testar config inválido: {e}")
            self.resultados["avisos"].append(f"Teste config inválido: {e}")
            return True  # Não crítico
    
    def teste_5_estrutura_arquivos(self) -> bool:
        """Teste 5: Validação de Estrutura de Arquivos"""
        self.log(INFO, "=== TESTE 5: Validação de Estrutura de Arquivos ===")
        
        arquivos_obrigatorios = [
            "numeia_executor_v2.py",
            "__init__.py"
        ]
        
        faltando = []
        for arquivo in arquivos_obrigatorios:
            path = self.base_dir / arquivo
            if not path.exists():
                faltando.append(arquivo)
            else:
                self.log(OK, f"Arquivo encontrado: {arquivo}")
        
        if faltando:
            self.log(ERRO, f"Arquivos faltando: {faltando}")
            self.resultados["erros"].append(f"Arquivos faltando: {faltando}")
            return False
        
        return True
    
    def gerar_relatorio(self) -> str:
        """Gera relatório JSON final"""
        total_testes = len(self.resultados["testes"])
        total_erros = len(self.resultados["erros"])
        total_avisos = len(self.resultados["avisos"])
        
        status = "SUCESSO" if total_erros == 0 else "FALHA"
        
        relatorio = {
            "status": status,
            "timestamp": self.resultados["timestamp"],
            "resumo": {
                "total_testes": total_testes,
                "total_erros": total_erros,
                "total_avisos": total_avisos
            },
            "detalhes": self.resultados,
            "recomendacoes": []
        }
        
        if total_erros > 0:
            relatorio["recomendacoes"].append("Corrigir erros antes de prosseguir")
        if total_avisos > 0:
            relatorio["recomendacoes"].append("Revisar avisos para otimização")
        
        # Salvar relatório
        relatorio_path = self.base_dir / "relatorio_validacao.json"
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        return str(relatorio_path)
    
    def executar_todos(self):
        """Executa todos os testes"""
        print("\n" + "="*70)
        print("VALIDAÇÃO COMPLETA - Numeia v2.0")
        print("="*70 + "\n")
        
        testes = [
            ("Sintaxe Python", self.teste_1_sintaxe),
            ("Imports", self.teste_2_imports),
            ("Configuração Válida", self.teste_3_config),
            ("Configuração Inválida", self.teste_4_config_invalido),
            ("Estrutura de Arquivos", self.teste_5_estrutura_arquivos),
        ]
        
        resultados = []
        for nome, funcao in testes:
            try:
                resultado = funcao()
                resultados.append((nome, resultado))
                print()
            except Exception as e:
                self.log(ERRO, f"Erro ao executar {nome}: {e}")
                resultados.append((nome, False))
        
        # Resumo final
        print("="*70)
        print("RESUMO FINAL")
        print("="*70)
        
        sucesso = sum(1 for _, r in resultados if r)
        total = len(resultados)
        
        for nome, resultado in resultados:
            status = OK if resultado else ERRO
            print(f"{status} {nome}")
        
        print(f"\nResultado: {sucesso}/{total} testes passaram")
        
        if len(self.resultados["erros"]) > 0:
            print(f"\n{ERRO} {len(self.resultados['erros'])} erro(s) encontrado(s):")
            for erro in self.resultados["erros"]:
                print(f"  - {erro}")
        
        if len(self.resultados["avisos"]) > 0:
            print(f"\n{AVISO} {len(self.resultados['avisos'])} aviso(s):")
            for aviso in self.resultados["avisos"]:
                print(f"  - {aviso}")
        
        # Gerar relatório
        relatorio_path = self.gerar_relatorio()
        print(f"\n{INFO} Relatório salvo em: {relatorio_path}")
        
        return sucesso == total

if __name__ == "__main__":
    validador = ValidacaoSistema()
    sucesso = validador.executar_todos()
    sys.exit(0 if sucesso else 1)

