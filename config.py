import os


class ConfigVarRequiredError(Exception):
    pass


def getenv(key, default=None, conv=str):
    """If `default` is None, then the var is non-optional."""
    var = os.getenv(key, default)
    if var is None:
        raise ConfigVarRequiredError(f"Configuration variable '{key}' is required but was not provided.")
    return conv(var)


AZURE_ACCOUNT_NAME = getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = getenv('AZURE_ACCOUNT_KEY')

MEDIA_CONTAINER_NAME = getenv('MEDIA_CONTAINER_NAME')
RESIZED_CONTAINER_NAME = getenv('RESIZED_CONTAINER_NAME')

CACHE_STALE_TIMEOUT = getenv('CACHE_STALE_TIMEOUT', 300, conv=int)  # seconds

STORAGE_BASE_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net"
MEDIA_CONTAINER_URL = f"{STORAGE_BASE_URL}/{MEDIA_CONTAINER_NAME}"
RESIZED_CONTAINER_URL = f"{STORAGE_BASE_URL}/{RESIZED_CONTAINER_NAME}"
