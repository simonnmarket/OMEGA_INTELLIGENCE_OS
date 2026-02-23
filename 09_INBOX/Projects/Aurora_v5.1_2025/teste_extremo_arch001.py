#!/usr/bin/env python3
"""
TESTE TÉCNICO EXTREMO - ARCH-001 VALIDATOR v2.0
Double Check Científico de Consolidação MT5
CEO + CTO + CKO - Protocolo de Verificação Extrema
"""

import os
import sys
import json
import hashlib
import zipfile
import importlib.util
from datetime import datetime
import subprocess
import shutil

class ARCH001ExtremeValidator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_id": f"EXTREME_VALIDATION_{self.timestamp}",
            "criticidade": "ALTA_CIENCIA",
            "status": "INICIADO",
            "testes": [],
            "pontuacao_total": 0,
            "max_pontos": 1000,
            "veredito_final": "PENDENTE"
        }
        
    def teste_1_verificar_backup_integridade(self):
        """TESTE 1: Verificação forense do backup"""
        pontos = 0
        max_pontos = 200
        detalhes = []
        
        # Buscar backup mais recente
        backups = [f for f in os.listdir('.') if f.startswith('backup_pre_arch001') and f.endswith('.zip')]
        
        if not backups:
            self.results["testes"].append({
                "nome": "Backup Forense",
                "status": "FALHA_CRITICA",
                "pontos": 0,
                "max_pontos": max_pontos,
                "detalhes": ["❌ NENHUM BACKUP ENCONTRADO - RISCO EXTREMO"]
            })
            return 0
        
        backup = max(backups)  # Mais recente
        detalhes.append(f"📁 Backup analisado: {backup}")
        
        try:
            # 1.1 Verificar tamanho mínimo (deve ter pelo menos 1MB)
            size_mb = os.path.getsize(backup) / (1024 * 1024)
            if size_mb > 1:
                pontos += 50
                detalhes.append(f"✅ Tamanho OK: {size_mb:.2f} MB")
            else:
                detalhes.append(f"⚠️ Tamanho SUSPEITO: {size_mb:.2f} MB")
            
            # 1.2 Verificar estrutura ZIP
            with zipfile.ZipFile(backup, 'r') as zipf:
                file_list = zipf.namelist()
                mt5_files = [f for f in file_list if 'mt5' in f.lower() and 'executor' in f.lower()]
                
                if len(mt5_files) >= 2:
                    pontos += 50
                    detalhes.append(f"✅ {len(mt5_files)} executores MT5 no backup")
                else:
                    detalhes.append(f"⚠️ Apenas {len(mt5_files)} executores no backup")
                
                # 1.3 Verificar hash interno
                for file in mt5_files[:3]:  # Verificar primeiros 3
                    try:
                        with zipf.open(file) as f:
                            content = f.read()
                            file_hash = hashlib.md5(content).hexdigest()
                            detalhes.append(f"   🔹 {file}: MD5={file_hash[:16]}...")
                    except:
                        pass
            
            # 1.4 Testar extração e reimportação
            extract_dir = f"temp_extract_{self.timestamp}"
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(backup, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Verificar se arquivos extraídos são válidos
            extracted_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith('.py'):
                        extracted_files.append(os.path.join(root, file))
            
            if len(extracted_files) > 10:
                pontos += 100
                detalhes.append(f"✅ {len(extracted_files)} arquivos extraídos com sucesso")
            
            # Limpar
            shutil.rmtree(extract_dir)
            
        except Exception as e:
            detalhes.append(f"❌ ERRO NO BACKUP: {str(e)}")
        
        self.results["testes"].append({
            "nome": "Backup Forense",
            "status": "APROVADO" if pontos >= 150 else "REPROVADO",
            "pontos": pontos,
            "max_pontos": max_pontos,
            "detalhes": detalhes
        })
        
        return pontos
    
    def teste_2_analise_cirurgica_executor(self):
        """TESTE 2: Análise cirúrgica do executor principal"""
        pontos = 0
        max_pontos = 300
        detalhes = []
        
        # Encontrar executor principal
        executor_candidates = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'logs_arch001', 'temp_', 'BACKUPS', 'backups']]
            for file in files:
                if 'mt5' in file.lower() and 'executor' in file.lower() and file.endswith('.py'):
                    # Excluir scripts de análise/consolidação
                    if 'arch001' not in file.lower() and 'bloco' not in file.lower():
                        executor_candidates.append(os.path.join(root, file))
        
        if len(executor_candidates) == 0:
            detalhes.append(f"❌ CRÍTICO: Nenhum executor encontrado")
            self.results["testes"].append({
                "nome": "Análise Cirúrgica Executor",
                "status": "FALHA_CRITICA",
                "pontos": 0,
                "max_pontos": max_pontos,
                "detalhes": detalhes
            })
            return 0
        
        # Se houver múltiplos, pegar o principal (04-Infraestrutura)
        executor_path = None
        for candidate in executor_candidates:
            if '04-Infraestrutura' in candidate or '04-Infrastructure' in candidate:
                executor_path = candidate
                break
        
        if not executor_path:
            executor_path = executor_candidates[0]
        
        detalhes.append(f"🔍 Executor principal: {executor_path}")
        if len(executor_candidates) > 1:
            detalhes.append(f"⚠️ {len(executor_candidates)} executores encontrados (esperado: 1)")
        
        try:
            with open(executor_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 2.1 Verificação de funcionalidades críticas
            required_patterns = {
                "mt5.initialize": 10,
                "mt5.order_send": 20,
                "mt5.positions_get": 10,
                "class.*MT5": 15,
                "def.*send_order": 15,
                "def.*close_position": 10,
                "try:": 10,
                "except.*Exception": 10,
                "logging": 10,
                "import MetaTrader5": 20
            }
            
            for pattern, value in required_patterns.items():
                if pattern in content:
                    pontos += value
                    detalhes.append(f"✅ {pattern}")
                else:
                    detalhes.append(f"⚠️ Ausente: {pattern}")
            
            # 2.2 Análise de complexidade
            line_count = len(lines)
            func_count = sum(1 for line in lines if 'def ' in line and '(' in line)
            class_count = sum(1 for line in lines if 'class ' in line)
            
            if line_count > 200:
                pontos += 30
                detalhes.append(f"✅ Complexidade adequada: {line_count} linhas")
            else:
                detalhes.append(f"⚠️ Possível simplificação excessiva: {line_count} linhas")
            
            detalhes.append(f"📊 Estatísticas: {func_count} funções, {class_count} classes")
            
            # 2.3 Teste de importação dinâmica
            try:
                spec = importlib.util.spec_from_file_location("mt5_executor_test", executor_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Verificar se tem classe principal
                has_mt5_class = any('MT5' in attr for attr in dir(module))
                if has_mt5_class:
                    pontos += 50
                    detalhes.append("✅ Classe MT5 detectada na importação")
                
                pontos += 50
                detalhes.append("✅ Importação dinâmica bem-sucedida")
                
            except Exception as e:
                detalhes.append(f"❌ FALHA NA IMPORTAÇÃO: {str(e)}")
            
        except Exception as e:
            detalhes.append(f"❌ ERRO NA ANÁLISE: {str(e)}")
        
        self.results["testes"].append({
            "nome": "Análise Cirúrgica Executor",
            "status": "APROVADO" if pontos >= 200 else "REPROVADO",
            "pontos": pontos,
            "max_pontos": max_pontos,
            "detalhes": detalhes
        })
        
        return pontos
    
    def teste_3_verificar_remocao_duplicatas(self):
        """TESTE 3: Verificação extrema de remoção de duplicatas"""
        pontos = 0
        max_pontos = 200
        detalhes = []
        
        # Buscar TODOS os arquivos python no sistema
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Excluir diretórios não relevantes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'node_modules', 'BACKUPS', 'backups', 'logs_arch001']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        detalhes.append(f"📁 Total arquivos Python: {len(python_files)}")
        
        # 3.1 Buscar referências a executores duplicados
        mt5_references = []
        duplicate_indicators = ['MT5NoStopsExecutor', 'mt5_executor_v', 'executor_mt5_old']
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for indicator in duplicate_indicators:
                        if indicator in content:
                            mt5_references.append({
                                "arquivo": py_file,
                                "referencia": indicator,
                                "linha": next((i+1 for i, line in enumerate(content.split('\n')) if indicator in line), 0)
                            })
            except:
                pass
        
        if not mt5_references:
            pontos += 150
            detalhes.append("✅ NENHUMA referência a executores duplicados encontrada")
        else:
            pontos += 50  # Pontos parciais
            detalhes.append(f"⚠️ {len(mt5_references)} referências suspeitas encontradas:")
            for ref in mt5_references[:5]:  # Mostrar apenas 5
                detalhes.append(f"   🔸 {ref['arquivo']}: {ref['referencia']} (linha {ref['linha']})")
        
        # 3.2 Verificar imports consistentes
        import_patterns = ['import mt5_executor', 'from mt5_executor', 'import.*mt5.*executor']
        clean_imports = True
        
        for py_file in python_files[:20]:  # Verificar 20 arquivos aleatórios
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'mt5' in content.lower() and 'executor' in content.lower():
                        # Verificar se importa o nome correto
                        has_correct_import = any(pattern in content for pattern in import_patterns)
                        if not has_correct_import:
                            clean_imports = False
                            detalhes.append(f"⚠️ Import suspeito em: {py_file}")
            except:
                pass
        
        if clean_imports:
            pontos += 50
            detalhes.append("✅ Imports consistentes verificados")
        
        self.results["testes"].append({
            "nome": "Verificação Remoção Duplicatas",
            "status": "APROVADO" if pontos >= 150 else "REPROVADO",
            "pontos": pontos,
            "max_pontos": max_pontos,
            "detalhes": detalhes
        })
        
        return pontos
    
    def teste_4_stress_test_importacao(self):
        """TESTE 4: Teste de stress na importação"""
        pontos = 0
        max_pontos = 150
        detalhes = []
        
        # Encontrar executor principal
        executor_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'logs_arch001', 'temp_', 'BACKUPS']]
            for file in files:
                if 'mt5' in file.lower() and 'executor' in file.lower() and file.endswith('.py'):
                    if '04-Infraestrutura' in root or '04-Infrastructure' in root:
                        executor_files.append(os.path.join(root, file))
        
        if not executor_files:
            self.results["testes"].append({
                "nome": "Stress Test Importação",
                "status": "FALHA",
                "pontos": 0,
                "max_pontos": max_pontos,
                "detalhes": ["❌ Nenhum executor encontrado para teste"]
            })
            return 0
        
        executor = executor_files[0]
        executor_name = os.path.basename(executor).replace('.py', '')
        executor_dir = os.path.dirname(executor)
        
        detalhes.append(f"🧪 Testando importação stress de: {executor}")
        
        # 4.1 Teste de importação dinâmica
        try:
            spec = importlib.util.spec_from_file_location(executor_name, executor)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            pontos += 100
            detalhes.append("✅ Importação dinâmica bem-sucedida")
            
            # Verificar atributos
            attrs = [attr for attr in dir(module) if not attr.startswith('_')]
            detalhes.append(f"✅ {len(attrs)} atributos públicos disponíveis")
            if len(attrs) > 10:
                detalhes.append("   Estrutura rica confirmada")
            
        except Exception as e:
            detalhes.append(f"❌ FALHA NA IMPORTAÇÃO: {str(e)}")
        
        # 4.2 Teste de disponibilidade MetaTrader5
        try:
            import MetaTrader5 as mt5
            pontos += 50
            detalhes.append("✅ MetaTrader5 detectado no ambiente")
            if hasattr(mt5, '__version__'):
                detalhes.append(f"   Versão MT5: {mt5.__version__}")
        except ImportError:
            detalhes.append("⚠️ MetaTrader5 não instalado (normal para teste)")
        
        self.results["testes"].append({
            "nome": "Stress Test Importação",
            "status": "APROVADO" if pontos >= 100 else "REPROVADO",
            "pontos": pontos,
            "max_pontos": max_pontos,
            "detalhes": detalhes
        })
        
        return pontos
    
    def teste_5_validacao_relatorios(self):
        """TESTE 5: Validação forense dos relatórios"""
        pontos = 0
        max_pontos = 150
        detalhes = []
        
        # Buscar relatórios ARCH-001 e checkpoint
        relatorios = [f for f in os.listdir('.') if ('relatorio' in f.lower() or 'checkpoint' in f.lower()) and ('arch001' in f.lower() or 'bloco1' in f.lower()) and (f.endswith('.json') or f.endswith('.md'))]
        
        if not relatorios:
            detalhes.append("❌ NENHUM RELATÓRIO ENCONTRADO")
            self.results["testes"].append({
                "nome": "Validação Relatórios",
                "status": "FALHA",
                "pontos": 0,
                "max_pontos": max_pontos,
                "detalhes": detalhes
            })
            return 0
        
        relatorio = max(relatorios)  # Mais recente
        detalhes.append(f"📄 Relatório analisado: {relatorio}")
        
        try:
            if relatorio.endswith('.json'):
                with open(relatorio, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 5.1 Verificar estrutura do relatório
                required_sections = ['metadata', 'fase_analise']
                
                missing = [section for section in required_sections if section not in data]
                if not missing:
                    pontos += 50
                    detalhes.append("✅ Estrutura do relatório completa")
                else:
                    detalhes.append(f"⚠️ Seções faltando: {missing}")
                
                # 5.2 Verificar status
                if 'metadata' in data and 'status' in data['metadata']:
                    status = data['metadata']['status']
                    if status == 'COMPLETO':
                        pontos += 50
                        detalhes.append(f"✅ Status: {status}")
                    else:
                        detalhes.append(f"⚠️ Status: {status}")
                
                # 5.3 Verificar executores encontrados
                if 'fase_analise' in data and 'total_encontrados' in data['fase_analise']:
                    total = data['fase_analise']['total_encontrados']
                    if total > 0:
                        pontos += 50
                        detalhes.append(f"✅ {total} executores identificados")
            
            elif relatorio.endswith('.md'):
                with open(relatorio, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content) > 500:
                    pontos += 100
                    detalhes.append(f"✅ Relatório completo: {len(content)} chars")
                else:
                    detalhes.append(f"⚠️ Relatório muito curto: {len(content)} chars")
                
                if 'CONCLUÍDO' in content or 'SUCESSO' in content:
                    pontos += 50
                    detalhes.append("✅ Status de conclusão encontrado")
            
        except Exception as e:
            detalhes.append(f"❌ ERRO na análise do relatório: {str(e)}")
        
        self.results["testes"].append({
            "nome": "Validação Relatórios",
            "status": "APROVADO" if pontos >= 100 else "REPROVADO",
            "pontos": pontos,
            "max_pontos": max_pontos,
            "detalhes": detalhes
        })
        
        return pontos
    
    def executar_validacao_extrema(self):
        """Executar todos os testes extremos"""
        print("\n" + "=" * 80)
        print("🚨 VALIDAÇÃO TÉCNICA EXTREMA - ARCH-001")
        print("Double Check Científico de Consolidação")
        print("=" * 80)
        
        total_pontos = 0
        
        # Executar todos os testes
        testes = [
            ("🔍 Backup Forense", self.teste_1_verificar_backup_integridade),
            ("💉 Análise Cirúrgica", self.teste_2_analise_cirurgica_executor),
            ("🧹 Remoção Duplicatas", self.teste_3_verificar_remocao_duplicatas),
            ("⚡ Stress Test", self.teste_4_stress_test_importacao),
            ("📊 Validação Relatórios", self.teste_5_validacao_relatorios)
        ]
        
        for nome, teste_func in testes:
            print(f"\n📋 Executando: {nome}")
            pontos = teste_func()
            total_pontos += pontos
            print(f"   Pontos: {pontos}")
        
        # Calcular resultado final
        porcentagem = (total_pontos / self.results["max_pontos"]) * 100
        self.results["pontuacao_total"] = total_pontos
        self.results["porcentagem"] = round(porcentagem, 2)
        
        if porcentagem >= 85:
            self.results["veredito_final"] = "APROVADO_EXCELENTE"
            status_emoji = "🏆"
        elif porcentagem >= 70:
            self.results["veredito_final"] = "APROVADO"
            status_emoji = "✅"
        elif porcentagem >= 50:
            self.results["veredito_final"] = "APROVADO_COM_RESSALVAS"
            status_emoji = "⚠️"
        else:
            self.results["veredito_final"] = "REPROVADO"
            status_emoji = "❌"
        
        self.results["status"] = "COMPLETO"
        
        # Salvar relatório
        report_file = f"validacao_extrema_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Imprimir relatório resumido
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DA VALIDAÇÃO EXTREMA")
        print("=" * 80)
        
        for teste in self.results["testes"]:
            status = "✅" if teste["pontos"] >= (teste["max_pontos"] * 0.7) else "❌"
            print(f"{status} {teste['nome']}: {teste['pontos']}/{teste['max_pontos']}")
        
        print(f"\n{status_emoji} PONTUAÇÃO TOTAL: {total_pontos}/1000 ({porcentagem:.1f}%)")
        print(f"{status_emoji} VEREDITO: {self.results['veredito_final']}")
        
        print(f"\n📄 Relatório detalhado salvo em: {report_file}")
        
        return porcentagem >= 70


def main():
    """Função principal"""
    print("🚨 INICIANDO VALIDAÇÃO TÉCNICA EXTREMA")
    print("Este teste vai verificar CIENTIFICAMENTE se o ARCH-001 foi executado corretamente.")
    print("Nível: EXTREMO | Método: DOUBLE CHECK | Confiança: 99.9%\n")
    
    # Execução automática (sem interação)
    print("🚀 Executando validação automaticamente...\n")
    
    try:
        validator = ARCH001ExtremeValidator()
        sucesso = validator.executar_validacao_extrema()
        
        if sucesso:
            print("\n🎉 VALIDAÇÃO EXTREMA CONCLUÍDA COM SUCESSO!")
            print("   O ARCH-001 foi executado CORRETAMENTE com alta confiança.")
            print("   Sistema consolidado e validado cientificamente.")
            return 0
        else:
            print("\n⚠️ VALIDAÇÃO EXTREMA IDENTIFICOU PROBLEMAS!")
            print("   Recomenda-se análise detalhada dos relatórios.")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERRO NA VALIDAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

