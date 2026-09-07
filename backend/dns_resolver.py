from __future__ import annotations

import ipaddress
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.exception
import dns.resolver

from .config import DNS_CONCURRENCY, REQUEST_TIMEOUT


def _resolve_one(hostname: str) -> tuple[str, list[str]]:
    resolver = dns.resolver.Resolver(configure=True)
    resolver.timeout = min(float(REQUEST_TIMEOUT), 1.5)
    resolver.lifetime = min(float(REQUEST_TIMEOUT), 1.5)
    ips: set[str] = set()
    for record_type in ('A', 'AAAA'):
        try:
            answers = resolver.resolve(hostname, record_type, raise_on_no_answer=False)
            for answer in answers:
                try:
                    ips.add(str(ipaddress.ip_address(answer.to_text())))
                except ValueError:
                    continue
        except (dns.exception.DNSException, OSError):
            continue
    return hostname, sorted(ips, key=lambda value: (ipaddress.ip_address(value).version, value))


def resolve_hosts(hostnames: list[str], deadline: float) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=DNS_CONCURRENCY, thread_name_prefix='orange-dns') as pool:
        futures = {pool.submit(_resolve_one, host): host for host in hostnames}
        for future in as_completed(futures):
            try:
                hostname, ips = future.result()
            except Exception:
                continue
            for ip in ips:
                pairs.append((hostname, ip))
            if deadline and time.monotonic() >= deadline:
                break
    return pairs
