from __future__ import annotations

import threading
import time

_lock = threading.Lock()
_last_seen: dict[str, float] = {}


def check_rate_limit(client_ip: str, interval_seconds: int) -> tuple[bool, int]:
    if interval_seconds <= 0:
        return True, 0
    now = time.monotonic()
    with _lock:
        previous = _last_seen.get(client_ip)
        if previous is not None:
            remaining = interval_seconds - (now - previous)
            if remaining > 0:
                return False, max(1, int(remaining + 0.999))
        _last_seen[client_ip] = now
    return True, 0
