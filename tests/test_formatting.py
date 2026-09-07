from backend.formatting import dedupe_and_limit, results_to_csv


def test_duplicate_removal_and_true_only():
    rows = dedupe_and_limit([
        {'hostname': 'b.example.com', 'ip': '1.1.1.1', 'cloudflare': True},
        {'hostname': 'b.example.com', 'ip': '1.1.1.1', 'cloudflare': False},
        {'hostname': 'a.example.com', 'ip': '2.2.2.2', 'cloudflare': True},
    ], 500)
    assert rows == [
        {'hostname': 'a.example.com', 'ip': '2.2.2.2', 'cloudflare': True},
        {'hostname': 'b.example.com', 'ip': '1.1.1.1', 'cloudflare': True},
    ]


def test_csv_escaping():
    csv = results_to_csv([{'hostname': 'a,example.com', 'ip': '1.1.1.1', 'cloudflare': True}])
    assert '"a,example.com",1.1.1.1,true' in csv.lower()
