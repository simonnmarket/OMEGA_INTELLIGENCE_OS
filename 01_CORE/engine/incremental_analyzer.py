import os
import json
import hashlib
import logging
from metrics import CodeMetrics
from statistics import TradingStatistics
from taxonomy import CodeTaxonomy
from scientific_assessor import ScientificAssessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.INFO

class IncrementalAnalyzer:
    def __init__(self, root_dir, results_path):
        self.root_dir = root_dir
        self.results_path = results_path
        self.assessor = ScientificAssessor()
        self.results = self.load_existing_results()

    def get_file_hash(self, filepath):
        try:
            hasher = hashlib.md5()
            # Usar prefixo para caminhos longos no Windows se necessário
            with open(filepath, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logging.error(f"Erro ao gerar hash para {filepath}: {str(e)}")
            return None

    def load_existing_results(self):
        if os.path.exists(self.results_path):
            with open(self.results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Criar um dicionário indexado pelo caminho relativo para busca rápida
                return {item['path']: item for item in data}
        return {}

    def run(self):
        logging.info(f"Iniciando análise incremental em: {self.root_dir}")
        new_count = 0
        updated_count = 0
        
        current_paths = set()
        
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(('.mq5', '.mqh', '.txt', '.py')):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, self.root_dir)
                    current_paths.add(rel_path)
                    
                    file_hash = self.get_file_hash(filepath)
                    
                    # Verificar se precisa re-analisar
                    if rel_path in self.results and self.results[rel_path].get('hash') == file_hash:
                        continue
                    
                    if rel_path in self.results:
                        logging.info(f"Atualizando: {rel_path}")
                        updated_count += 1
                    else:
                        logging.info(f"Novo arquivo detectado: {rel_path}")
                        new_count += 1
                        
                    try:
                        analysis = self.assessor.analyze_module(filepath)
                        analysis['path'] = rel_path
                        analysis['hash'] = file_hash
                        self.results[rel_path] = analysis
                    except Exception as e:
                        logging.error(f"Erro ao analisar {file}: {str(e)}")

        # Remover arquivos que não existem mais
        paths_to_remove = [p for p in self.results if p not in current_paths]
        for p in paths_to_remove:
            logging.info(f"Removendo do índice: {p}")
            del self.results[p]

        self.save_results()
        logging.info(f"Concluído: {new_count} novos, {updated_count} atualizados, {len(paths_to_remove)} removidos.")

    def save_results(self):
        with open(self.results_path, 'w', encoding='utf-8') as f:
            json.dump(list(self.results.values()), f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    root_dir = r'c:\Users\User\.gemini\antigravity\playground\ultraviolet-nadir\09_INBOX'
    results_path = r'c:\Users\User\.gemini\antigravity\playground\ultraviolet-nadir\07_LOGS\SCIENTIFIC_BATCH_ANALYSIS.json'
    
    analyzer = IncrementalAnalyzer(root_dir, results_path)
    analyzer.run()
