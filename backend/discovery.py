from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from .config import REQUEST_TIMEOUT
from .validation import hostname_belongs_to_domain

CRT_BASE = 'https://crt.sh/'
USER_AGENT = 'OrangeTest/1.0 (+passive-security-research)'

class DiscoveryError(RuntimeError):
    """Raised when Certificate Transparency discovery is unavailable."""


def _fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=min(REQUEST_TIMEOUT, 12)) as response:
            if response.status >= 400:
                raise DiscoveryError(f'crt.sh returned HTTP {response.status}')
            raw = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        raise DiscoveryError('crt.sh request failed') from exc
    if not raw.strip():
        return []
    try:
        return json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DiscoveryError('crt.sh returned invalid JSON') from exc


def discover_subdomains(domain: str, max_candidates: int) -> list[str]:
    encoded = urllib.parse.quote(f'%.{domain}', safe='')
    payload = _fetch_json(f'{CRT_BASE}?q={encoded}&output=json')
    if payload is None:
        payload = []
    if not isinstance(payload, list):
        raise DiscoveryError('crt.sh returned an unexpected response')

    found: set[str] = {domain}
    for record in payload:
        if not isinstance(record, dict):
            continue
        names = record.get('name_value')
        if not isinstance(names, str):
            continue
        for name in names.splitlines():
            cleaned = name.strip().lower().lstrip('*.').rstrip('.')
            if cleaned and hostname_belongs_to_domain(cleaned, domain):
                found.add(cleaned)
                if len(found) >= max_candidates:
                    return sorted(found)[:max_candidates]
    return sorted(found)[:max_candidates]
