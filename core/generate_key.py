"""
core/generate_key.py — Admin Tool: Generate & Re-encrypt Core Prompt
Jalankan SEKALI oleh admin untuk menghasilkan key baru.
JANGAN commit file ini ke GitHub jika berisi key asli.

Usage:
  python3 core/generate_key.py

Output:
  - core/encrypted_prompt.py (updated ciphertext)
  - Tampilkan key baru untuk di-set ke Streamlit Secrets
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.fernet import Fernet
from core.data import CORE_PROMPT_TEXT

print("=" * 65)
print("CORE PROMPT ENCRYPTION TOOL")
print("=" * 65)

# Generate key baru
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(CORE_PROMPT_TEXT.encode("utf-8"))

# Verifikasi
decrypted = Fernet(key).decrypt(encrypted).decode("utf-8")
assert decrypted == CORE_PROMPT_TEXT, "Encryption verification FAILED!"

# Simpan ciphertext
out_path = os.path.join(os.path.dirname(__file__), "encrypted_prompt.py")
with open(out_path, "w") as f:
    f.write('"""core/encrypted_prompt.py\n')
    f.write('Fernet-encrypted Core Prompt.\n')
    f.write('Key: Streamlit Secrets → PROMPT_ENCRYPT_KEY\n')
    f.write('"""\n')
    f.write(f'ENCRYPTED_CORE_PROMPT = {repr(encrypted)}\n')

print(f"\n✅ Encrypted prompt saved to: {out_path}")
print(f"   Plaintext  : {len(CORE_PROMPT_TEXT)} chars")
print(f"   Ciphertext : {len(encrypted)} bytes")
print()
print("=" * 65)
print("LANGKAH SELANJUTNYA:")
print("=" * 65)
print()
print("1. Copy key di bawah ini:")
print(f"\n   PROMPT_ENCRYPT_KEY = \"{key.decode()}\"\n")
print("2. Buka Streamlit Cloud → app Anda → Settings → Secrets")
print("3. Tambahkan baris di atas ke kolom Secrets")
print("4. Klik Save → app akan restart")
print()
print("5. Commit & push core/encrypted_prompt.py ke GitHub")
print("   (file ini aman — hanya berisi ciphertext)")
print()
print("⚠️  JANGAN commit key ini ke GitHub!")
print("⚠️  Key hanya boleh ada di Streamlit Secrets!")
