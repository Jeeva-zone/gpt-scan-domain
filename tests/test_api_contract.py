from fastapi.testclient import TestClient

import api.index as api

client = TestClient(api.app)


def test_health():
    assert client.get('/api/health').json() == {'status': 'ok'}


def test_invalid_input_response(monkeypatch):
    monkeypatch.setattr(api, 'check_rate_limit', lambda *_args: (True, 0))
    response = client.post('/api/scan', json={'domain': 'localhost'})
    assert response.status_code == 400
    assert response.json()['error']['code'] == 'INVALID_DOMAIN'


def test_rate_limit_response(monkeypatch):
    monkeypatch.setattr(api, 'check_rate_limit', lambda *_args: (False, 42))
    response = client.post('/api/scan', json={'domain': 'example.com'})
    assert response.status_code == 429
    assert response.headers['Retry-After'] == '42'
    assert response.json()['error']['code'] == 'RATE_LIMITED'


def test_success_schema_and_no_gray_results(monkeypatch):
    monkeypatch.setattr(api, 'check_rate_limit', lambda *_args: (True, 0))
    monkeypatch.setattr(api, 'scan_domain', lambda _domain: {
        'success': True,
        'domain': 'example.com',
        'results': [{'hostname': 'www.example.com', 'ip': '104.17.1.1', 'cloudflare': True}],
        'count': 1,
        'duration_ms': 12,
        'discovery_source': 'crt.sh',
        'note': 'Certificate Transparency discovery may not find every subdomain.',
    })
    data = client.post('/api/scan', json={'domain': 'example.com'}).json()
    assert data['success'] is True
    assert data['count'] == 1
    assert all(row.get('cloudflare') is True for row in data['results'])


def test_unexpected_internal_error_is_sanitized(monkeypatch):
    monkeypatch.setattr(api, 'check_rate_limit', lambda *_args: (True, 0))
    monkeypatch.setattr(api, 'scan_domain', lambda _domain: (_ for _ in ()).throw(RuntimeError('SECRET STACK TRACE')))
    response = client.post('/api/scan', json={'domain': 'example.com'})
    assert response.status_code == 500
    assert 'SECRET' not in response.text
    assert response.json()['error']['code'] == 'INTERNAL_ERROR'
