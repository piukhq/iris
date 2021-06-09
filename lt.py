import logging
import random
import time

import requests

logging.basicConfig(level=logging.WARNING, format="%(asctime)s :: %(levelname)s :: %(message)s")
log = logging.getLogger(__name__)


class CircleBuf:
    def __init__(self, size, initial=0):
        self.data = [initial] * size
        self.size = size
        self._index = 0
        log.debug(f"Initialised new circular buffer of size {self.size}")

    def append(self, val):
        log.debug(f"Appending {val} to circular buffer")
        self.data[self._index] = val
        log.debug(f"Index before: {self._index}")
        self._index = (self._index + 1) % self.size
        log.debug(f"Index after: {self._index}")


sizes = tuple(
    {"width": w, "height": h}
    for w, h in (
        (320, 240),
        (400, 300),
        (640, 480),
        (800, 600),
        (1280, 800),
    )
)

images = (
    "iris/ranger-black.png",
    "iris/ranger-blue.png",
    "iris/ranger-pink.png",
    "iris/ranger-red.png",
    "iris/ranger-yellow.png",
)


if __name__ == "__main__":
    perf = CircleBuf(10)
    try:
        while True:
            start = time.time()
            image = random.choice(images)
            size = random.choice(sizes)
            resp = requests.get(f"http://content.bink.com/{image}", params=size, allow_redirects=False)
            resp.raise_for_status()
            perf.append(time.time() - start)
            print(f"Average request time: {1000 * sum(perf.data) / perf.size} ms", end="       \r")
    except KeyboardInterrupt:
        pass
