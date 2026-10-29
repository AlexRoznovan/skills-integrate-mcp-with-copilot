import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path


PASSWORD_ITERATIONS = 600_000
SESSION_DURATION_SECONDS = 8 * 60 * 60
TEACHERS_FILE = Path(__file__).with_name("teachers.json")


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return salt.hex(), password_hash.hex()


def load_teachers(path: Path = TEACHERS_FILE) -> list[dict[str, str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []

    teachers = data.get("teachers") if isinstance(data, dict) else None
    if not isinstance(teachers, list):
        raise ValueError("Teacher file must contain a 'teachers' list")
    return teachers


def authenticate_teacher(
    username: str, password: str, path: Path = TEACHERS_FILE
) -> bool:
    for teacher in load_teachers(path):
        if teacher.get("username") != username:
            continue
        try:
            salt = bytes.fromhex(teacher["salt"])
            expected_hash = teacher["password_hash"]
        except (KeyError, TypeError, ValueError):
            return False
        _, actual_hash = hash_password(password, salt)
        return hmac.compare_digest(actual_hash, expected_hash)
    return False


def add_teacher(username: str, password: str, path: Path = TEACHERS_FILE) -> None:
    username = username.strip()
    if not username or ":" in username:
        raise ValueError("Username must be non-empty and cannot contain ':'")
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")

    teachers = load_teachers(path)
    if any(teacher.get("username") == username for teacher in teachers):
        raise ValueError("That teacher username already exists")

    salt, password_hash = hash_password(password)
    teachers.append(
        {"username": username, "salt": salt, "password_hash": password_hash}
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"teachers": teachers}, indent=2) + "\n", encoding="utf-8"
    )
    path.chmod(0o600)


def create_session(username: str, secret: str, now: int | None = None) -> str:
    current_time = int(time.time()) if now is None else now
    expires_at = current_time + SESSION_DURATION_SECONDS
    payload = f"{username}:{expires_at}"
    signature = hmac.new(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def verify_session(
    token: str | None, secret: str, now: int | None = None
) -> str | None:
    if not token:
        return None
    try:
        username, expires_at_text, signature = token.rsplit(":", 2)
        expires_at = int(expires_at_text)
    except (ValueError, TypeError):
        return None

    payload = f"{username}:{expires_at}"
    expected_signature = hmac.new(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    current_time = int(time.time()) if now is None else now
    if expires_at <= current_time or not hmac.compare_digest(
        signature, expected_signature
    ):
        return None
    return username