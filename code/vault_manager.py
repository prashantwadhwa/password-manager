# vault_manager.py
import json

class Vault:
    def __init__(self):
        self.entries = {}

    def add_entry(self, site, username, password):
        self.entries[site] = {
            "username": username,
            "password": password
        }

    def get_entry(self, site):
        return self.entries.get(site)

    def list_sites(self):
        return list(self.entries.keys())

    def serialize(self) -> str:
        return json.dumps(self.entries)

    def deserialize(self, data: str):
        self.entries = json.loads(data)
