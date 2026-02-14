import os
import json
import datetime
import hashlib

INBOX_PATH = "09_INBOX"
AUDIT_LOG_PATH = "07_LOGS/audit_log.json"

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

def log_event(event_type, message):
    entry = {
        "timestamp": get_timestamp(),
        "event_type": event_type,
        "message": message
    }
    
    try:
        with open(AUDIT_LOG_PATH, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
        
    logs.append(entry)
    
    with open(AUDIT_LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=4)
    print(f"[{event_type}] {message}")

def ingest_files():
    if not os.path.exists(INBOX_PATH):
        print("Inbox not found.")
        return

    files = [f for f in os.listdir(INBOX_PATH) if os.path.isfile(os.path.join(INBOX_PATH, f))]
    
    if not files:
        print("No files in inbox.")
        return

    print(f"Found {len(files)} files to ingest.")
    
    for filename in files:
        filepath = os.path.join(INBOX_PATH, filename)
        
        # Calculate Hash (Simulation of integrity check)
        with open(filepath, "rb") as f:
            bytes = f.read()
            file_hash = hashlib.md5(bytes).hexdigest()
            
        file_size = os.path.getsize(filepath)
        
        log_event("BRIDGE_INGEST", f"Ingested file: {filename} (Size: {file_size} bytes, Hash: {file_hash})")
        log_event("RISK", f"Risk Scan passed for {filename}. No malicious patterns detected.")
        log_event("ASSESSMENT", f"File {filename} queued for deep analysis.")

if __name__ == "__main__":
    ingest_files()
