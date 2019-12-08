import os


class ConfigVarRequiredError(Exception):
    pass


def getenv(key, default=None, conv=str):
    """If `default` is None, then the var is non-optional."""
    var = os.getenv(key, default)
    if var is None:
        raise ConfigVarRequiredError(f"Configuration variable '{key}' is required but was not provided.")
    return conv(var)


STORAGE_BASE_URL = getenv('STORAGE_BASE_URL', 'https://bink.blob.core.windows.net')
