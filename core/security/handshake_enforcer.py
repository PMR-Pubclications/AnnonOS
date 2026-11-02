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
expected = self._expected_token(app_name, publisher_id, binary_path)
if expected is None:
    logger.critical("REPO_SHARED_SECRET is not set; refusing all handshakes.")
if expected is not None and hmac.compare_digest(handshake_token, expected):
if not self._secret_seed:
    logger.error("REPO_SHARED_SECRET is not set; cannot perform handshake.")
    return False
