def test_healthcheck(client) -> None:
    res = client.get("/livez")

    assert res.status_code == 204
    assert res.data == b""
