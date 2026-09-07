from backend import scanner


def test_max_results_and_cloudflare_filter(monkeypatch):
    monkeypatch.setattr(scanner, 'get_cloudflare_networks', lambda: tuple())
    monkeypatch.setattr(scanner, 'discover_subdomains', lambda *_args: ['example.com'])
    monkeypatch.setattr(scanner, 'resolve_hosts', lambda *_args: [('example.com', '8.8.8.8')])
    result = scanner.scan_domain('example.com')
    assert result['results'] == []
    assert result['count'] == 0
