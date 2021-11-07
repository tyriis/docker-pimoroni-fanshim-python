# Docker for [fanshim-python](https://github.com/pimoroni/fanshim-python)


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

### env

| Name | Description | Default |
|:---|:------------|:--------|
| **LOG_LEVEL** | _`CRITICAL`_, _`FATAL`_, _`ERROR`_, _`WARNING`_, _`INFO`_, _`DEBUG`_, _`NOTSET`_ | `INFO` |
| **PROMETHEUS_METRIC_PORT** | The port to run prometheus metrics exporter. | `9100` |
| **OFF_THRESHOLD** | Temperature threshold in degrees C to disable fan. | `55.0` |
| **ON_THRESHOLD** | Temperature threshold in degrees C to enable fan. | `65.0` |
| **LOW_TEMP** | Temperature at which the LED is green. | `OFF_THRESHOLD` |
| **HIGH_TEMP** | Temperature at which the LED is red. | `ON_THRESHOLD` |
| **DELAY** | Delay, in seconds, between temperature readings. | `2.0` |
| **PREEMPT** | Monitor CPU frequency and activate cooling premptively. | `FALSE` |
| **VERBOSE** | Output temp and fan status messages. | `FALSE` |
| **NOBUTTON** | Disable button input. | `FALSE` |
| **NOLED** | Disable LED control. | `FALSE` |
| **BRIGHTNESS** | LED brightness, from 0 to 255. | `255` |
| **EXTENDED_COLOURS** | Extend LED colours for outside of normal low to high range. | `FALSE` |

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

### Metrics
The following metrics are exportet from

| Name | Type | Description |
|:---|:------------|:--------|
| **fanshim_processing_seconds** | _`Histogram`_ | `Time spent processing fanshim state handler.` |
| **fanshim_cpu_core_temperature** | _`Gauge`_ | `Temperature of the CPU core in °C.` |
| **fanshim_cpu_core_frequency** | _`Gauge`_ | `Frequenzy of the CPU core in MHz.` |
| **fanshim_cpu_core_max_frequency** | _`Gauge`_ | `Maximum frequenzy of the CPU core in MHz.` |
| **fanshim_fan_state** | _`Gauge`_ | `Fanshim fan state on or off.` |
| **python_gc_objects_collected_total** | _`Counter`_ | `Objects collected during GC.` |
| **python_gc_objects_uncollectable_total** | _`Counter`_ | `Uncollectable object found during GC.` |
| **python_gc_collections_total** | _`Counter`_ | `Number of times this generation was collected.` |
| **python_info** | _`Gauge`_ | `Python platform information.` |
| **process_virtual_memory_bytes** | _`Gauge`_ | `Virtual memory size in bytes.` |
| **process_resident_memory_bytes** | _`Gauge`_ | `Resident memory size in bytes.` |
| **process_start_time_seconds** | _`Gauge`_ | `Start time of the process since unix epoch in seconds.` |
| **process_cpu_seconds_total** | _`Gauge`_ | `Total user and system CPU time spent in seconds.` |
| **process_open_fds** | _`Gauge`_ | `Number of open file descriptors.` |
| **process_max_fds** | _`Gauge`_ | `Maximum number of open file descriptors.` |

