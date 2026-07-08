import json
from module2_55 import main as m


def test_sanitize_html():
    raw = '<div><script>alert(1)</script><p>Good</p></div>'
    cleaned = m.sanitize_html(raw)
    assert '<script' not in cleaned
    assert 'Good' in cleaned


def test_timezone_normalization():
    t1 = '20260708T130000Z'
    assert m.normalize_timezone(t1).endswith('+00:00')
    t2 = '2026-07-08T13:00:00+01:00'
    assert m.normalize_timezone(t2) == t2
