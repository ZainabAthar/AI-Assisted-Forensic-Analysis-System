import pytest
import time
from pathlib import Path
import sys
import os

# Setup paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from streamlit.testing.v1 import AppTest

def test_sequential_analysis_load():
    """
    Stress Test: Simulate 5 rapid sequential analysis starts to check for state leakage or crashes.
    """
    at = AppTest.from_file(str(project_root / "app.py"))
    
    # We want to ensure that starting multiple runs doesn't crash the server
    for i in range(5):
        at.run(timeout=60)
        # In a real environment, we'd upload different files, 
        # but here we just ensure the app remains responsive.
        assert not at.exception

def test_large_audit_log_performance(tmp_path):
    """
    Stress Test: Verify that the audit logger handles high volume without excessive delay.
    """
    from scripts.audit_logger import ForensicAuditLogger
    test_log_dir = tmp_path / "logs"
    logger = ForensicAuditLogger(log_dir=str(test_log_dir))
    
    start_time = time.time()
    for i in range(100):
        logger.log_event("STRESS_TEST", f"Message entry {i}")
    end_time = time.time()
    
    # 100 entries should take much less than 1 second
    assert (end_time - start_time) < 1.0
