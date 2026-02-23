#!/usr/bin/env python3
"""
COMPLEXITY GUARD v3.0 - Monitor de Complexidade para NCNT
Implementação baseada na Análise Crítica #2
Adaptado para estrutura Aurora
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
import logging
from datetime import datetime

logger = logging.getLogger("NCNT.ComplexityGuard")

class ComplexityMetrics:
    """Métricas de complexidade de um módulo"""
    
    def __init__(self):
        self.lines_of_code = 0
        self.cyclomatic_complexity = 0
        self.number_of_methods = 0
        self.number_of_classes = 0
        self.dependency_count = 0
        self.nested_depth = 0
        self.comment_ratio = 0.0
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'lines_of_code': self.lines_of_code,
            'cyclomatic_complexity': self.cyclomatic_complexity,
            'number_of_methods': self.number_of_methods,
            'number_of_classes': self.number_of_classes,
            'dependency_count': self.dependency_count,
            'nested_depth': self.nested_depth,
            'comment_ratio': self.comment_ratio,
            'complexity_score': self.calculate_score()
        }
    
    def calculate_score(self) -> float:
        """Calcula score de complexidade (0-100, menor é melhor)"""
        score = 0
        
        # Penalidades
        if self.lines_of_code > 500:
            score += min((self.lines_of_code - 500) / 10, 20)
        
        if self.cyclomatic_complexity > 50:
            score += min((self.cyclomatic_complexity - 50) / 5, 20)
        
        if self.number_of_methods > 20:
            score += min((self.number_of_methods - 20) / 2, 15)
        
        if self.dependency_count > 10:
            score += min((self.dependency_count - 10) * 2, 15)
        
        if self.nested_depth > 4:
            score += (self.nested_depth - 4) * 5
        
        if self.comment_ratio < 0.1:  # Menos de 10% comentários
            score += 10
        
        return min(score, 100)

class ComplexityGuard:
    """
    Guardião de Complexidade para o Sistema NCNT
    Monitora e impõe limites arquiteturais
    """
    
    # LIMITES INSTITUCIONAIS (TIER-0)
    LIMITS = {
        'lines_per_module': 500,           # Máximo 500 linhas por módulo
        'cyclomatic_complexity': 50,       # Complexidade ciclomática máxima
        'methods_per_class': 20,           # Máximo 20 métodos por classe
        'dependencies_per_module': 10,     # Máximo 10 dependências
        'nested_depth': 4,                 # Profundidade máxima de nesting
        'comment_ratio_min': 0.1,          # Mínimo 10% de comentários
        'god_object_score': 70             # Score máximo para God Object
    }
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(__file__))
        self.thresholds = self.LIMITS.copy()
        self.audit_results = {}
        
        logger.info(f"Complexity Guard inicializado em: {self.base_path}")
    
    def analyze_module(self, module_path: str) -> ComplexityMetrics:
        """
        Analisa um módulo Python específico
        
        Args:
            module_path: Caminho para o arquivo Python
            
        Returns:
            ComplexityMetrics: Métricas de complexidade
        """
        metrics = ComplexityMetrics()
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            # Linhas de código
            metrics.lines_of_code = len([l for l in content if l.strip() and not l.strip().startswith('#')])
            
            # Razão de comentários
            comment_lines = len([l for l in content if l.strip().startswith('#')])
            total_lines = len(content)
            metrics.comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
            
            # Análise AST para métricas avançadas
            source_code = ''.join(content)
            tree = ast.parse(source_code)
            
            # Adiciona parent info para visitor
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child.parent = node
            
            # Contador de classes e métodos
            class_counter = ClassMethodVisitor()
            class_counter.visit(tree)
            
            metrics.number_of_classes = class_counter.class_count
            metrics.number_of_methods = class_counter.method_count
            metrics.cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
            metrics.dependency_count = self._count_dependencies(source_code)
            metrics.nested_depth = self._calculate_nested_depth(tree)
            
        except Exception as e:
            logger.error(f"Erro ao analisar módulo {module_path}: {e}")
        
        return metrics
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calcula complexidade ciclomática"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.Try, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _count_dependencies(self, source_code: str) -> int:
        """Conta dependências de import"""
        imports = set()
        lines = source_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('import ', 'from ')):
                # Extrai nome do módulo
                if line.startswith('import '):
                    parts = line[7:].split()
                    if parts:
                        imports.add(parts[0].split('.')[0])
                elif line.startswith('from '):
                    parts = line[5:].split('import')
                    if len(parts) > 0:
                        module = parts[0].strip().split('.')[0]
                        imports.add(module)
        
        # Remove imports padrão do Python
        stdlib_imports = {'os', 'sys', 'json', 'datetime', 'typing', 'logging', 'pathlib'}
        imports = imports - stdlib_imports
        
        return len(imports)
    
    def _calculate_nested_depth(self, tree: ast.AST) -> int:
        """Calcula profundidade máxima de nesting"""
        depth = 0
        max_depth = 0
        
        def visit_node(node, current_depth):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef, ast.If, ast.For, ast.While,
                                     ast.Try, ast.With)):
                    visit_node(child, current_depth + 1)
                else:
                    visit_node(child, current_depth)
        
        visit_node(tree, 0)
        return max_depth
    
    def audit_all_modules(self) -> Dict:
        """
        Audita todos os módulos do sistema
        
        Returns:
            Dict com resultados da auditoria
        """
        audit_results = {
            'modules_audited': 0,
            'modules_passing': 0,
            'modules_failing': 0,
            'violations': [],
            'recommendations': []
        }
        
        # Encontra todos os arquivos Python
        python_files = []
        for root, dirs, files in os.walk(self.base_path):
            # Ignora diretórios específicos
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'tests', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    python_files.append(os.path.join(root, file))
        
        logger.info(f"Auditando {len(python_files)} módulos Python")
        
        for file_path in python_files:
            try:
                relative_path = os.path.relpath(file_path, self.base_path)
                metrics = self.analyze_module(file_path)
                score = metrics.calculate_score()
                
                module_result = {
                    'path': relative_path,
                    'metrics': metrics.to_dict(),
                    'status': 'PASS' if score < self.thresholds['god_object_score'] else 'FAIL',
                    'score': score
                }
                
                # Verifica violações específicas
                violations = self._check_violations(metrics)
                if violations:
                    module_result['violations'] = violations
                    audit_results['violations'].extend([
                        f"{relative_path}: {v}" for v in violations
                    ])
                    audit_results['modules_failing'] += 1
                else:
                    audit_results['modules_passing'] += 1
                
                audit_results['modules_audited'] += 1
                self.audit_results[relative_path] = module_result
                
                # Gera recomendações
                if score > 50:  # Módulo complexo
                    rec = self._generate_recommendations(relative_path, metrics)
                    if rec:
                        audit_results['recommendations'].append(rec)
            except Exception as e:
                logger.error(f"Erro ao auditar {file_path}: {e}")
        
        return audit_results
    
    def _check_violations(self, metrics: ComplexityMetrics) -> List[str]:
        """Verifica violações dos limites"""
        violations = []
        
        if metrics.lines_of_code > self.thresholds['lines_per_module']:
            violations.append(f"Linhas de código ({metrics.lines_of_code}) > {self.thresholds['lines_per_module']}")
        
        if metrics.cyclomatic_complexity > self.thresholds['cyclomatic_complexity']:
            violations.append(f"Complexidade ciclomática ({metrics.cyclomatic_complexity}) > {self.thresholds['cyclomatic_complexity']}")
        
        if metrics.number_of_methods > self.thresholds['methods_per_class']:
            violations.append(f"Número de métodos ({metrics.number_of_methods}) > {self.thresholds['methods_per_class']}")
        
        if metrics.dependency_count > self.thresholds['dependencies_per_module']:
            violations.append(f"Dependências ({metrics.dependency_count}) > {self.thresholds['dependencies_per_module']}")
        
        if metrics.nested_depth > self.thresholds['nested_depth']:
            violations.append(f"Profundidade de nesting ({metrics.nested_depth}) > {self.thresholds['nested_depth']}")
        
        if metrics.comment_ratio < self.thresholds['comment_ratio_min']:
            violations.append(f"Razão de comentários ({metrics.comment_ratio:.1%}) < {self.thresholds['comment_ratio_min']:.0%}")
        
        return violations
    
    def _generate_recommendations(self, module_path: str, metrics: ComplexityMetrics) -> str:
        """Gera recomendações para refatoração"""
        recommendations = []
        
        if metrics.lines_of_code > 400:
            recommendations.append("Considerar dividir o módulo em submódulos menores")
        
        if metrics.cyclomatic_complexity > 30:
            recommendations.append("Simplificar lógica condicional complexa")
        
        if metrics.number_of_methods > 15:
            recommendations.append("Extrair responsabilidades para novas classes")
        
        if metrics.dependency_count > 8:
            recommendations.append("Reduzir acoplamento com injeção de dependências")
        
        if recommendations:
            return f"{module_path}: {'; '.join(recommendations)}"
        
        return ""
    
    def generate_report(self, output_file: str = None) -> str:
        """Gera relatório de auditoria"""
        audit_results = self.audit_all_modules()
        
        report = [
            "=" * 80,
            "RELATÓRIO DE AUDITORIA DE COMPLEXIDADE - NCNT v3.0",
            "=" * 80,
            f"Data: {datetime.now().isoformat()}",
            f"Base Path: {self.base_path}",
            "",
            f"📊 ESTATÍSTICAS:",
            f"  Módulos auditados: {audit_results['modules_audited']}",
            f"  Módulos aprovados: {audit_results['modules_passing']}",
            f"  Módulos reprovados: {audit_results['modules_failing']}",
            f"  Taxa de aprovação: {audit_results['modules_passing'] / max(audit_results['modules_audited'], 1):.1%}",
            ""
        ]
        
        if audit_results['violations']:
            report.extend([
                "🚨 VIOLAÇÕES ENCONTRADAS:",
                *[f"  • {v}" for v in audit_results['violations'][:10]],  # Mostra apenas 10
                ""
            ])
        
        if audit_results['recommendations']:
            report.extend([
                "💡 RECOMENDAÇÕES:",
                *[f"  • {r}" for r in audit_results['recommendations'][:5]],  # Mostra apenas 5
                ""
            ])
        
        # Módulos mais complexos (top 5)
        complex_modules = sorted(
            [(path, data['score']) for path, data in self.audit_results.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if complex_modules:
            report.extend([
                "⚠️  MÓDULOS MAIS COMPLEXOS:",
                *[f"  • {path}: {score:.1f}/100" for path, score in complex_modules],
                ""
            ])
        
        report.append("=" * 80)
        
        report_text = '\n'.join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"Relatório salvo em: {output_file}")
        
        return report_text

class ClassMethodVisitor(ast.NodeVisitor):
    """Visitor AST para contar classes e métodos"""
    
    def __init__(self):
        self.class_count = 0
        self.method_count = 0
    
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        # Conta métodos dentro de classes
        if hasattr(node, 'parent') and isinstance(node.parent, ast.ClassDef):
            self.method_count += 1
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

if __name__ == "__main__":
    print("🧪 Testando Complexity Guard v3.0")
    
    guard = ComplexityGuard()
    
    # Teste 1: Análise deste próprio arquivo
    current_file = __file__
    metrics = guard.analyze_module(current_file)
    
    print(f"📊 Métricas deste módulo:")
    print(f"  Linhas de código: {metrics.lines_of_code}")
    print(f"  Complexidade ciclomática: {metrics.cyclomatic_complexity}")
    print(f"  Número de métodos: {metrics.number_of_methods}")
    print(f"  Número de classes: {metrics.number_of_classes}")
    print(f"  Dependências: {metrics.dependency_count}")
    print(f"  Score de complexidade: {metrics.calculate_score():.1f}/100")
    
    # Teste 2: Auditoria completa
    print("\n🔍 Executando auditoria completa...")
    results = guard.audit_all_modules()
    
    print(f"\n🎯 Resultados:")
    print(f"  Módulos auditados: {results['modules_audited']}")
    print(f"  Módulos aprovados: {results['modules_passing']}")
    print(f"  Módulos reprovados: {results['modules_failing']}")
    
    if results['violations']:
        print(f"\n⚠️  Violações encontradas: {len(results['violations'])}")
        for violation in results['violations'][:3]:  # Mostra apenas 3
            print(f"  • {violation}")
    
    print("\n✅ Complexity Guard v3.0 testado com sucesso")


