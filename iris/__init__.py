from io import BytesIO
import mimetypes
import logging
import pathlib

from flask import Flask, request, Response
import requests
import PIL.Image

import config

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)


def download_image(resource_path):
    return requests.get(
        f"{config.STORAGE_BASE_URL}/{resource_path}").content


def load_pil_image(image_data):
    fd = BytesIO(image_data)
    return PIL.Image.open(fd)


def resize_image(image, width, height):
    log.info(f"Resizing image to {width}x{height}")
    return image.resize((width, height))


def resource_exists(url):
    log.info(f"Checking for resource existence at ...{url[-24:]}")
    result = requests.head(url)
    return result.ok


@app.route('/healthz')
def healthz():
    return ''


@app.route('/<path:resource_path>')
def get_resource(resource_path):
    width = request.args.get('width')
    height = request.args.get('height')
    should_resize = width is not None and height is not None

    file_ext = pathlib.Path(resource_path).suffix
    mimetype = mimetypes.types_map.get(file_ext)
    if mimetype is None:
        log.warning(
            f"Can't find mimetype for extension '{file_ext}', which means we can't attempt a resize."
        )
        should_resize = False

    if should_resize:
        pil_image = resize_image(load_pil_image(download_image(resource_path)), int(width), int(height))
        with BytesIO() as fd:
            pil_image.save(fd, format=mimetype.split('/')[1])
            image = fd.getvalue()
    else:
        image = download_image(resource_path)

    return Response(image, mimetype=mimetype)
