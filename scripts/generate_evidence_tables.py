import os
import re
import csv
import ast
import glob
from datetime import datetime

def get_test_descriptions():
    """Harvest docstrings from all test functions."""
    descriptions = {}
    test_files = glob.glob('tests/**/*.py', recursive=True)
    for f in test_files:
        try:
            with open(f, 'r') as file:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        doc = ast.get_docstring(node)
                        if doc:
                            descriptions[node.name] = doc.strip().split('\n')[0]
                        else:
                            descriptions[node.name] = "Verifies system consistency."
        except Exception:
            continue
    return descriptions

def parse_full_logs(log_path):
    """Parse pytest output to extract test names and their status."""
    if not os.path.exists(log_path):
        return []
    
    results = []
    try:
        # PowerShell redirects often produce UTF-16 with BOM
        with open(log_path, 'r', encoding='utf-16') as f:
            lines = f.readlines()
    except (UnicodeError, UnicodeDecodeError):
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
    for line in lines:
        if "::" in line and ("PASSED" in line or "FAILED" in line):
            # Format: tests/test_ui.py::test_dashboard_access PASSED [ 5%]
            parts = line.split()
            full_test_path = parts[0]
            status = parts[1]
            test_name = full_test_path.split("::")[-1]
            file_name = full_test_path.split("::")[0]
            results.append({
                'name': test_name,
                'file': file_name,
                'status': status
            })
    return results

def generate_tables(results, descriptions, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Markdown Table for Report
    md_path = os.path.join(out_dir, "test_summary_table.md")
    with open(md_path, 'w') as f:
        f.write("# Forensic System Test Summary\n\n")
        f.write("| Test Case | Objective | Status |\n")
        f.write("| :--- | :--- | :--- |\n")
        for res in results:
            clean_name = res['name'].replace("_", " ").title()
            obj = descriptions.get(res['name'], "Verifies component integrity.")
            f.write(f"| {clean_name} | {obj} | **{res['status']}** |\n")
            
    print(f"Markdown table generated at: {md_path}")
    
    # 2. CSV for raw data reference
    csv_path = os.path.join(out_dir, "full_test_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Test Name', 'Objective', 'Status', 'File'])
        writer.writeheader()
        for res in results:
            writer.writerow({
                'Test Name': res['name'],
                'Objective': descriptions.get(res['name'], ""),
                'Status': res['status'],
                'File': res['file']
            })
    print(f"CSV table generated at: {csv_path}")

if __name__ == "__main__":
    log_file = r"d:\FYP\MD-II\Forensic_Audit_Results_Final\audit_logs\full_test_logs.txt"
    out_dir = r"d:\FYP\MD-II\Forensic_Audit_Results_Final\data_tables"
    
    print("Collecting test descriptions...")
    desc = get_test_descriptions()
    
    print("Parsing test logs...")
    test_results = parse_full_logs(log_file)
    
    if test_results:
        print(f"Generating evidence tables for {len(test_results)} tests...")
        generate_tables(test_results, desc, out_dir)
        print("Success!")
    else:
        print("Error: No test results found in logs. Ensure tests have completed.")
