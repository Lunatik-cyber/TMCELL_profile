import json
import base64
import os

ACCOUNTS_FILE = "accounts.dat"
ENC_KEY = b"R7p2kT8vQ1wZ9xM3uJ5sL8nC4eV0aB6d"  # Замените на свой ключ! (длина 16/24/32 байта)

def xor_crypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def save_accounts(accounts: dict):
    json_data = json.dumps(accounts, ensure_ascii=False).encode("utf-8")
    encrypted = xor_crypt(json_data, ENC_KEY)
    encoded = base64.b64encode(encrypted)
    with open(ACCOUNTS_FILE, "wb") as f:
        f.write(encoded)

def load_accounts() -> dict:
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    with open(ACCOUNTS_FILE, "rb") as f:
        encoded = f.read()
    try:
        encrypted = base64.b64decode(encoded)
        json_data = xor_crypt(encrypted, ENC_KEY)
        return json.loads(json_data.decode("utf-8"))
    except Exception:
        print("Ошибка расшифровки файла аккаунтов! Файл будет очищен.")
        os.remove(ACCOUNTS_FILE)
        return {}