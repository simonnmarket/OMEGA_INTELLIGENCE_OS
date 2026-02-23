import os
import re
import json
import networkx as nx
from datetime import datetime

def scan_all_files(root_dir):
    files = []
    for folder, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(('.mqh', '.mq5')):
                files.append(os.path.normpath(os.path.join(folder, file)))
    return files

def check_file_integrity(file):
    return 0.95 if os.path.exists(file) else 0.0

def classify_tier(file):
    file_upper = file.upper()
    if "CORE" in file_upper:
        return "CORE"
    elif "INCLUDE" in file_upper:
        return "INCLUDE"
    elif "AUDITOR" in file_upper:
        return "AUDITOR"
    return "OTHER"

def verify_link_status(file, dep):
    return "valid" if os.path.exists(dep) else "error"

def extract_hyper_links(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'#include\s+[<"](.*?)[>"]', content)
            base_dir = os.path.dirname(file)
            return [os.path.normpath(os.path.join(base_dir, m)) for m in matches]
    except Exception as e:
        print(f"Erro ao ler {file}: {e}")
        return []

def find_actual_file(dep, root_dir):
    # Procurar arquivo ignorando case
    for folder, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower() == os.path.basename(dep).lower():
                return os.path.normpath(os.path.join(folder, fname))
    # Verificar bibliotecas padrão do MT5
    standard_path = os.path.join(root_dir, "Include", os.path.basename(dep))
    if os.path.exists(standard_path):
        return standard_path
    return None

def build_dependency_graph(root):
    graph = nx.DiGraph()
    root_dir = os.path.normpath(root)
    files = scan_all_files(root_dir)
    
    for file in files:
        deps = extract_hyper_links(file)
        criticality = 1.0 if "logger_institutional.mqh" in file.lower() else (0.8 if "quantum" in file.lower() else 0.5)
        graph.add_node(file, 
                       integrity=check_file_integrity(file),
                       tier=classify_tier(file),
                       criticality=criticality,
                       timeResolution=100,
                       last_modified=datetime.fromtimestamp(os.path.getmtime(file)).isoformat() if os.path.exists(file) else "")
        for dep in deps:
            actual_dep = find_actual_file(dep, root_dir)
            graph.add_edge(file, actual_dep if actual_dep else dep, status=verify_link_status(file, actual_dep if actual_dep else dep))
    
    # Exportar para JSON
    nodes = [{"id": n.replace(root_dir + "/", ""), **graph.nodes[n]} for n in graph.nodes]
    links = [{"source": u.replace(root_dir + "/", ""), "target": v.replace(root_dir + "/", ""), **graph.edges[u, v]} for u, v in graph.edges]
    with open(os.path.join(root_dir, "dependencies.json"), "w") as f:
        json.dump({"nodes": nodes, "links": links}, f, indent=2)
    
    # Exportar para GEXF
    nx.write_gexf(graph, os.path.join(root_dir, "dependencies.gexf"))
    
    # Log de auditoria
    with open(os.path.join(root_dir, "audit_log.json"), "a") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "action": "Generated dependency graph", "nodes": len(nodes), "links": len(links)}, f)
        f.write("\n")
    
    return graph

if __name__ == "__main__":
    build_dependency_graph("C:/Users/Lenovo/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/") 