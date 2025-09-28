import os
import shutil
import streamlit as st
from typing import Optional


def copy_for_read(path: str) -> Optional[str]:
    """Workaround Windows locks: copy to temp file then read the copy."""
    try:
        base = os.path.basename(path)
        temp_dir = st.session_state.get("_temp_dir", os.path.dirname(path) or ".")
        os.makedirs(temp_dir, exist_ok=True)
        tmp_path = os.path.join(temp_dir, f"._reading_{base}.tmp")
        shutil.copyfile(path, tmp_path)
        return tmp_path
    except Exception:
        return None
