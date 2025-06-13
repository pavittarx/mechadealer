from pathlib import Path
import json
from cryptography.fernet import Fernet


class CredentialsManager:
    def __init__(self, creds_dir=".creds"):
        self.creds_dir = Path(creds_dir)
        self.creds_file = self.creds_dir / "credentials.json"
        self.key_file = self.creds_dir / ".key"
        self._setup()

    def _setup(self):
        """Initialize the credentials directory and encryption key"""
        self.creds_dir.mkdir(exist_ok=True)

        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)

        self.fernet = Fernet(self._load_key())

        if not self.creds_file.exists():
            self._save_creds({})

    def _load_key(self):
        """Load the encryption key"""
        with open(self.key_file, "rb") as f:
            return f.read()

    def _load_creds(self):
        """Load and decrypt credentials"""
        if not self.creds_file.exists():
            return {}

        with open(self.creds_file, "rb") as f:
            encrypted_data = f.read()
            if not encrypted_data:
                return {}
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)

    def _save_creds(self, creds):
        """Encrypt and save credentials"""
        encrypted_data = self.fernet.encrypt(json.dumps(creds).encode())
        with open(self.creds_file, "wb") as f:
            f.write(encrypted_data)

    def set_credential(self, key: str, value: str):
        """Set a credential value"""
        creds = self._load_creds()
        creds[key] = value
        self._save_creds(creds)

    def get_credential(self, key: str) -> str | None:
        """Get a credential value"""
        creds = self._load_creds()
        return creds.get(key)

    def view_credentials(self):
        """View all credentials"""
        return self._load_creds()

    def delete_credential(self, key: str):
        """Delete a credential"""
        creds = self._load_creds()
        if key in creds:
            del creds[key]
            self._save_creds(creds)
