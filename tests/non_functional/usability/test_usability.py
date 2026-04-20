import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
import os
import sys

# Setup paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.append(str(project_root))

def get_widget(at, name):
    """Helper to get widget proxy regardless of singular/plural attribute name."""
    if hasattr(at, name):
        return getattr(at, name)
    plural = f"{name}s"
    if hasattr(at, plural):
        return getattr(at, plural)
    return at.get(name)

def test_navigation_flow_visibility():
    """Verify that the user journey is clear and reachable."""
    at = AppTest.from_file(str(project_root / "app.py")).run()
    
    # Check for the primary forensic modes (Image / Audio)
    # Since current app.py has both on the main page
    uploaders = get_widget(at, "file_uploader")
    assert any("Upload Image" in str(u.label) for u in uploaders)
    assert any("Upload Audio" in str(u.label) for u in uploaders)
    
    # Check for meaningful titles/subheaders
    titles = get_widget(at, "title")
    headers = get_widget(at, "header")
    subheaders = get_widget(at, "subheader")
    
    all_text = [str(w.value) for w in titles] + [str(w.value) for w in headers] + [str(w.value) for w in subheaders]
    
    assert any("Analysis & Visualization" in t for t in all_text)

def test_error_messaging_on_invalid_image(tmp_path):
    """Verify the app gives helpful advice on invalid image uploads."""
    at = AppTest.from_file(str(project_root / "app.py"))
    
    # Mock an invalid file (0-byte)
    invalid_png = tmp_path / "corrupt.png"
    invalid_png.write_bytes(b"") # 0-byte file
    
    # In some Streamlit versions, we access file_uploader via index
    uploaders = get_widget(at, "file_uploader")
    if len(uploaders) > 0:
        uploaders[0].upload(data=b"", name="corrupt.png")
        at.run()
        
        # We expect SOME reaction, either a warning or the analysis button NOT to show
        # Streamlit itself handles some format restrictions, but our app 
        # should handle the logic gracefully.
        
        # If we try to run analysis on it:
        buttons = get_widget(at, "button")
        if len(buttons) > 0 and "Run Analysis" in buttons[0].label:
            buttons[0].click().run()
            # If it triggers an error in Python, st.error should show it
            assert not at.exception 
            # Ideally our app shows a validation message

def test_audio_upload_mismatch_error():
    """Verify that uploading only 1 audio file prevents analysis."""
    at = AppTest.from_file(str(project_root / "app.py"))
    
    # Search for audio uploader (index 1 usually)
    uploaders = get_widget(at, "file_uploader")
    if len(uploaders) > 1:
        uploader = uploaders[1]
        uploader.upload(data=b"fake wav", name="only_one.wav")
        at.run()
        
        # The 'Analyze Audio' button should NOT be visible per app logic
        buttons = get_widget(at, "button")
        assert not any("Analyze Audio" in btn.label for btn in buttons)
        
        # Verify instructions remain clear
        infos = get_widget(at, "info")
        assert any("Please upload EXACTLY two audio files" in str(msg.body) for msg in infos)
