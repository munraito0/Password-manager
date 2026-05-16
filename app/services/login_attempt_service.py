import time
from app.logger import logger

_attempts: dict[str, dict] = {}

_MAX_ATTEMPTS = 5
_BLOCK_SECONDS = 300  # 5 минут


def is_blocked(email: str) -> bool:
    entry = _attempts.get(email)
    if not entry:
        return False
    blocked_until = entry.get("blocked_until")
    if blocked_until and time.monotonic() < blocked_until:
        return True
    if blocked_until:
        _attempts.pop(email, None)
    return False


def get_retry_after(email: str) -> int:
    entry = _attempts.get(email)
    if not entry:
        return 0
    blocked_until = entry.get("blocked_until", 0)
    remaining = blocked_until - time.monotonic()
    return max(0, int(remaining))


def record_failed(email: str) -> None:
    entry = _attempts.setdefault(email, {"count": 0, "blocked_until": None})
    entry["count"] += 1
    if entry["count"] >= _MAX_ATTEMPTS:
        entry["blocked_until"] = time.monotonic() + _BLOCK_SECONDS
        logger.warning(
            f"Multiple failed login attempts for user: {email}",
            extra={"operation": "login_blocked", "entity": "user"},
        )


def reset(email: str) -> None:
    _attempts.pop(email, None)
