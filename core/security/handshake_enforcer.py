@staticmethod
def _shared_secret() -> Optional[bytes]:
    secret = os.environ.get("REPO_SHARED_SECRET")
    return secret.encode("utf-8") if secret else None

def _expected_token(self, app_name: str, publisher_id: str, binary_path: str) -> Optional[str]:
    secret = self._shared_secret()
    if secret is None:
        return None
    message = f"{app_name}:{publisher_id}:{binary_path}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()
