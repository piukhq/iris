import os
from unittest.mock import MagicMock

import flask
import pytest

os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"] = (
    "DefaultEndpointsProtocol=https;AccountName=binkuksouthdev;AccountKey=LALALAZswZAJbFhKjIGr0feakhY8QsCw4o"
    "Uuj6bXNfxhWQv2caNkDo8czIu05DBcaZbSL7vfpYGP7OZsbpXuhw==;EndpointSuffix=core.windows.net"
)

RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resources")


@pytest.fixture(scope="session")
def app() -> flask.Flask:
    from iris import app as app_

    return app_


@pytest.fixture(scope="session")
def image_resource() -> bytes:
    with open(os.path.join(RESOURCE_DIR, "boots.png"), "rb") as fp:
        return fp.read()


@pytest.fixture()
def patched_download_image(monkeypatch) -> MagicMock:
    import iris.server

    download_image_mock = MagicMock()
    monkeypatch.setattr(iris.server, "download_image", download_image_mock)

    return download_image_mock
