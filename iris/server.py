import logging
import mimetypes
import pathlib
from io import BytesIO
from typing import Optional

import PIL.Image
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContainerClient
from flask import Flask, Response, request
from flask_cors import CORS
from pydantic import BaseSettings

from .prometheus import handle_metrics, status_code_counter

log = logging.getLogger("iris")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s"))
log.addHandler(handler)


# Quieten the azure library
logging.getLogger("azure").setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)
app.add_url_rule("/metrics", "metrics", view_func=handle_metrics)


class Settings(BaseSettings):
    storage_account_connection_string: str
    allowed_storage_containers: list = ["media", "logos"]
    storage_container: str = "media"
    storage_container_in_url: bool = True


settings = Settings()


def download_image(resource_path: str) -> Optional[bytes]:
    if settings.storage_container_in_url:
        container, path = resource_path.split("/", 1)
        if container not in settings.allowed_storage_containers:
            log.warning(f"Container: {container}, not in allowed containers: {settings.allowed_storage_containers}")
            return None
    else:
        container = None
        path = resource_path

    try:
        container_client: ContainerClient = ContainerClient.from_connection_string(
            settings.storage_account_connection_string, container if container else settings.storage_container
        )
        return container_client.download_blob(path).readall()
    except ResourceNotFoundError:
        return None


def load_pil_image(image_data: bytes) -> PIL.Image.Image:
    fd = BytesIO(image_data)
    return PIL.Image.open(fd)


def resize_image(image: PIL.Image.Image, width: int, height: int) -> PIL.Image.Image:
    log.info(f"Resizing image to {width}x{height}")
    return image.resize((width, height))


@app.after_request
def prometheus_after_request(response: Response) -> Response:
    if request.endpoint not in ("livez", "metrics"):
        status_code_counter.labels(status=response.status_code).inc()

    return response


@app.route("/livez")
def livez() -> Response:
    return Response("", status=204)


@app.route("/content/<path:resource_path>")
def get_resource(resource_path: str) -> Response:
    width = request.args.get("width")
    height = request.args.get("height")

    file_ext = pathlib.Path(resource_path).suffix
    mimetype = mimetypes.types_map.get(file_ext, "application/octet-stream")
    image = download_image(resource_path)

    if image is None:
        return Response("", status=404)

    if mimetype.startswith("image/") and width and height:
        pil_image = resize_image(load_pil_image(image), int(width), int(height))
        with BytesIO() as fd:
            pil_image.save(fd, format=mimetype.split("/")[1])
            image = fd.getvalue()
    elif not mimetype.startswith("image/"):
        logging.warning(f"Resource {resource_path}'s MIME type {mimetype} is not that of an image, no resize")

    return Response(image, mimetype=mimetype)


if __name__ == "__main__":
    app.run()
