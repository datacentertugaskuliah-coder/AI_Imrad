"""
executors/gdrive_resolver.py v12
FIX v12:
  - Detect dan handle URL FOLDER Google Drive
  - Pattern regex tambahan: /drive/folders/{FOLDER_ID}
  - fetch_folder() via gdown.download_folder()
  - fetch_smart() sebagai single entry point
"""
import re, os, tempfile


# ── URL type detection ─────────────────────────────────────────────────────────

def detect_gdrive_type(url: str) -> tuple[str, str | None]:
    """
    Detect whether URL is a file or folder.
    Returns ("folder", folder_id) | ("file", file_id) | ("unknown", None)
    """
    if not url:
        return "unknown", None
    url = url.strip()
    url_lower = url.lower()
    if "drive.google.com" not in url_lower and "docs.google.com" not in url_lower:
        return "unknown", None

    # FOLDER detection first (before file, to avoid false positives)
    folder_patterns = [
        r"/drive/folders/([a-zA-Z0-9_-]{15,})",
        r"/folders/([a-zA-Z0-9_-]{15,})",
    ]
    for p in folder_patterns:
        m = re.search(p, url)
        if m:
            return "folder", m.group(1)

    # FILE detection
    file_patterns = [
        r"/file/d/([a-zA-Z0-9_-]{15,})",
        r"[?&]id=([a-zA-Z0-9_-]{15,})",
        r"/d/([a-zA-Z0-9_-]{15,})",
        r"/open\?id=([a-zA-Z0-9_-]{15,})",
        r"/uc\?.*id=([a-zA-Z0-9_-]{15,})",
        r"/document/d/([a-zA-Z0-9_-]{15,})",
    ]
    for p in file_patterns:
        m = re.search(p, url)
        if m:
            return "file", m.group(1)

    return "unknown", None


def parse_gdrive_file_id(url: str) -> str | None:
    """Backward-compat: returns file_id if it's a file URL."""
    url_type, rid = detect_gdrive_type(url)
    return rid if url_type == "file" else None


def validate_gdrive_url(url: str) -> tuple[bool, str]:
    """Validate URL and return type info."""
    if not url or not url.strip():
        return False, "URL kosong"
    url_type, rid = detect_gdrive_type(url)
    if url_type == "folder":
        return True, f"📁 Folder Google Drive · ID: {rid[:10]}..."
    elif url_type == "file":
        return True, f"📄 File Google Drive · ID: {rid[:10]}..."
    else:
        return False, (
            "URL tidak dikenali. Format yang didukung:\n"
            "• File  : drive.google.com/file/d/FILE_ID/view\n"
            "• Folder: drive.google.com/drive/folders/FOLDER_ID"
        )


# ── File download ──────────────────────────────────────────────────────────────

def fetch_from_gdrive(url: str) -> tuple[bytes | None, str, str]:
    """
    Fetch single file. Returns (bytes, filename, error).
    Kept for backward compatibility — use fetch_smart() for new code.
    """
    url_type, file_id = detect_gdrive_type(url)
    if url_type == "folder":
        return None, "", "Ini URL folder. Gunakan fetch_folder_files() untuk folder."
    if not file_id:
        return None, "", "File ID tidak valid."
    return _fetch_file_bytes(file_id)


def _fetch_file_bytes(file_id: str) -> tuple[bytes | None, str, str]:
    """Download single file by ID. Method 1: gdown, Method 2: requests."""
    # Method 1: gdown
    try:
        import gdown
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp_path = tmp.name
        dl_url = f"https://drive.google.com/uc?id={file_id}"
        result = gdown.download(dl_url, tmp_path, quiet=True, fuzzy=True)
        if result and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 100:
            with open(tmp_path, "rb") as f:
                content = f.read()
            os.unlink(tmp_path)
            return content, _detect_ext(content, file_id), ""
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    except Exception:
        pass

    # Method 2: requests direct
    try:
        import requests
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        r = requests.get(url, allow_redirects=True, timeout=20,
                          headers={"User-Agent": "Mozilla/5.0"})
        if r.ok and len(r.content) > 100 and b"<html" not in r.content[:200].lower():
            return r.content, _detect_ext(r.content, file_id), ""
    except Exception:
        pass

    return None, "", (
        "Download gagal. Pastikan:\n"
        "1. File diset 'Anyone with the link can view'\n"
        "2. File berukuran < 25MB\n"
        "3. Format: .pdf, .docx, atau .txt"
    )


def _detect_ext(content: bytes, file_id: str) -> str:
    if content[:4] == b"%PDF":       ext = ".pdf"
    elif content[:2] == b"PK":       ext = ".docx"
    elif all(c < 128 for c in content[:50]): ext = ".txt"
    else:                             ext = ".bin"
    return f"gdrive_{file_id[:8]}{ext}"


# ── Folder download ────────────────────────────────────────────────────────────

def fetch_folder_files(folder_url: str) -> tuple[list, str]:
    """
    Download all files in a Google Drive folder.
    Returns (list_of_tuples, error_message)
    Each tuple: (file_bytes, filename, "")
    """
    url_type, folder_id = detect_gdrive_type(folder_url)
    if url_type != "folder" or not folder_id:
        return [], "Bukan URL folder Google Drive."

    results = []
    tmpdir = None

    try:
        import gdown
        tmpdir = tempfile.mkdtemp()
        folder_dl_url = f"https://drive.google.com/drive/folders/{folder_id}"
        gdown.download_folder(
            folder_dl_url, output=tmpdir,
            quiet=True, use_cookies=False
        )
        # Collect all downloaded files
        for fname in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, fname)
            if os.path.isfile(fpath):
                with open(fpath, "rb") as f:
                    content = f.read()
                if len(content) > 0:
                    results.append((content, fname, ""))
        # Cleanup
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

        if results:
            return results, ""
        return [], "Tidak ada file yang berhasil diunduh dari folder."

    except Exception as e:
        if tmpdir:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)
        err_str = str(e)
        if "Permission" in err_str or "cannot" in err_str.lower():
            return [], (
                "Folder tidak dapat diakses.\n"
                "Buka GDrive → klik kanan folder → Share → "
                "'Anyone with the link can view' → coba lagi."
            )
        return [], f"Download folder gagal: {err_str[:100]}"


# ── Smart unified entry point ──────────────────────────────────────────────────

def fetch_smart(url: str) -> tuple[str, list, str]:
    """
    Single entry point for any GDrive URL.
    Returns (url_type, list_of_(bytes,filename,error), error_message)
    url_type: "file" | "folder" | "unknown"
    """
    url_type, resource_id = detect_gdrive_type(url)

    if url_type == "folder":
        files, err = fetch_folder_files(url)
        return "folder", files, err

    elif url_type == "file":
        content, fname, err = _fetch_file_bytes(resource_id)
        if content:
            return "file", [(content, fname, "")], ""
        return "file", [], err

    else:
        return "unknown", [], (
            "URL tidak dikenali. Format yang didukung:\n"
            "• File: drive.google.com/file/d/FILE_ID/view\n"
            "• Folder: drive.google.com/drive/folders/FOLDER_ID"
        )
