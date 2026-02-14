"""
Audit Module - OMEGA_INTELLIGENCE_OS
Implements immutable logging and decision tracking as per Doc 10 and Doc 8.
"""
import datetime
import os

class AuditLogger:
    def __init__(self, log_dir="07_LOGS"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def log_event(self, event_type, message, agent_id="SYSTEM"):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{event_type}] [{agent_id}] {message}\n"
        
        # Log to daily file
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.log_dir, f"audit_{date_str}.log")
        
        with open(file_path, "a") as f:
            f.write(log_entry)
        
        return True
