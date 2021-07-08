# Iris

Content delivery API with dynamic image resizing.

Serves images from an Azure Blob Storage account, the storage account "container" is specified by an environment variable to prevent
serving files from other containers within the same storage account.

Currently Iris will happily serve any file within a Blob Storage container, regardless if it is an image or not. There exists a scenario where if
the file extension is that of an image, and the file in blob storage is not an image and Iris is instructed to resize the image, it will cause an exception.
This is accepted as it requires employees to upload non-image files to Blob Storage with an image filename. 

`STORAGE_ACCOUNT_CONNECTION_STRING` Should be the connection string from the storage account access keys section.

`STORAGE_CONTAINER` Should be the storage account container name, defaults to `media`

`LINKERD_AWAIT_DISABLED` This controls the Docker entrypoint which will wait till the LinkerD proxy is ready. Setting this will stop that functionality.


## Installation

To set up the virtual environment
```shell
pipenv sync --dev
```

To update dependencies
```shell
pipenv update --dev
```


## Test Server

Export valid Azure storage credentials, then either run the server via python or via docker.
```shell
export STORAGE_ACCOUNT_CONNECTION_STRING=BLAH
export STORAGE_CONTAINER=BLAH

pipenv run python -m iris.server
# OR
docker build -t iris .
docker run --rm -it -p 9000:9000 -p 9100:9100 --name iris -e LINKERD_AWAIT_DISABLED=1 -e STORAGE_ACCOUNT_CONNECTION_STRING=$STORAGE_ACCOUNT_CONNECTION_STRING -e STORAGE_CONTAINER=$STORAGE_CONTAINER iris
```

Example requests:
```shell
http get localhost:5000/path/to/image.jpg?width=300&height=200
# or
curl -v http://localhost:5000/path/to/image.jpg?width=300&height=200
# or for production (assuming the image still exists)
curl -v https://api.gb.bink.com/content/media/hermes/bink.jpg
```


### Pycharm Configuration

Add a new `Python` configuration, change `Script path` dropdown to `Module name` then set the module name to `iris.server`. Then update the environment variables to valid ones that are required. 


### VSCode Configuration

Not a clue, PyCharm FTW


## Tests

Run pytest via
```shell
pipenv run pytest
```
