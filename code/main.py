from getpass import getpass
from crypto_utils import derive_key, encrypt_data, decrypt_data
from vault_manager import Vault
from config import VAULT_FILE
import os

vault = Vault()


def load_vault(master_password):
    if not os.path.exists(VAULT_FILE):
        return None
    try:
        key = derive_key(master_password)
        with open(VAULT_FILE, "rb") as f:
            encrypted = f.read()
        decrypted = decrypt_data(key, encrypted)
        vault.deserialize(decrypted.decode())
        return key
    except Exception:
        print("❌ Failed to load vault. Wrong password or corrupt file.")
        return None


def save_vault(key):
    data = vault.serialize().encode()
    encrypted = encrypt_data(key, data)
    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)
    print("✅ Vault saved to disk.")


def main():
    print("🔐 Welcome to CLI Password Manager")
    master_password = getpass("Enter master password: ")
    key = load_vault(master_password)

    if key is None:
        choice = input("Vault not found. Create new one? (y/n): ").lower()
        if choice != "y":
            return
        key = derive_key(master_password)
    while True:
        cmd = input("\nCommands: [add] [get] [list] [save] [exit] > ").lower()
        if cmd == "add":
            site = input("Website: ")
            username = input("Username: ")
            password = getpass("Password: ")
            vault.add_entry(site, username, password)
            print("✅ Entry added.")
        elif cmd == "get":
            site = input("Website: ")
            entry = vault.get_entry(site)
            if entry:
                print(
                    f"🔑 Username: {entry['username']}\n🔑 Password: {entry['password']}"
                )
            else:
                print("❌ Entry not found.")
        elif cmd == "list":
            for s in vault.list_sites():
                print(f"📌 {s}")
        elif cmd == "save":
            save_vault(key)
        elif cmd == "exit":
            print("👋 Goodbye!")
            break
        else:
            print("❓ Unknown command.")

if __name__ == "__main__":
    main()