import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audit.audit import log_event

class ProjectAssessor:
    def __init__(self):
        log_event("ASSESSOR", "Project Assessor initialized")

    def evaluate_project(self, project_data):
        # Avaliação simples baseada em critérios fictícios
        score = sum(project_data.get("values", []))
        # Avoid division by zero
        count = len(project_data.get("values", []))
        if count == 0:
            count = 1
        
        golden_points = score / count
        log_event("ASSESSMENT", f"Project scored {golden_points}")
        return golden_points

if __name__ == "__main__":
    pa = ProjectAssessor()
    pa.evaluate_project({"values": [10, 20, 30]})
