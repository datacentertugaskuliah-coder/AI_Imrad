"""
core/prompt_vault.py — Secure Core Prompt Vault v12
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algoritma keamanan:
  1. CORE_PROMPT_TEXT dihapus dari core/data.py
  2. Hanya ciphertext (Fernet) yang ada di repo
  3. Key tersimpan di Streamlit Cloud Secrets (PROMPT_ENCRYPT_KEY)
  4. Decrypt terjadi di memory saat runtime, tidak pernah di-write ke file
  5. Jika key tidak ada → fallback graceful (tampilkan placeholder)

Apa yang aman:
  ✅ GitHub repo: hanya berisi ciphertext gibberish
  ✅ Streamlit Secrets: key terenkripsi AES-256 oleh Streamlit
  ✅ Memory: decrypt hanya saat diperlukan, tidak di-cache ke disk
  ✅ Akses: hanya pemilik akun Streamlit yang bisa set/baca Secrets

Apa yang TIDAK bisa dilindungi:
  ⚠️  Jika user sudah login ke dashboard → prompt ditampilkan di halaman Core Prompt
  ⚠️  Solusi: Pisahkan akses Core Prompt dari akses umum (dual password)
"""
import streamlit as st
from functools import lru_cache

# Lazy import untuk efisiensi
def _get_fernet():
    try:
        from cryptography.fernet import Fernet
        return Fernet
    except ImportError:
        return None

def get_core_prompt() -> str:
    """
    Decrypt dan kembalikan Core Prompt.
    Key dari Streamlit Secrets → decrypt ciphertext → return plaintext.
    Plaintext hanya ada di memory, tidak ditulis ke file.
    """
    # 1. Ambil ciphertext dari encrypted_prompt.py
    try:
        from core.encrypted_prompt import ENCRYPTED_CORE_PROMPT
        ciphertext = ENCRYPTED_CORE_PROMPT
    except ImportError:
        return _fallback_prompt("encrypted_prompt.py tidak ditemukan")

    # 2. Ambil key dari Streamlit Secrets
    try:
        encrypt_key = st.secrets.get("PROMPT_ENCRYPT_KEY", "")
        if not encrypt_key:
            return _fallback_prompt("PROMPT_ENCRYPT_KEY tidak ditemukan di Secrets")
    except Exception:
        # Fallback untuk local dev tanpa Streamlit context
        try:
            import toml
            with open(".streamlit/secrets.toml") as f:
                secrets = toml.load(f)
            encrypt_key = secrets.get("PROMPT_ENCRYPT_KEY", "")
        except Exception:
            return _fallback_prompt("Tidak dapat membaca Secrets")

    # 3. Decrypt
    Fernet = _get_fernet()
    if not Fernet:
        return _fallback_prompt("Library 'cryptography' tidak terinstall")

    try:
        cipher = Fernet(encrypt_key.encode() if isinstance(encrypt_key, str) else encrypt_key)
        plaintext = cipher.decrypt(ciphertext).decode("utf-8")
        return plaintext
    except Exception as e:
        return _fallback_prompt(f"Decrypt gagal: {str(e)[:50]}")


def _fallback_prompt(reason: str) -> str:
    return (
        f"[CORE PROMPT ENCRYPTED — {reason}]\n"
        "Untuk mengakses Core Prompt:\n"
        "1. Set PROMPT_ENCRYPT_KEY di Streamlit Cloud Secrets\n"
        "2. Pastikan library 'cryptography' ada di requirements.txt\n"
        "3. Hubungi administrator sistem"
    )


def is_prompt_available() -> bool:
    """Check apakah Core Prompt bisa didekripsi tanpa error."""
    p = get_core_prompt()
    return not p.startswith("[CORE PROMPT ENCRYPTED")


def get_prompt_status() -> dict:
    """Return status info untuk debugging (tidak expose prompt itu sendiri)."""
    try:
        from core.encrypted_prompt import ENCRYPTED_CORE_PROMPT
        has_ciphertext = True
        ct_len = len(ENCRYPTED_CORE_PROMPT)
    except ImportError:
        has_ciphertext = False
        ct_len = 0

    try:
        key = st.secrets.get("PROMPT_ENCRYPT_KEY", "")
        has_key = bool(key)
    except Exception:
        has_key = False

    return {
        "has_ciphertext": has_ciphertext,
        "ciphertext_bytes": ct_len,
        "has_key": has_key,
        "is_available": is_prompt_available(),
    }
