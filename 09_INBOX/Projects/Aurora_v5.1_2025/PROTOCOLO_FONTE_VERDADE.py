#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROTOCOLO FONTE DE VERDADE - AURORA v5.1
=========================================

Este protocolo GARANTE que SEMPRE consultamos a documentação oficial ANTES
de qualquer ação. IMPEDE erros de discrepância e garante consistência total.

REGRA DE OURO: NUNCA assumir, SEMPRE consultar a fonte de verdade primeiro.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FonteVerdadeAurora:
    """
    Classe que SEMPRE consulta a documentação oficial antes de qualquer ação.
    É a ÚNICA fonte de verdade para informações do sistema Aurora.
    """
    
    # FONTES OFICIAIS (ÚNICAS FONTES DE VERDADE)
    DOCUMENTO_TECNICO_COMPLETO = "AURORA_COMPLETE_TECHNICAL_DOCUMENT.md"
    DOCUMENTO_SINTETIZADO = "AURORA_SISTEMA_SINTETIZADO_FINAL_V5.1.md"
    MANIFESTO_GOVERNANCA = "project_manifest.json"
    
    # CONSTANTES VERIFICADAS
    TOTAL_MODULOS_SISTEMA = 252  # Verificado na PARTE 4 do documento técnico
    
    def __init__(self):
        """Inicializa verificando se as fontes de verdade existem."""
        self.verificar_fontes()
        self._cache = {}
    
    def verificar_fontes(self) -> bool:
        """
        Verifica se todas as fontes de verdade existem.
        Gera ERRO CRÍTICO se alguma estiver faltando.
        """
        fontes = [
            self.DOCUMENTO_TECNICO_COMPLETO,
            self.DOCUMENTO_SINTETIZADO,
        ]
        
        faltando = []
        for fonte in fontes:
            if not os.path.exists(fonte):
                faltando.append(fonte)
        
        if faltando:
            raise FileNotFoundError(
                f"ERRO CRÍTICO: Fontes de verdade faltando:\n" +
                "\n".join(f"  - {f}" for f in faltando) +
                "\n\nNÃO PROSSIGA sem estas fontes!"
            )
        
        return True
    
    def obter_lista_modulos_documentada(self) -> List[str]:
        """
        Obtém a lista COMPLETA de 252 módulos da PARTE 4 do documento técnico.
        Esta é a ÚNICA fonte de verdade para a lista de módulos.
        
        Returns:
            Lista de caminhos dos 252 módulos do sistema
        """
        if 'modulos_documentados' in self._cache:
            return self._cache['modulos_documentados']
        
        doc_path = self.DOCUMENTO_TECNICO_COMPLETO
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontrar PARTE 4
        parte4_start = content.find("## PARTE 4: LISTA COMPLETA DE MÓDULOS (252 System Modules)")
        if parte4_start == -1:
            raise ValueError("ERRO: PARTE 4 não encontrada no documento técnico")
        
        # Encontrar bloco de código
        list_start = content.find("## 4.1 Complete Module List", parte4_start)
        code_start = content.find("```text", list_start)
        if code_start == -1:
            code_start = content.find("```", list_start)
        
        if code_start == -1:
            raise ValueError("ERRO: Bloco de código da lista não encontrado")
        
        code_end = content.find("```", code_start + 7)
        if code_end == -1:
            raise ValueError("ERRO: Fim do bloco de código não encontrado")
        
        # Extrair linhas
        code_block = content[code_start + 7:code_end].strip()
        lines = [line.strip() for line in code_block.split('\n') if line.strip()]
        
        # Filtrar apenas .py
        modules = []
        for line in lines:
            if line.endswith('.py'):
                normalized = line.replace('\\', '/')
                modules.append(normalized)
        
        # VALIDAÇÃO CRÍTICA
        if len(modules) != self.TOTAL_MODULOS_SISTEMA:
            raise ValueError(
                f"ERRO CRÍTICO: Contagem de módulos incorreta!\n"
                f"  Esperado: {self.TOTAL_MODULOS_SISTEMA}\n"
                f"  Encontrado: {len(modules)}\n"
                f"  NÃO PROSSIGA até corrigir!"
            )
        
        self._cache['modulos_documentados'] = modules
        return modules
    
    def verificar_modulos_integrados(self) -> Tuple[bool, Dict]:
        """
        Verifica se TODOS os 252 módulos documentados estão no sistema de governança.
        
        Returns:
            (todos_integrados, relatorio_detalhado)
        """
        # Obter lista documentada (fonte de verdade)
        modulos_documentados = self.obter_lista_modulos_documentada()
        
        # Obter módulos no manifesto
        if not os.path.exists(self.MANIFESTO_GOVERNANCA):
            return False, {
                "erro": "Manifesto de governança não existe",
                "modulos_documentados": len(modulos_documentados),
                "modulos_no_manifesto": 0
            }
        
        with open(self.MANIFESTO_GOVERNANCA, 'r', encoding='utf-8') as f:
            manifesto = json.load(f)
        
        modulos_manifesto = manifesto.get("modules", {})
        
        # Criar mapeamento de nomes
        nomes_documentados = {
            m.replace('\\', '_').replace('/', '_').replace('.py', ''): m
            for m in modulos_documentados
        }
        
        nomes_manifesto = {
            mod_data.get("name", ""): mod_id
            for mod_id, mod_data in modulos_manifesto.items()
        }
        
        # Verificar quais estão faltando
        faltando = []
        integrados = []
        
        for nome_doc, path_doc in nomes_documentados.items():
            if nome_doc in nomes_manifesto:
                integrados.append(path_doc)
            else:
                faltando.append(path_doc)
        
        todos_integrados = len(faltando) == 0
        
        return todos_integrados, {
            "todos_integrados": todos_integrados,
            "total_documentados": len(modulos_documentados),
            "total_no_manifesto": len(modulos_manifesto),
            "total_integrados": len(integrados),
            "total_faltando": len(faltando),
            "modulos_faltando": faltando[:10],  # Primeiros 10
            "percentual_integrado": (len(integrados) / len(modulos_documentados) * 100) if modulos_documentados else 0
        }
    
    def validar_consistencia_completa(self) -> Dict:
        """
        Validação COMPLETA de consistência entre documentação e sistema.
        Retorna relatório detalhado de qualquer inconsistência.
        """
        resultado = {
            "status": "OK",
            "erros": [],
            "avisos": [],
            "validacoes": {}
        }
        
        # 1. Verificar se documento técnico existe
        if not os.path.exists(self.DOCUMENTO_TECNICO_COMPLETO):
            resultado["status"] = "ERRO"
            resultado["erros"].append("Documento técnico completo não encontrado")
            return resultado
        
        # 2. Verificar contagem de módulos no documento
        try:
            modulos_doc = self.obter_lista_modulos_documentada()
            resultado["validacoes"]["modulos_documentados"] = len(modulos_doc)
            
            if len(modulos_doc) != self.TOTAL_MODULOS_SISTEMA:
                resultado["status"] = "ERRO"
                resultado["erros"].append(
                    f"Contagem incorreta no documento: {len(modulos_doc)} != {self.TOTAL_MODULOS_SISTEMA}"
                )
        except Exception as e:
            resultado["status"] = "ERRO"
            resultado["erros"].append(f"Erro ao ler documento: {e}")
            return resultado
        
        # 3. Verificar integração no sistema de governança
        todos_integrados, rel_integracao = self.verificar_modulos_integrados()
        resultado["validacoes"]["integracao"] = rel_integracao
        
        if not todos_integrados:
            resultado["status"] = "ERRO"
            resultado["erros"].append(
                f"{rel_integracao['total_faltando']} módulos documentados não estão no sistema de governança"
            )
        
        # 4. Verificar existência física dos arquivos
        modulos_inexistentes = []
        for mod_path in modulos_doc:
            # Tentar diferentes variações de caminho
            paths_to_try = [
                mod_path,
                mod_path.replace('/', '\\'),
                mod_path.replace('\\', '/'),
            ]
            
            existe = False
            for path_variant in paths_to_try:
                if os.path.exists(path_variant):
                    existe = True
                    break
            
            if not existe:
                modulos_inexistentes.append(mod_path)
        
        resultado["validacoes"]["arquivos_existentes"] = {
            "total": len(modulos_doc),
            "existentes": len(modulos_doc) - len(modulos_inexistentes),
            "inexistentes": len(modulos_inexistentes),
            "lista_inexistentes": modulos_inexistentes[:10]
        }
        
        if modulos_inexistentes:
            resultado["status"] = "ERRO"
            resultado["erros"].append(
                f"{len(modulos_inexistentes)} módulos documentados não existem fisicamente"
            )
        
        return resultado


def protocolo_obrigatorio_antes_de_qualquer_acao():
    """
    PROTOCOLO OBRIGATÓRIO que DEVE ser executado ANTES de qualquer ação.
    
    Este protocolo garante que:
    1. Sempre consultamos a documentação oficial primeiro
    2. Validamos consistência antes de prosseguir
    3. Impedimos erros de discrepância
    """
    print("=" * 80)
    print("PROTOCOLO FONTE DE VERDADE - VALIDACAO OBRIGATORIA")
    print("=" * 80)
    
    fonte = FonteVerdadeAurora()
    
    # Executar validação completa
    resultado = fonte.validar_consistencia_completa()
    
    print(f"\nStatus: {resultado['status']}")
    
    if resultado["erros"]:
        print("\nERROS CRITICOS ENCONTRADOS:")
        for erro in resultado["erros"]:
            print(f"  ❌ {erro}")
        print("\nNAO PROSSIGA ATE CORRIGIR OS ERROS!")
        return False
    
    if resultado["avisos"]:
        print("\nAVISOS:")
        for aviso in resultado["avisos"]:
            print(f"  ⚠️  {aviso}")
    
    print("\nVALIDACOES:")
    for key, value in resultado["validacoes"].items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                if not isinstance(v, list):
                    print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("VALIDACAO CONCLUIDA - SISTEMA CONSISTENTE")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    # Executar protocolo obrigatório
    sucesso = protocolo_obrigatorio_antes_de_qualquer_acao()
    
    if not sucesso:
        exit(1)

