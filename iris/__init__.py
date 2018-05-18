from io import BytesIO
import mimetypes
import logging
import pathlib
import time

from flask import Flask, request, redirect
from azure.storage.blob import BlockBlobService
from azure.storage.blob.models import ContentSettings
import requests
import PIL.Image

import config


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)


_cache = {}


def make_resized_image_path(original_path, width, height):
    head, tail = original_path.rsplit('.', 1)
    return f"{head}.{width}x{height}.{tail}"


def blob_to_image(resource_path):
    blob_contents = requests.get(f"{config.MEDIA_CONTAINER_URL}/{resource_path}").content
    fd = BytesIO(blob_contents)
    return PIL.Image.open(fd)


bbs = BlockBlobService(config.AZURE_ACCOUNT_NAME, config.AZURE_ACCOUNT_KEY)


def resize_blob(resource_path, width, height, mimetype):
    image = blob_to_image(resource_path)
    resized = image.resize((width, height))

    resized_bytes = BytesIO()
    resized.save(resized_bytes, format=mimetype.rsplit('/', 1)[1])
    resized_bytes.seek(0)

    resized_path = make_resized_image_path(resource_path, width, height)

    bbs.create_blob_from_stream(
        config.RESIZED_CONTAINER_NAME,
        resized_path,
        resized_bytes,
        content_settings=ContentSettings(content_type=mimetype))

    resized_blob_url = f"{config.RESIZED_CONTAINER_URL}/{resized_path}"
    _cache[resized_blob_url] = {
        'res': True,
        'exp': time.time() + config.CACHE_STALE_TIMEOUT,
    }

    return redirect(resized_blob_url)


def resource_exists(url):
    log.info(f"Checking for resource existence at ...{url[-24:]}")
    try:
        entry = _cache[url]
    except KeyError:
        pass  # cache miss
    else:
        if entry['exp'] >= time.time():
            return entry['res']
    result = requests.head(url)
    _cache[url] = {
        'res': result.ok,
        'exp': time.time() + config.CACHE_STALE_TIMEOUT
    }
    log.debug('Cached new result.')
    return result.ok


def fast_redirect(resource_path):
    log.info('Performing performing fast redirect to original resource.')
    return redirect(f"{config.MEDIA_CONTAINER_URL}/{resource_path}")


@app.route('/healthz')
def healthz():
    return ''


@app.route('/<path:resource_path>')
def get_resource(resource_path):
    width = request.args.get('width')
    height = request.args.get('height')
    resize_requested = width is not None and height is not None

    if not resize_requested:
        return fast_redirect(resource_path)

    file_ext = pathlib.Path(resource_path).suffix
    mimetype = mimetypes.types_map.get(file_ext)
    if mimetype is None:
        log.warning(f"Can't find mimetype for extension '{file_ext}', which means we can't attempt a resize.")
        return fast_redirect(resource_path)

    resized_blob_path = make_resized_image_path(resource_path, width, height)
    blob_url = f"{config.RESIZED_CONTAINER_URL}/{resized_blob_path}"

    if resource_exists(blob_url):
        log.info('Resized blob already exists, performing fast redirect to resized resource.')
        return redirect(blob_url)

    width, height = int(width), int(height)
    log.info(f"Resizing image to {width}x{height}")
    return resize_blob(resource_path, width, height, mimetype)
