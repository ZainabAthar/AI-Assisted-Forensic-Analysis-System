import subprocess
import os
import sys
from pathlib import Path

def run_command(command, description, check=True):
    print(f"\n[STEP] {description}...")
    try:
        # Use sys.executable for internal scripts
        if command.startswith("python"):
            command = command.replace("python", sys.executable, 1)
            
        result = subprocess.run(command, shell=True, check=check, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Step failed: {description}")
        return False

def main():
    # Ensure we are in the project root
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)
    
    evidence_dir = Path("d:/FYP/MD-II/Test_Evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("AI-ASSISTED FORENSIC ANALYSIS SYSTEM: MASTER EXECUTION SUITE")
    print("="*60)
    
    # Step 1: Automated Testing
    test_cmd = f"python -m pytest -s -v --html={evidence_dir}/test_report.html --self-contained-html --color=no > {evidence_dir}/full_test_logs.txt"
    run_command(test_cmd, "Executing 39-Test Forensic Suite", check=False)
    
    # Step 2: Visualization
    viz_cmd = "python scripts/generate_test_visualizations.py"
    run_command(viz_cmd, "Generating Performance & Stability Graphs")
    
    # Step 3: Final PDF Report
    report_cmd = "python scripts/generate_fyp_final_report.py"
    run_command(report_cmd, "Compiling 6-Chapter Final Project Report")
    
    print("\n" + "="*60)
    print("SUCCESS: ALL FORENSIC ASSETS GENERATED")
    print(f"1. Evidence Dashboard: {evidence_dir}/test_report.html")
    print(f"2. Final PDF Report: d:/FYP/MD-II/FYP_Final_Project_Report.pdf")
    print("="*60)

if __name__ == "__main__":
    main()
