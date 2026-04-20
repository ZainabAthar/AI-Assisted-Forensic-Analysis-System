import pytest
import torch
import numpy as np
from pathlib import Path
import sys
import os
from PIL import Image

# Setup paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "Report generation" / "core"))

from dataset.dataset_test import TestDataset
from generate_forensic_report import ForensicReportGenerator

def test_dataset_normalization(tmp_path):
    """
    Unit Test: Verify that TestDataset correctly normalizes image data.
    """
    img_path = tmp_path / "test.jpg"
    # Create an image with known pixel values
    img_data = np.ones((100, 100, 3), dtype=np.uint8) * 128
    Image.fromarray(img_data).save(img_path)
    
    ds = TestDataset(list_img=[str(img_path)])
    tensor, path = ds[0]
    
    # Value should be approx 128 / 256.0 = 0.5
    assert tensor.shape == (3, 100, 100)
    assert torch.allclose(tensor[0, 0, 0], torch.tensor(0.5), atol=0.01)
    assert path == str(img_path)

def test_forensic_explanation_logic():
    """
    Unit Test: Verify high-level interpretation logic for forensic scores.
    """
    gen = ForensicReportGenerator()
    
    # Authentic case
    expl_auth = gen._generate_image_explanation(0.05)
    assert "minimal" in expl_auth.lower()
    assert "authentic" in expl_auth.lower()
    
    # Tampered case
    expl_tamp = gen._generate_image_explanation(0.95)
    assert "very high" in expl_tamp.lower()
    assert "tampering" in expl_tamp.lower()
    assert "anomalies" in expl_tamp.lower()

def test_report_image_resizing(tmp_path):
    """
    Unit Test: Verify internal image resizing logic for PDFs.
    """
    large_img = tmp_path / "large.jpg"
    Image.new('RGB', (2000, 2000), color='red').save(large_img)
    
    gen = ForensicReportGenerator()
    resized_path = gen._resize_image_for_pdf(str(large_img), max_width=500, max_height=500)
    
    assert os.path.exists(resized_path)
    with Image.open(resized_path) as img:
        assert img.width <= 500
        assert img.height <= 500
    
    # Cleanup
    if os.path.exists(resized_path):
        os.remove(resized_path)
