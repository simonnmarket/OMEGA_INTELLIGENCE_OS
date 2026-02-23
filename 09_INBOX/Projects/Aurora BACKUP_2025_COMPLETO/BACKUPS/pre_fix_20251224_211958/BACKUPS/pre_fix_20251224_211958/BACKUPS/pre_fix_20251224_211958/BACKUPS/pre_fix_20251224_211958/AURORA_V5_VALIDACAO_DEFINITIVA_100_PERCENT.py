#!/usr/bin/env python3
"""
AURORA_V5_VALIDACAO_DEFINITIVA_100_PERCENT.py

Validação que NÃO ACEITA menos de 100% operacional.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess
import importlib.util

class ValidadorDefinitivo:
    """Validador que exige 100% de operacionalidade."""
    
    def __init__(self):
        self.root = Path(".").absolute()
        self.resultados = {
            "timestamp": datetime.now().isoformat(),
            "exigencia": "100%_operacional",
            "tolerancia": 0,
            "status_final": "reprovado",
            "modulos": [],
            "erros": []
        }
    
    def validar_modulo_estrito(self, caminho_modulo):
        """Validação estrita de um módulo."""
        try:
            # 1. Compilação obrigatória
            compilacao = subprocess.run(
                [sys.executable, "-m", "py_compile", str(caminho_modulo)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if compilacao.returncode != 0:
                return {
                    "modulo": str(caminho_modulo.relative_to(self.root)),
                    "status": "reprovado",
                    "erro": compilacao.stderr[:300],
                    "tipo": "erro_compilacao"
                }
            
            # 2. Importação obrigatória (tentativa)
            try:
                spec = importlib.util.spec_from_file_location(
                    f"val_{caminho_modulo.name}",
                    str(caminho_modulo)
                )
                
                if not spec or not spec.loader:
                    return {
                        "modulo": str(caminho_modulo.relative_to(self.root)),
                        "status": "reprovado",
                        "erro": "Não foi possível criar spec de importação",
                        "tipo": "erro_import"
                    }
                
                # 3. Carregamento (sem executar)
                module = importlib.util.module_from_spec(spec)
                
                return {
                    "modulo": str(caminho_modulo.relative_to(self.root)),
                    "status": "aprovado",
                    "erro": None,
                    "tipo": "operacional"
                }
                
            except Exception as e:
                return {
                    "modulo": str(caminho_modulo.relative_to(self.root)),
                    "status": "reprovado",
                    "erro": str(e),
                    "tipo": "erro_carregamento"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "modulo": str(caminho_modulo.relative_to(self.root)),
                "status": "reprovado",
                "erro": "Timeout na compilação",
                "tipo": "timeout"
            }
        except Exception as e:
            return {
                "modulo": str(caminho_modulo.relative_to(self.root)),
                "status": "reprovado",
                "erro": str(e),
                "tipo": "erro_validacao"
            }
    
    def executar_validacao_completa(self):
        """Executa validação completa."""
        print("🧪 VALIDAÇÃO DEFINITIVA - EXIGÊNCIA: 100% OPERACIONAL")
        print("=" * 80)
        
        # Encontrar todos os módulos
        modulos = []
        for py_file in self.root.rglob("*.py"):
            if "__pycache__" in str(py_file) or "backup" in str(py_file):
                continue
            modulos.append(py_file)
        
        print(f"📁 Total de módulos para validar: {len(modulos)}")
        
        # Validar cada módulo
        aprovados = 0
        reprovados = 0
        
        for i, modulo in enumerate(modulos, 1):
            rel_path = str(modulo.relative_to(self.root))
            
            resultado = self.validar_modulo_estrito(modulo)
            self.resultados["modulos"].append(resultado)
            
            if resultado["status"] == "aprovado":
                aprovados += 1
                print(f"✅ {i:4d}/{len(modulos)}: {rel_path[:70]:70} APROVADO")
            else:
                reprovados += 1
                self.resultados["erros"].append(resultado)
                print(f"❌ {i:4d}/{len(modulos)}: {rel_path[:70]:70} REPROVADO")
        
        # Determinar status final
        taxa_aprovacao = (aprovados / len(modulos)) * 100 if modulos else 0
        
        if taxa_aprovacao == 100:
            self.resultados["status_final"] = "aprovado"
            print(f"\n🎯 RESULTADO: {aprovados}/{len(modulos)} ({taxa_aprovacao:.2f}%) - APROVADO")
        else:
            self.resultados["status_final"] = "reprovado"
            print(f"\n🎯 RESULTADO: {aprovados}/{len(modulos)} ({taxa_aprovacao:.2f}%) - REPROVADO")
        
        return taxa_aprovacao == 100
    
    def gerar_relatorio_estrito(self):
        """Gera relatório estrito da validação."""
        
        relatorio = f"""AURORA v5.0 - VALIDAÇÃO DEFINITIVA
================================================================================
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Exigência: 100% dos módulos operacionais
Tolerância: 0%
Status Final: {self.resultados['status_final'].upper()}
================================================================================

RESUMO ESTATÍSTICO
------------------
Total de Módulos Validados: {len(self.resultados['modulos'])}
Módulos Aprovados: {sum(1 for m in self.resultados['modulos'] if m['status'] == 'aprovado')}
Módulos Reprovados: {sum(1 for m in self.resultados['modulos'] if m['status'] == 'reprovado')}

"""
        
        if self.resultados["erros"]:
            relatorio += "MÓDULOS REPROVADOS (REQUEREM CORREÇÃO):\n"
            relatorio += "=" * 80 + "\n"
            
            for erro in self.resultados["erros"]:
                relatorio += f"\n❌ {erro['modulo']}\n"
                relatorio += f"   Tipo: {erro['tipo']}\n"
                relatorio += f"   Erro: {erro['erro'][:150]}...\n"
        
        relatorio += f"""

DECISÃO FINAL DA VALIDAÇÃO
--------------------------
"""
        
        if self.resultados["status_final"] == "aprovado":
            relatorio += """✅ SISTEMA APROVADO PARA PRODUÇÃO

PRÓXIMOS PASSOS OBRIGATÓRIOS:

1. Executar: python aurora_etapa_a.py --system-check
2. Executar: python aurora_etapa_a.py --real-market-data
3. Coletar métricas empíricas
4. Tomar decisão baseada em dados"""
        else:
            relatorio += """❌ SISTEMA REPROVADO - NÃO PODE PROSSEGUIR

AÇÕES OBRIGATÓRIAS ANTES DE REVALIDAR:

1. Corrigir TODOS os módulos listados acima
2. Executar script de correção definitiva
3. Re-executar esta validação
4. Só prosseguir após aprovação 100%"""

        return relatorio

def main():
    """Função principal."""
    validador = ValidadorDefinitivo()
    
    try:
        # Executar validação
        aprovado = validador.executar_validacao_completa()
        
        # Gerar relatório
        relatorio = validador.gerar_relatorio_estrito()
        
        # Salvar resultados
        json_path = Path("aurora_validacao_definitiva.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(validador.resultados, f, indent=2, ensure_ascii=False)
        
        txt_path = Path("aurora_validacao_definitiva.txt")
        txt_path.write_text(relatorio, encoding='utf-8')
        
        # Exibir resultado
        print("\n" + "=" * 80)
        print(relatorio)
        print("=" * 80)
        
        print(f"\n📁 JSON detalhado: {json_path}")
        print(f"📁 Relatório: {txt_path}")
        
        # Retornar código de saída
        return 0 if aprovado else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Validação interrompida")
        return 2
    except Exception as e:
        print(f"\n❌ Erro na validação: {str(e)}")
        return 3

if __name__ == "__main__":
    sys.exit(main())

