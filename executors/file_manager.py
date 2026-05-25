"""
executors/file_manager.py — One-by-One File Manager v8
Algoritma: persistent file list in session state
Supports: upload one-by-one, remove individual, add via GDrive
"""
import streamlit as st
from datetime import datetime


SESSION_KEY = "data_files_corpus"


def init_corpus():
    """Initialize empty corpus if not exists."""
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = []


def add_file(filename: str, content: bytes, source: str = "upload",
              source_url: str = "") -> int:
    """Add file to corpus. Returns index of added file."""
    init_corpus()
    st.session_state[SESSION_KEY].append({
        "id": len(st.session_state[SESSION_KEY]),
        "filename": filename,
        "content": content,
        "size_kb": len(content) / 1024,
        "source": source,           # "upload" or "gdrive"
        "source_url": source_url,
        "added_at": datetime.now().strftime("%H:%M:%S"),
    })
    return len(st.session_state[SESSION_KEY]) - 1


def remove_file(idx: int) -> bool:
    """Remove file at index. Returns success."""
    init_corpus()
    if 0 <= idx < len(st.session_state[SESSION_KEY]):
        st.session_state[SESSION_KEY].pop(idx)
        # Re-index
        for i, f in enumerate(st.session_state[SESSION_KEY]):
            f["id"] = i
        return True
    return False


def get_corpus() -> list:
    """Get all files."""
    init_corpus()
    return st.session_state[SESSION_KEY]


def clear_corpus():
    """Clear all files."""
    st.session_state[SESSION_KEY] = []


def get_corpus_summary() -> dict:
    """Get corpus statistics."""
    init_corpus()
    files = st.session_state[SESSION_KEY]
    upload_count = len([f for f in files if f["source"] == "upload"])
    gdrive_count = len([f for f in files if f["source"] == "gdrive"])
    total_size = sum(f["size_kb"] for f in files)
    return {
        "total": len(files),
        "upload": upload_count,
        "gdrive": gdrive_count,
        "total_size_kb": total_size,
    }
