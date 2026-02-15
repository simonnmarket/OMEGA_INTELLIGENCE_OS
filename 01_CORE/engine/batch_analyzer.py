import os
import json
import logging
from scientific_assessor import ScientificAssessor

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchAnalyzer:
    """
    Processador em lote para análise científica de repositórios de código.
    """
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.assessor = ScientificAssessor()
        self.results = []

    def run(self):
        logger.info(f"Iniciando análise em lote no diretório: {self.root_dir}")
        
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(('.mq5', '.mqh', '.txt', '.py')):
                    filepath = os.path.join(root, file)
                    logger.info(f"Analisando: {file}")
                    try:
                        analysis = self.assessor.analyze_module(filepath)
                        # Adicionar metadados de localização
                        analysis['path'] = os.path.relpath(filepath, self.root_dir)
                        self.results.append(analysis)
                    except Exception as e:
                        logger.error(f"Erro ao analisar {file}: {str(e)}")

        self.save_results()

    def save_results(self):
        output_path = os.path.join(os.path.dirname(__file__), '..', '..', '07_LOGS', 'SCIENTIFIC_BATCH_ANALYSIS.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Análise concluída. {len(self.results)} arquivos processados.")
        logger.info(f"Resultados salvos em: {output_path}")

if __name__ == "__main__":
    inbox_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '09_INBOX'))
    analyzer = BatchAnalyzer(inbox_dir)
    analyzer.run()
