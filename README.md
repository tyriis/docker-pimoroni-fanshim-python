# Docker ARM64 for pimoroni-fanshim-python

[fanshim-python](https://github.com/pimoroni/fanshim-python) the official fanshim library.

[prometheus](https://github.com/prometheus/client_python) includes prometheus export for monitoring

The python code in this repo is based on the official library [examples](https://github.com/pimoroni/fanshim-python/blob/master/examples/automatic.py).

## build
Enable arm64 build support on amd64 systems (only required if not running).

```bash
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

Build (and push) the image for arm64.
```bash
docker buildx build \
  --push \
  --platform linux/arm64 \
  --output=type=image,push=true \
  --tag tyriis/fanshim-python:latest .
```

## start
Start a configured docker container.
```
docker run -d --privileged \
  --env OFF_THRESHOLD=55 \
  --env ON_THRESHOLD=65 \
  --env LOW_TEMP=55 \
  --env HIGH_TEMP=65 \
  --env DELAY=2 \
  --env PREEMPT=FALSE \
  --env VERBOSE=FALSE \
  --env NOBUTTON=FALSE \
  --env NOLED=FALSE \
  --env BRIGHTNESS=255 \
  --env EXTENDED_COLOURS=TRUE \
  --env LOG_LEVEL=INFO \
  --env PROMETHEUS_METRIC_PORT=9100 \
  --name fanshim-python \
  tyriis/fanshim-python
```

## prometheus exporter
Currently prometheus metrics exporter runs on port `9100` if not changed.
