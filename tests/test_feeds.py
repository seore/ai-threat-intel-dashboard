from threat_intel import feeds


def test_feodo_fetch_callable():
    assert hasattr(feeds, "fetch_feodo_blocklist")
