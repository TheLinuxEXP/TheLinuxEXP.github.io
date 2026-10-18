"""Single-user login for the local admin: password hash, session key, lockout."""

import json
import os
import secrets
import time
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

MIN_PASSWORD_LENGTH = 10
# Compared against when the user name is wrong, so timing does not reveal it.
_DUMMY_HASH = generate_password_hash("not-the-password")


def _write_private(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.chmod(path, 0o600)


class Credentials:
    def __init__(self, data_dir: Path):
        self.path = Path(data_dir) / "credentials.json"

    def exists(self) -> bool:
        return self.path.is_file()

    def set(self, username: str, password: str) -> None:
        username = username.strip()
        if not username or len(username) > 64:
            raise ValueError("The user name is required (64 characters at most).")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"The password must be at least {MIN_PASSWORD_LENGTH} characters long.")
        _write_private(self.path, json.dumps({"username": username, "password_hash": generate_password_hash(password)}))

    def verify(self, username: str, password: str) -> bool:
        stored = json.loads(self.path.read_text(encoding="utf-8")) if self.exists() else {}
        hash_to_check = stored.get("password_hash", _DUMMY_HASH)
        password_ok = check_password_hash(hash_to_check, password)
        user_ok = secrets.compare_digest(username.encode(), stored.get("username", "").encode())
        return bool(stored) and password_ok and user_ok


def load_secret_key(data_dir: Path) -> str:
    path = Path(data_dir) / "secret.key"
    if not path.is_file():
        _write_private(path, secrets.token_hex(32))
    return path.read_text(encoding="utf-8").strip()


class LoginThrottle:
    """After 5 wrong attempts in a row, logins are refused for a minute."""

    def __init__(self, max_failures: int = 5, lock_seconds: int = 60, clock=time.monotonic):
        self.max_failures, self.lock_seconds, self.clock = max_failures, lock_seconds, clock
        self.failures, self.locked_until = 0, 0.0

    def seconds_left(self) -> int:
        return max(0, int(self.locked_until - self.clock()) + 1) if self.locked_until > self.clock() else 0

    def failed(self) -> None:
        self.failures += 1
        if self.failures >= self.max_failures:
            self.locked_until = self.clock() + self.lock_seconds
            self.failures = 0

    def succeeded(self) -> None:
        self.failures, self.locked_until = 0, 0.0
