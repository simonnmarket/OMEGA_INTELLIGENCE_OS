#!/usr/bin/env python3
"""
RED TEAM FINAL VALIDATION - ETAPA 1 AURORA v5.1
CEO + CKO Final Approval Protocol
"""

import os
import sys
import json
from datetime import datetime

class RedTeamFinalValidation:
    def __init__(self):
        self.resultados = {
            "timestamp": datetime.now().isoformat(),
            "etapa": "ETAPA_1_FINAL",
            "testes": {},
            "veredito_final": "PENDENTE"
        }
    
    def validar_scripts_instalados(self):
        """Verificar se todos os scripts foram instalados"""
        scripts = ["executar_etapa1.py", "redteam_validation.py", "fix_critical_issues.py"]
        resultado = {"scripts": [], "total": len(scripts), "instalados": 0}
        
        for script in scripts:
            existe = os.path.exists(script)
            if existe:
                resultado["instalados"] += 1
            resultado["scripts"].append({"nome": script, "existe": existe})
        
        resultado["status"] = "APROVADO" if resultado["instalados"] == resultado["total"] else "REPROVADO"
        self.resultados["testes"]["scripts_instalados"] = resultado
        return resultado["status"] == "APROVADO"
    
    def validar_documentacao_criada(self):
        """Verificar se documentação foi criada"""
        docs = ["RELATORIO_CONCLUSAO_ETAPA1.md", "relatorio_execucao_etapa1.json"]
        resultado = {"documentos": [], "total": len(docs), "criados": 0}
        
        for doc in docs:
            existe = os.path.exists(doc)
            if existe:
                resultado["criados"] += 1
            resultado["documentos"].append({"nome": doc, "existe": existe})
        
        resultado["status"] = "APROVADO" if resultado["criados"] >= 1 else "REPROVADO"
        self.resultados["testes"]["documentacao_criada"] = resultado
        return resultado["status"] == "APROVADO"
    
    def testar_importacao_sistema(self):
        """Testar importação do sistema principal"""
        try:
            import system_core.ncnt_orchestrator_complete
            resultado = {"status": "APROVADO", "mensagem": "Importação bem-sucedida"}
        except Exception as e:
            resultado = {"status": "REPROVADO", "mensagem": f"Erro: {e}"}
        
        self.resultados["testes"]["importacao_sistema"] = resultado
        return resultado["status"] == "APROVADO"
    
    def gerar_veredito_final(self):
        """Gerar veredito final CEO+CKO"""
        testes = self.resultados["testes"]
        aprovados = sum(1 for t in testes.values() if t["status"] == "APROVADO")
        total = len(testes)
        
        if aprovados == total:
            self.resultados["veredito_final"] = "APROVADO"
        elif aprovados >= total * 0.7:
            self.resultados["veredito_final"] = "APROVADO COM RESSALVAS"
        else:
            self.resultados["veredito_final"] = "REPROVADO"
        
        return self.resultados["veredito_final"]
    
    def executar_validacao_final(self):
        """Executar validação completa"""
        print("=" * 60)
        print("RED TEAM FINAL VALIDATION - ETAPA 1")
        print("=" * 60)
        
        self.validar_scripts_instalados()
        self.validar_documentacao_criada()
        self.testar_importacao_sistema()
        
        veredito = self.gerar_veredito_final()
        
        print(f"\nVeredito Final: {veredito}")
        for teste, resultado in self.resultados["testes"].items():
            print(f"- {teste}: {resultado['status']}")
        
        with open("redteam_final_validation.json", "w") as f:
            json.dump(self.resultados, f, indent=2)
        
        return veredito

if __name__ == "__main__":
    validator = RedTeamFinalValidation()
    resultado = validator.executar_validacao_final()
    sys.exit(0 if resultado == "APROVADO" else 1)

