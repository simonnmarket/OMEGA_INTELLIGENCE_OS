import json, os, datetime

LOG_FILE = "07_LOGS/audit_log.json"

def log_event(event_type, message):
    entry = {
        "timestamp": str(datetime.datetime.now()),
        "event_type": event_type,
        "message": message
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Audit: {message}")
