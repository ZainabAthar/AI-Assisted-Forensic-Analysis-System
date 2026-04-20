import logging
import os
from datetime import datetime
from pathlib import Path

class ForensicAuditLogger:
    """
    Specialized logger for forensic integrity.
    Logs actions with timestamps and secure formatting.
    """
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "forensic_audit.log"
        
        # Setup logging
        self.logger = logging.getLogger("ForensicAudit")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers and support test isolation
        if log_dir != "logs" or not self.logger.handlers:
            # Clear existing handlers if we are switching to a test directory
            if log_dir != "logs":
                for handler in self.logger.handlers[:]:
                    self.logger.removeHandler(handler)
                    
            fh = logging.FileHandler(self.log_file)
            fh.setLevel(logging.INFO)
            
            # Professional forensic format: [TIMESTAMP] [LEVEL] [EVENT_ID] MESSAGE
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [EVT-%(relativeCreated)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def log_event(self, action, details, status="SUCCESS"):
        """Record a forensic event."""
        message = f"| ACTION: {action} | DETAILS: {details} | STATUS: {status} |"
        self.logger.info(message)

# Global singleton for easy access
audit_logger = ForensicAuditLogger()
