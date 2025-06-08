from getpass import getpass
from crypto_utils import derive_key, encrypt_data, decrypt_data
from vault_manager import Vault
from config import VAULT_DIR
import os

vault = Vault()


def list_vaults():
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)
    return [f[:-4] for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]


def select_or_create_vault():
    vaults = list_vaults()
    if vaults:
        print("🔐 Available vaults:")
        for i, v in enumerate(vaults):
            print(f"  [{i+1}] {v}")
        choice = input(
            "Enter vault name or number (or type new to create one): "
        ).strip()
        if choice.lower() == "new":
            return create_vault()
        if choice.isdigit() and 1 <= int(choice) <= len(vaults):
            return vaults[int(choice) - 1]
        elif choice in vaults:
            return choice
        else:
            print("❌ Invalid selection.")
            return select_or_create_vault()
    else:
        print("📭 No vaults found. Let's create one.")
        return create_vault()


def create_vault():
    name = input("🆕 Enter new vault name: ").strip()
    path = os.path.join(VAULT_DIR, f"{name}.enc")
    if os.path.exists(path):
        print("❌ Vault already exists.")
        return select_or_create_vault()
    return name


def load_vault(vault_name, master_password):
    path = os.path.join(VAULT_DIR, f"{vault_name}.enc")
    vault = Vault()

    if not os.path.exists(path):
        return vault, derive_key(master_password)
    try:
        with open(path, "rb") as f:
            encrypted = f.read()
        key = derive_key(master_password)
        decrypted = decrypt_data(key, encrypted)
        vault.deserialize(decrypted.decode())
        return vault, key
    except Exception:
        print("❌ Incorrect password or corrupt vault.")
        return None, None


def save_vault(vault, vault_name, key):
    path = os.path.join(VAULT_DIR, f"{vault_name}.enc")
    data = vault.serialize().encode()
    encrypted = encrypt_data(key, data)
    with open(path, "wb") as f:
        f.write(encrypted)
    print("✅ Vault saved.")


def main():
    print("🔐 Welcome to Multi-Vault Password Manager")
    vault_name = select_or_create_vault()
    master_password = getpass(f"Enter password for vault '{vault_name}': ")
    vault, key = load_vault(vault_name, master_password)
    if not vault:
        return

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
            save_vault(vault, vault_name, key)
        elif cmd == "exit":
            confirm = input("💾 Do you want to save your vault before exiting? (y/n): ").strip().lower()
            if confirm == 'y':
                save_vault(vault, vault_name, key)
            print("👋 Goodbye!")
            break
        else:
            print("❓ Unknown command.")


if __name__ == "__main__":
    main()
