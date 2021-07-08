from unittest.mock import MagicMock

import pytest


def test_get_image(client, patched_download_image: MagicMock, image_resource: bytes) -> None:
    patched_download_image.return_value = image_resource

    res = client.get("/content/media/test.png")

    assert res.status_code == 200
    assert res.data == image_resource
    assert res.headers["Content-Type"] == "image/png"


def test_get_non_existant_image(client, patched_download_image: MagicMock) -> None:
    patched_download_image.return_value = None

    res = client.get("/content/media/test.png")

    assert res.status_code == 404


def test_get_image_resize(client, patched_download_image: MagicMock, image_resource: bytes) -> None:
    patched_download_image.return_value = image_resource

    res = client.get("/content/media/test.png?width=50&height=50")

    assert res.status_code == 200
    assert len(res.data) < len(image_resource)
    assert res.headers["Content-Type"] == "image/png"


@pytest.mark.parametrize("url", ["/content/media/test.png?height=50", "/content/media/test.png?width=50"])
def test_get_image_resize_missing_arg(
    client, patched_download_image: MagicMock, image_resource: bytes, url: str
) -> None:
    patched_download_image.return_value = image_resource

    res = client.get(url)

    # If width or height are missing then it should the original image
    assert res.status_code == 200
    assert res.data == image_resource
    assert res.headers["Content-Type"] == "image/png"


def test_get_image_resize_bad_mime_type(client, patched_download_image: MagicMock, image_resource: bytes) -> None:
    patched_download_image.return_value = image_resource

    res = client.get("/content/media/test.pdf?width=50&height=50")

    # If mime type does not start with image/ then no resize
    assert res.status_code == 200
    assert res.data == image_resource
    assert res.headers["Content-Type"] == "application/pdf"
