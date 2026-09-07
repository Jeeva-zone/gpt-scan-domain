from __future__ import annotations

import ipaddress
import threading
import time
import urllib.error
import urllib.request

from .config import CF_CACHE_SECONDS, REQUEST_TIMEOUT

V4_URL = 'https://www.cloudflare.com/ips-v4'
V6_URL = 'https://www.cloudflare.com/ips-v6'
USER_AGENT = 'OrangeTest/1.0 (+passive-security-research)'
_lock = threading.Lock()
_cached: tuple[float, tuple[ipaddress._BaseNetwork, ...]] | None = None

class CloudflareRangeError(RuntimeError):
    """Raised when official Cloudflare ranges cannot be verified."""


def _fetch(url: str) -> tuple[str, ...]:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/plain'})
    try:
        with urllib.request.urlopen(req, timeout=min(REQUEST_TIMEOUT, 12)) as response:
            if response.status >= 400:
                raise CloudflareRangeError('Cloudflare IP ranges unavailable')
            body = response.read().decode('utf-8')
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, UnicodeDecodeError) as exc:
        raise CloudflareRangeError('Cloudflare IP ranges unavailable') from exc
    values = tuple(line.strip() for line in body.splitlines() if line.strip())
    if not values:
        raise CloudflareRangeError('Cloudflare IP ranges unavailable')
    return values


def get_cloudflare_networks(force_refresh: bool = False) -> tuple[ipaddress._BaseNetwork, ...]:
    global _cached
    now = time.monotonic()
    with _lock:
        if not force_refresh and _cached and now - _cached[0] < CF_CACHE_SECONDS:
            return _cached[1]
    values = _fetch(V4_URL) + _fetch(V6_URL)
    try:
        networks = tuple(ipaddress.ip_network(value, strict=False) for value in values)
    except ValueError as exc:
        raise CloudflareRangeError('Cloudflare IP ranges returned malformed CIDR data') from exc
    with _lock:
        _cached = (time.monotonic(), networks)
    return networks


def is_cloudflare_ip(ip: str, networks: tuple[ipaddress._BaseNetwork, ...] | None = None) -> bool:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    nets = networks if networks is not None else get_cloudflare_networks()
    return any(address.version == network.version and address in network for network in nets)
