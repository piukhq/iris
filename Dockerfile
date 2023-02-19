FROM ghcr.io/binkhq/python:3.11-poetry as build

WORKDIR /src
ADD . .
RUN poetry build

FROM ghcr.io/binkhq/python:3.11
WORKDIR /app
COPY --from=build /src/dist/*.whl .

RUN export wheel=$(find -type f -name "*.whl") && \
    pip install "$wheel" && \
    rm -rf "$wheel"
ENV PROMETHEUS_MULTIPROC_DIR=/dev/shm
ENTRYPOINT ["linkerd-await", "--"]
CMD [ "gunicorn", "--error-logfile=-", "--access-logfile=-", \
                  "--bind=0.0.0.0:9000", "--bind=0.0.0.0:9100", \
                  "--logger-class=iris.GunicornLogger", "iris:app" ]
