from io import BytesIO
import mimetypes
import logging
import pathlib
import os
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from typing import Optional

from flask import Flask, request, Response, jsonify, make_response
import PIL.Image

from iris.prometheus import start_metrics
from iris.metrics import status_code_counter

log = logging.getLogger("iris")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s"))
log.addHandler(handler)

app = Flask(__name__)

container_client = ContainerClient.from_connection_string(
    os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"], os.getenv("STORAGE_CONTAINER", "media")
)

# Start prometheus
start_metrics()


def download_image(resource_path: str) -> Optional[bytes]:
    # resource_path contains blob_container_name/blobpath
    container, path = resource_path.split("/", 1)
    if container_client.container_name != container:
        log.warning(
            f'Request for container "{container}" does not match '
            f'the configured container "{container_client.container_name}"'
        )
        return None

    try:
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
def prometheus_after_request(response):
    if request.endpoint not in ["readyz", "livez", "healthz"]:
        status_code_counter.labels(status=response.status_code).inc()

    return response


@app.route("/readyz")
def readyz() -> Response:
    response = Response("", status=204)

    try:
        container_client.get_blob_client("testimg").get_blob_properties()
    except ResourceNotFoundError as err:
        # Complain if container doesnt exist
        if err.error_code != "BlobNotFound":
            response = make_response(jsonify({"error": f"{err} - {err.error_code}"}), 500)

    return response


@app.route("/livez")
def livez() -> Response:
    return Response("", status=204)


@app.route("/healthz")
def healthz():
    return ""


@app.route("/content/<path:resource_path>")
def get_resource(resource_path: str):
    width = request.args.get("width")
    height = request.args.get("height")
    should_resize = width is not None and height is not None

    file_ext = pathlib.Path(resource_path).suffix
    mimetype = mimetypes.types_map.get(file_ext)
    if mimetype is None:
        log.warning(f"Can't find mimetype for extension '{file_ext}', which means we can't attempt a resize.")
        should_resize = False

    image = download_image(resource_path)

    if image is None:
        return Response("", status=404)

    if should_resize:
        pil_image = resize_image(load_pil_image(download_image(resource_path)), int(width), int(height))
        with BytesIO() as fd:
            pil_image.save(fd, format=mimetype.split("/")[1])
            image = fd.getvalue()

    return Response(image, mimetype=mimetype)


if __name__ == "__main__":
    app.run()
