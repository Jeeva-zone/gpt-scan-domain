from __future__ import annotations

import re
from urllib.parse import urlparse

LABEL_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$')


def normalize_domain(value: str) -> str:
    value = (value or '').strip().lower()
    if '://' in value:
        parsed = urlparse(value)
        value = parsed.hostname or ''
    return value.rstrip('.').strip()


def is_valid_domain(domain: str) -> bool:
    if not domain or len(domain) > 253 or '.' not in domain or '://' in domain or '/' in domain or ':' in domain:
        return False
    labels = domain.split('.')
    return len(labels) >= 2 and all(LABEL_RE.fullmatch(label) for label in labels) and not any(label.isdigit() for label in labels[-1:])


def hostname_belongs_to_domain(hostname: str, domain: str) -> bool:
    return hostname == domain or hostname.endswith('.' + domain)
