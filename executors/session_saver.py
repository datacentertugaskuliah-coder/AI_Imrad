"""
executors/session_saver.py — Session Persistence v15
JSON export/import untuk backup sesi saat disconnect Streamlit Cloud
"""
import json
from datetime import datetime
import streamlit as st


SAVEABLE_KEYS = [
    "v9_topic", "v9_method", "v9_novelty", "v9_quant", "v9_keywords",
    "v9_field", "v9_journal_url",
    "v9_main_filename", "v11_ref_filename", "v11_style_filename",
    "v13_corpus_quant", "v15_authors", "v15_credit_statement",
]


def export_session_to_json() -> tuple[str, str]:
    """Serialize session state ke JSON. Returns (json_string, filename)."""
    data = {"_version": "v15", "_saved_at": datetime.now().isoformat()}
    for key in SAVEABLE_KEYS:
        val = st.session_state.get(key)
        if val is not None and not callable(val):
            if isinstance(val, (str, int, float, bool, list, dict)):
                data[key] = val
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    fname = f"research_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return json_str, fname


def import_session_from_json(json_bytes: bytes) -> tuple[bool, str]:
    """Load session state from JSON file. Returns (success, message)."""
    try:
        data = json.loads(json_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        return False, f"File JSON tidak valid: {str(e)[:80]}"

    restored = 0
    for key, val in data.items():
        if key.startswith("_"):
            continue
        if key in SAVEABLE_KEYS:
            st.session_state[key] = val
            restored += 1

    saved_at = data.get("_saved_at", "tidak diketahui")
    return True, f"✅ {restored} field dipulihkan dari sesi {saved_at[:19]}"


def get_session_summary() -> dict:
    """Get summary of current saveable session state."""
    filled = 0
    total = len(SAVEABLE_KEYS)
    for key in SAVEABLE_KEYS:
        val = st.session_state.get(key)
        if val:
            filled += 1
    return {
        "filled": filled,
        "total": total,
        "percent": int(filled / total * 100) if total else 0,
    }
