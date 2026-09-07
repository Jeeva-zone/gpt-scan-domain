from backend.validation import hostname_belongs_to_domain, is_valid_domain, normalize_domain


def test_valid_domain_normalization():
    assert normalize_domain('  HTTPS://SpeedTest.NET/  ') == 'speedtest.net'
    assert is_valid_domain('speedtest.net')


def test_invalid_domain_rejection():
    for value in ('localhost', 'example', 'http://bad domain.com', 'a..com', '-bad.com', 'bad-.com', 'bad.com:443'):
        assert not is_valid_domain(value)


def test_domain_suffix_filtering():
    assert hostname_belongs_to_domain('app.example.com', 'example.com')
    assert hostname_belongs_to_domain('example.com', 'example.com')
    assert not hostname_belongs_to_domain('example.com.evil.test', 'example.com')
    assert not hostname_belongs_to_domain('notexample.com', 'example.com')


def test_wildcard_style_names_are_trimmed_by_discovery_logic():
    assert normalize_domain('WWW.Example.com.') == 'www.example.com'
