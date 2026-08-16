import os
import hashlib
import tempfile
from typing import Tuple

def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def save_temp_file(file_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1] or ".pdf"
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"gmc_doc_{compute_file_hash(file_bytes)[:12]}{ext}")
    with open(temp_path, "wb") as f:
        f.write(file_bytes)
    return temp_path

def cleanup_temp_file(filepath: str) -> None:
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass
