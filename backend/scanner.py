from __future__ import annotations

import time

from .cloudflare_ranges import CloudflareRangeError, get_cloudflare_networks, is_cloudflare_ip
from .config import MAX_CANDIDATES, MAX_RESULTS, MAX_SCAN_SECONDS
from .discovery import DiscoveryError, discover_subdomains
from .dns_resolver import resolve_hosts
from .formatting import dedupe_and_limit


class ScanError(Exception):
    def __init__(self, code: str, message: str, status: int):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def scan_domain(domain: str) -> dict:
    started = time.monotonic()
    deadline = started + MAX_SCAN_SECONDS
    try:
        candidates = discover_subdomains(domain, MAX_CANDIDATES)
    except DiscoveryError as exc:
        raise ScanError('DISCOVERY_UNAVAILABLE', 'Certificate Transparency discovery is unavailable.', 502) from exc
    if time.monotonic() >= deadline:
        raise ScanError('SCAN_TIMEOUT', 'The scan exceeded the allowed time.', 503)
    try:
        networks = get_cloudflare_networks()
    except CloudflareRangeError as exc:
        raise ScanError('CLOUDFLARE_UNAVAILABLE', 'Cloudflare IP ranges could not be verified.', 503) from exc
    pairs = resolve_hosts(candidates, deadline)
    if time.monotonic() >= deadline:
        raise ScanError('SCAN_TIMEOUT', 'The scan exceeded the allowed time.', 503)
    results = [
        {'hostname': hostname, 'ip': ip, 'cloudflare': True}
        for hostname, ip in pairs
        if is_cloudflare_ip(ip, networks)
    ]
    results = dedupe_and_limit(results, MAX_RESULTS)
    return {
        'success': True,
        'domain': domain,
        'results': results,
        'count': len(results),
        'duration_ms': int((time.monotonic() - started) * 1000),
        'discovery_source': 'crt.sh',
        'note': 'Certificate Transparency discovery may not find every subdomain.',
    }
