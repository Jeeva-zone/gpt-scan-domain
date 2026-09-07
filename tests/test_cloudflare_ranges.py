from backend.cloudflare_ranges import is_cloudflare_ip
import ipaddress


def nets(*cidrs):
    return tuple(ipaddress.ip_network(c) for c in cidrs)


def test_cloudflare_ipv4_match():
    assert is_cloudflare_ip('104.17.147.22', nets('104.16.0.0/13'))


def test_cloudflare_ipv6_match():
    assert is_cloudflare_ip('2606:4700::1', nets('2606:4700::/32'))


def test_non_cloudflare_ip_rejected():
    assert not is_cloudflare_ip('8.8.8.8', nets('104.16.0.0/13'))
