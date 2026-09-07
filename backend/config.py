from __future__ import annotations

import os


def int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(minimum, min(maximum, value))

MAX_CANDIDATES = int_env('MAX_CANDIDATES', 1000, 1, 5000)
DNS_CONCURRENCY = int_env('DNS_CONCURRENCY', 25, 1, 100)
REQUEST_TIMEOUT = int_env('REQUEST_TIMEOUT', 30, 3, 60)
MAX_RESULTS = int_env('MAX_RESULTS', 500, 1, 2000)
RATE_LIMIT_SECONDS = int_env('RATE_LIMIT_SECONDS', 60, 0, 3600)
MAX_SCAN_SECONDS = int_env('MAX_SCAN_SECONDS', 90, 10, 90)
CF_CACHE_SECONDS = int_env('CF_CACHE_SECONDS', 3600, 60, 86400)
ALLOWED_ORIGINS = tuple(o.strip() for o in os.getenv('ALLOWED_ORIGINS', '').split(',') if o.strip())
