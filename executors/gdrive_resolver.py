"""
executors/gdrive_resolver.py v16 — PURE IN-MEMORY (no disk write)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Perubahan v16:
  - HAPUS gdown.download() dan gdown.download_folder() (keduanya tulis ke disk)
  - Gunakan requests + BytesIO murni (memory only)
  - Folder: scrape file IDs dari HTML → fetch per file in-memory
  - Confirm-token handler untuk file > 25MB tanpa disk
  - Pesan error spesifik: 403 private / 404 not found / rate-limit
"""
import re
from io import BytesIO


# ── URL type detection ─────────────────────────────────────────────────────────

def detect_gdrive_type(url: str) -> tuple:
    """Detect file/folder/unknown. Returns (type, resource_id)."""
    if not url:
        return "unknown", None
    url = url.strip()
    ul = url.lower()
    if "drive.google.com" not in ul and "docs.google.com" not in ul:
        return "unknown", None

    # Folder patterns
    for p in [r"/drive/folders/([a-zA-Z0-9_-]{15,})",
              r"/folders/([a-zA-Z0-9_-]{15,})"]:
        m = re.search(p, url)
        if m:
            return "folder", m.group(1)

    # File patterns
    for p in [r"/file/d/([a-zA-Z0-9_-]{15,})",
              r"[?&]id=([a-zA-Z0-9_-]{15,})",
              r"/d/([a-zA-Z0-9_-]{15,})",
              r"/document/d/([a-zA-Z0-9_-]{15,})",
              r"/spreadsheets/d/([a-zA-Z0-9_-]{15,})"]:
        m = re.search(p, url)
        if m:
            return "file", m.group(1)

    return "unknown", None


def parse_gdrive_file_id(url: str):
    t, rid = detect_gdrive_type(url)
    return rid if t == "file" else None


def validate_gdrive_url(url: str) -> tuple:
    """Validate URL. Returns (is_valid, message)."""
    if not url or not url.strip():
        return False, "URL kosong"
    t, rid = detect_gdrive_type(url)
    if t == "folder":
        return True, f"📁 Folder Google Drive · ID: {rid[:10]}..."
    if t == "file":
        return True, f"📄 File Google Drive · ID: {rid[:10]}..."
    return False, ("URL tidak dikenali. Format:\n"
                   "• File  : drive.google.com/file/d/FILE_ID/view\n"
                   "• Folder: drive.google.com/drive/folders/FOLDER_ID")


# ── PURE IN-MEMORY file fetch (no disk) ─────────────────────────────────────────

def _extract_confirm_token(response) -> str:
    """Extract confirm token for large files (>25MB virus scan page)."""
    # Check cookies
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    # Fallback: search HTML
    try:
        m = re.search(r'confirm=([0-9A-Za-z_-]+)', response.text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""


def fetch_file_inmemory(file_id: str) -> tuple:
    """
    Fetch single file PURELY in-memory (BytesIO, no disk).
    Returns (bytes | None, filename, error).
    """
    try:
        import requests
    except ImportError:
        return None, "", "Library requests tidak tersedia."

    session = requests.Session()
    base_url = "https://drive.google.com/uc?export=download"

    try:
        # Initial request
        response = session.get(base_url, params={"id": file_id},
                                stream=True, timeout=30,
                                headers={"User-Agent": "Mozilla/5.0"})

        # Check status
        if response.status_code == 404:
            return None, "", "_NOT_FOUND_"
        if response.status_code == 403:
            return None, "", "_PRIVATE_"

        # Check for confirm token (large files)
        token = _extract_confirm_token(response)
        if token:
            response = session.get(base_url,
                                    params={"id": file_id, "confirm": token},
                                    stream=True, timeout=60,
                                    headers={"User-Agent": "Mozilla/5.0"})

        # Read content into BytesIO (memory only)
        buffer = BytesIO()
        total = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                buffer.write(chunk)
                total += len(chunk)
                if total > 100 * 1024 * 1024:  # 100MB safety cap
                    break

        buffer.seek(0)
        content = buffer.read()

        # Validate content
        if len(content) < 50:
            return None, "", "_EMPTY_"

        # Check if we got an HTML error page instead of file
        if content[:200].lower().startswith(b"<!doctype html") or \
           content[:100].lower().startswith(b"<html"):
            # Could be a permission page
            if b"sign in" in content[:2000].lower() or \
               b"request access" in content[:2000].lower():
                return None, "", "_PRIVATE_"
            return None, "", "_HTML_RESPONSE_"

        filename = _detect_filename(content, file_id)
        return content, filename, ""

    except requests.exceptions.Timeout:
        return None, "", "_TIMEOUT_"
    except Exception as e:
        return None, "", f"_ERROR_{str(e)[:60]}"


def _detect_filename(content: bytes, file_id: str) -> str:
    """Detect file extension from magic bytes."""
    if content[:4] == b"%PDF":
        ext = ".pdf"
    elif content[:2] == b"PK":
        ext = ".docx"  # could be xlsx too, but docx more common
    elif content[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        ext = ".doc"  # old office format
    elif all(c < 128 for c in content[:100]):
        ext = ".txt"
    else:
        ext = ".bin"
    return f"gdrive_{file_id[:8]}{ext}"


def _diagnose(error_code: str, resource_id: str) -> str:
    """Convert internal error code to user-friendly message."""
    diagnoses = {
        "_NOT_FOUND_": (
            f"❌ File/folder tidak ditemukan (404).\n"
            f"ID: {resource_id[:12]}...\n"
            f"Periksa apakah link benar dan file belum dihapus."
        ),
        "_PRIVATE_": (
            f"🔒 File/folder masih privat (butuh login).\n"
            f"Solusi: Buka di GDrive → Share → 'Anyone with the link' → 'Viewer' → Save."
        ),
        "_EMPTY_": "⚠️ File kosong atau gagal terbaca.",
        "_TIMEOUT_": "⏱️ Timeout — file terlalu besar atau koneksi lambat. Coba file < 50MB.",
        "_HTML_RESPONSE_": (
            "⚠️ Google mengembalikan halaman web, bukan file.\n"
            "Pastikan link mengarah ke file/folder yang valid dan public."
        ),
    }
    if error_code in diagnoses:
        return diagnoses[error_code]
    if error_code.startswith("_ERROR_"):
        return f"⚠️ Error: {error_code[7:]}"
    return error_code


# ── PURE IN-MEMORY folder fetch (no disk) ───────────────────────────────────────

def list_folder_files(folder_id: str) -> tuple:
    """
    Scrape file IDs from folder HTML page (public folders only).
    Returns (list_of_file_ids, error).
    """
    try:
        import requests
    except ImportError:
        return [], "Library requests tidak tersedia."

    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    try:
        r = requests.get(folder_url, timeout=30,
                          headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 404:
            return [], "_NOT_FOUND_"
        if r.status_code == 403:
            return [], "_PRIVATE_"

        html = r.text

        # Check if private (redirect to login)
        if "accounts.google.com/ServiceLogin" in html or \
           ("sign in" in html[:5000].lower() and "request access" in html.lower()):
            return [], "_PRIVATE_"

        # Extract file IDs from HTML
        # Google embeds file data as ["FILE_ID",[...
        file_ids = set()

        # Pattern 1: data-id attribute
        for m in re.finditer(r'data-id="([a-zA-Z0-9_-]{20,})"', html):
            file_ids.add(m.group(1))

        # Pattern 2: in embedded JSON ["ID",["parent"]
        for m in re.finditer(r'\["([a-zA-Z0-9_-]{25,})",\["' + re.escape(folder_id), html):
            file_ids.add(m.group(1))

        # Pattern 3: /file/d/ID links
        for m in re.finditer(r'/file/d/([a-zA-Z0-9_-]{20,})', html):
            file_ids.add(m.group(1))

        # Remove folder_id itself if captured
        file_ids.discard(folder_id)

        if not file_ids:
            return [], "_NO_FILES_FOUND_"

        return list(file_ids), ""

    except requests.exceptions.Timeout:
        return [], "_TIMEOUT_"
    except Exception as e:
        return [], f"_ERROR_{str(e)[:60]}"


def read_folder_inmemory(folder_url: str) -> tuple:
    """
    Read all files in a public folder PURELY in-memory.
    Returns (list_of_(bytes, filename, ""), error_message).
    """
    url_type, folder_id = detect_gdrive_type(folder_url)
    if url_type != "folder" or not folder_id:
        return [], "Bukan URL folder Google Drive."

    # Step 1: list file IDs
    file_ids, err = list_folder_files(folder_id)
    if err:
        return [], _diagnose(err, folder_id) if err.startswith("_") else err
    if not file_ids:
        return [], (
            "Folder kosong atau file ID tidak terdeteksi.\n"
            "Pastikan folder berisi file dan diset 'Anyone with the link can view'."
        )

    # Step 2: fetch each file in-memory
    results = []
    errors = []
    for fid in file_ids[:30]:  # cap 30 files
        content, fname, ferr = fetch_file_inmemory(fid)
        if content:
            results.append((content, fname, ""))
        else:
            errors.append(f"{fid[:8]}: {ferr}")

    if not results:
        return [], (
            "Tidak ada file yang berhasil dibaca dari folder.\n"
            "Pastikan SEMUA file di dalam folder juga public, "
            "atau set folder ke 'Anyone with the link can view'."
        )

    return results, ""


# ── Public API (backward compatible) ────────────────────────────────────────────

def fetch_from_gdrive(url: str) -> tuple:
    """
    Fetch single file in-memory. Returns (bytes | None, filename, error).
    v16: pure in-memory, no disk.
    """
    url_type, file_id = detect_gdrive_type(url)
    if url_type == "folder":
        return None, "", "Ini URL folder. Gunakan read_folder_inmemory()."
    if not file_id:
        return None, "", "File ID tidak valid."
    content, fname, err = fetch_file_inmemory(file_id)
    if err and err.startswith("_"):
        return None, "", _diagnose(err, file_id)
    return content, fname, err


def fetch_folder_files(url: str) -> tuple:
    """
    Read all files in folder in-memory.
    Returns (list_of_(bytes, filename, ""), error).
    v16: pure in-memory, no disk.
    """
    return read_folder_inmemory(url)


def fetch_smart(url: str) -> tuple:
    """Unified entry. Returns (url_type, files_list, error)."""
    url_type, rid = detect_gdrive_type(url)
    if url_type == "folder":
        files, err = read_folder_inmemory(url)
        return "folder", files, err
    elif url_type == "file":
        content, fname, err = fetch_from_gdrive(url)
        return ("file", [(content, fname, "")], "") if content else ("file", [], err)
    return "unknown", [], "URL tidak dikenali."
