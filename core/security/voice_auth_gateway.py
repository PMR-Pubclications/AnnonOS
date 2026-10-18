import sqlite3
from civilian_secure_db import CivilianSecureDatabase

class VoiceAuthGateway:
    def __init__(self, db_path: str = "/opt/annonos/data/civilian_profiles.db"):
        self.db_path = db_path
        self.keystore = AnnonOSHardwareKeystore()
        self.ledger = MerkleLedger()
        self.trust_shell_override_active = False

    def authenticate_via_voice(self, spoken_passphrase: str) -> bool:
        """Dynamically checks the encrypted civilian database for a matching voice signature."""
        logger.info("Processing voice-activated authentication request against secure civilian database...")

        if self.check_trust_shell_remote_override():
            logger.info("ACCESS GRANTED: Trust-Shell remote override active.")
            return True

        # Query all active profiles from the encrypted secure database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, full_name, voice_signature_hash FROM civilian_profiles WHERE active = 1;")
            rows = cursor.fetchall()
            conn.close()

            spoken_hash = hashlib.sha256(spoken_passphrase.strip().encode('utf-8')).hexdigest()

            for row in rows:
                profile_id = row["id"]
                encrypted_voice_hash = row["voice_signature_hash"]
                
                # Decrypt the stored voice signature hash using the hardware keystore
                decrypted_voice_hash = self.keystore.decrypt_payload(encrypted_voice_hash)

                if hmac.compare_digest(spoken_hash, decrypted_voice_hash):
                    logger.info(f"ACCESS GRANTED: Voice signature verified for Profile ID {profile_id}.")
                    self.ledger.append_record("VOICE_AUTH_SUCCESS", {"profile_id": profile_id})
                    return True

        except Exception as e:
            logger.error(f"Error querying civilian database during authentication: {e}")

        logger.critical("ACCESS DENIED: Voice passphrase did not match any authorized profile in the database.")
        self.ledger.append_record("VOICE_AUTH_FAILURE", {"status": "UNAUTHORIZED"})
        return False
