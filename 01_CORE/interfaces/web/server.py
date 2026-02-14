import http.server
import socketserver
import json
import os
import sys

# Configuration
PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), "")
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../07_LOGS"))
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../02_MODULES/Include"))

class OmegaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response_data = {}
            
            if self.path == "/api/audit":
                log_path = os.path.join(LOG_DIR, "audit_log.json")
                if os.path.exists(log_path):
                    with open(log_path, "r") as f:
                        response_data = json.load(f)
                else:
                    response_data = []
                    
            elif self.path == "/api/modules":
                meta_path = os.path.join(MODULE_DIR, "metadata_schema.json")
                if os.path.exists(meta_path):
                    with open(meta_path, "r") as f:
                        response_data = json.load(f)
                else:
                    response_data = []

            elif self.path == "/api/stats":
                # Calculate stats on the fly
                log_path = os.path.join(LOG_DIR, "audit_log.json")
                total_events = 0
                last_active = "N/A"
                if os.path.exists(log_path):
                    with open(log_path, "r") as f:
                        logs = json.load(f)
                        total_events = len(logs)
                        if logs:
                            last_active = logs[-1]['timestamp']
                
                response_data = {
                    "system_status": "ONLINE",
                    "total_events": total_events,
                    "last_active": last_active,
                    "version": "1.0.0"
                }

            self.wfile.write(json.dumps(response_data).encode())
        else:
            # Serve static files
            super().do_GET()

if __name__ == "__main__":
    os.chdir(WEB_DIR)
    print(f"OMEGA Dashboard Server running at http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), OmegaHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
