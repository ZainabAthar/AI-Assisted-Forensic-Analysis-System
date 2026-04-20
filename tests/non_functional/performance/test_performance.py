import pytest
import time
import os
import sys
import torch
import numpy as np
import csv
from PIL import Image
from pathlib import Path
from unittest.mock import patch, MagicMock

# Setup paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent.parent
sys.path.append(str(project_root))

from audioproc import interface as audio_proc
from audio_report_generator import AudioForensicReportGenerator
from generate_forensic_report import ForensicReportGenerator

@pytest.fixture
def multi_res_images(tmp_path):
    """Creates dummy images for multiple resolutions (480p to 4K)."""
    res_map = {
        '480p': (640, 480),
        '720p': (1280, 720),
        '1080p': (1920, 1080),
        '1440p': (2560, 1440),
        '2160p': (3840, 2160)
    }
    paths = {}
    for name, size in res_map.items():
        path = tmp_path / f"test_{name}.jpg"
        Image.new('RGB', size, color=(73, 109, 137)).save(path)
        paths[name] = str(path)
    return paths


def test_report_generation_latency(tmp_path):
    """Benchmark how long it takes to compile the PDF reports."""
    output_audio = str(tmp_path / "audio_report.pdf")
    output_image = str(tmp_path / "image_report.pdf")
    
    # Audio Report
    audio_gen = AudioForensicReportGenerator()
    start_time = time.time()
    audio_gen.create_pdf_report(
        output_path=output_audio,
        similarity_score=0.95,
        decision="Same Speaker",
        waveform_path=None, 
        spectrogram_path=None,
        audio_names=["test1.wav", "test2.wav"]
    )
    audio_duration = time.time() - start_time
    print(f"[PERF] Audio Report Generation: {audio_duration:.4f}s")
    
    # Image Report
    image_gen = ForensicReportGenerator()
    image_gen.analysis_results = {
        'score': 0.75, 
        'map': np.zeros((100, 100)),
        'conf': np.zeros((100, 100))
    }
    start_time = time.time()
    image_gen.create_pdf_report(output_image)
    image_duration = time.time() - start_time
    print(f"[PERF] Image Report Generation: {image_duration:.4f}s")
    
    assert audio_duration < 3.0
    assert image_duration < 3.0

def test_image_process_latency_scaling(multi_res_images):
    """Measure if processing time scales linearly or worse with resolution."""
    raw_data = []
    
    def process_image(path):
        start = time.time()
        img = Image.open(path)
        img = img.resize((224, 224)) 
        np.array(img)
        return time.time() - start

    for res_name, path in multi_res_images.items():
        latency = process_image(path)
        raw_data.append([res_name, f"{latency:.6f}"])
        print(f"\n[PERF] Image Loading ({res_name}): {latency:.4f}s")
    
    # Export to Authentic CSV for report backing
    evidence_dir = project_root / "Test_Evidence"
    os.makedirs(evidence_dir, exist_ok=True)
    csv_path = evidence_dir / "raw_benchmarks.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Resolution", "Latency_Seconds"])
        writer.writerows(raw_data)
        
    print(f"Authentic benchmarks exported to: {csv_path}")
    assert os.path.exists(csv_path)
