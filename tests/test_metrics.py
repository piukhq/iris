def test_metrics(client) -> None:
    res = client.get("/metrics")

    assert res.status_code == 200
