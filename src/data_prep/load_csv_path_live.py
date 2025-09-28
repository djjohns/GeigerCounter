import os
import pandas as pd
from typing import Optional, Tuple
from . import normalize_df, copy_for_read


def load_csv_path_live(path: str) -> Tuple[pd.DataFrame, str, Optional[float]]:
    """
    Live-mode read: no cache. Returns (df, info_message, mtime).
    We read fresh on every rerun; auto-refresh triggers reruns.
    """
    try:
        mtime = os.path.getmtime(path)
    except FileNotFoundError:
        return pd.DataFrame(), f"File not found: {path}", None
    except Exception as e:
        return pd.DataFrame(), f"Could not stat file: {e}", None

    # Try direct read first
    try:
        df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8")
        return normalize_df(df), "", mtime
    except Exception as e1:
        # If locked, try temp copy
        tmp = copy_for_read(path)
        if tmp:
            try:
                df = pd.read_csv(
                    tmp, engine="python", on_bad_lines="skip", encoding="utf-8"
                )
                return (
                    normalize_df(df),
                    "Read from temporary copy (source locked).",
                    mtime,
                )
            except Exception as e2:
                return pd.DataFrame(), f"Read failed (direct: {e1}) (temp: {e2})", mtime
            finally:
                try:
                    os.remove(tmp)
                except Exception:
                    pass
        else:
            return pd.DataFrame(), f"Read failed (direct): {e1}", mtime
