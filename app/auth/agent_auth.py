import hmac
import hashlib
import json
from app.core.config import settings


def sign_payload(sender: str, payload_dict: dict) -> str:
    """
    Signs a dictionary payload with an HMAC signature.
    """
    payload_str = json.dumps(payload_dict, sort_keys=True)
    message = f"{sender}:{payload_str}".encode("utf-8")
    signature = hmac.new(
        settings.AGENT_SECRET_KEY.encode("utf-8"), message, hashlib.sha256
    ).hexdigest()
    return signature


def verify_signature(sender: str, payload_dict: dict, signature: str) -> bool:
    """
    Verifies the HMAC signature of a payload.
    """
    expected_signature = sign_payload(sender, payload_dict)
    return hmac.compare_digest(expected_signature, signature)
