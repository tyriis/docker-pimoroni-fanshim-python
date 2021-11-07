#!/usr/bin/env python3
import colorsys
import psutil
import time
import signal
import sys
import os
import logging
import time
from threading import Lock
from fanshim import FanShim
from prometheus_client import start_http_server, Summary, Gauge, Histogram
from pythonjsonlogger import jsonlogger

LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))

def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    supported_keys = [
      'asctime',
      'created',
      'filename',
      'funcName',
      'levelname',
      'levelno',
      'lineno',
      'module',
      'msecs',
      'message',
      'name',
      'pathname',
      'process',
      'processName',
      'relativeCreated',
      'thread',
      'threadName'
    ]
    log_format = lambda x: ['%({0:s})s'.format(i) for i in x]
    custom_format = ' '.join(log_format(supported_keys))
    formatter = jsonlogger.JsonFormatter(custom_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    return logger

logger = get_module_logger(__name__)
logger.info("fanshim startup")

def parse_float(env, default):
    try:
        result = float(os.getenv(env))
        logger.debug(f'{env} value parsed: {result}')
        return result
    except:
        logger.warning(f'{env} value not parsed return: {default}!')
        return default

def parse_bool(env, default):
    def return_default():
        logger.warning(f'{env} value not parsed return: {default}!')
        return default
    try:
        if os.getenv(env).lower() in ['true', '1']:
            logger.debug(f'{env} value parsed: {True}')
            return True
        elif os.getenv(env).lower() in ['false', '0']:
            logger.debug(f'{env} value parsed: {True}')
            return False
        return return_default()
    except:
        return return_default()

OFF_THRESHOLD = parse_float('OFF_THRESHOLD', 55.0)
ON_THRESHOLD = parse_float('ON_THRESHOLD', 65.0)
LOW_TEMP = parse_float('LOW_TEMP', None)
HIGH_TEMP = parse_float('HIGH_TEMP', None)
DELAY = parse_float('DELAY', 2.0)
PREEMPT = parse_bool('PREEMPT', False)
VERBOSE = parse_bool('VERBOSE', False)
NOBUTTON = parse_bool('NOBUTTON', False)
NOLED = parse_bool('NOLED', False)
BRIGHTNESS = parse_float('BRIGHTNESS', 255.0)
EXTENDED_COLOURS = parse_bool('EXTENDED_COLOURS', False)
PROMETHEUS_METRIC_PORT = int(os.getenv('PROMETHEUS_METRIC_PORT', '9100'))

# Create the metrics
PROCESSING_TIME = Histogram('fanshim_processing_seconds', 'Time spent processing fanshim state handler')
LOOP_EXECUTION_LATENCY = Summary('fanshim_processing_latency_seconds', 'Description of summary')
CORE_TEMPERATURE = Gauge('fanshim_cpu_core_temperature', 'Temperature of the CPU core in °C')
CORE_TEMPERATURE.set_function(lambda: get_cpu_temp())
CORE_FREQUENCY = Gauge('fanshim_cpu_core_frequency', 'Frequenzy of the CPU core in MHz')
CORE_FREQUENCY.set_function(lambda: get_cpu_freq().current)
CORE_MAX_FREQUENCY = Gauge('fanshim_cpu_core_max_frequency', 'Maximum frequenzy of the CPU core in MHz')
CORE_MAX_FREQUENCY.set_function(lambda: get_cpu_freq().max)
FAN_STATE = Gauge('fanshim_fan_state', 'Fanshim fan state on or off')
FAN_STATE.set(0)

def clean_exit(signum, frame):
    set_fan(False)
    if not NOLED:
        fanshim.set_light(0, 0, 0)
    sys.exit(0)

def update_led_temperature(temp):
    led_busy.acquire()
    temp = float(temp)
    if temp < LOW_TEMP and EXTENDED_COLOURS:
        # Between minimum temp and low temp, set LED to blue through to green
        temp -= min_temp
        temp /= float(LOW_TEMP - min_temp)
        temp  = max(0, temp)
        hue   = (120.0 / 360.0) + ((1.0 - temp) * 120.0 / 360.0)
    elif temp > HIGH_TEMP and EXTENDED_COLOURS:
        # Between high temp and maximum temp, set LED to red through to magenta
        temp -= HIGH_TEMP
        temp /= float(max_temp - HIGH_TEMP)
        temp  = min(1, temp)
        hue   = 1.0 - (temp * 60.0 / 360.0)
    else:
        # In the normal low temp to high temp range, set LED to green through to red
        temp -= LOW_TEMP
        temp /= float(HIGH_TEMP - LOW_TEMP)
        temp = max(0, min(1, temp))
        hue   = (1.0 - temp) * 120.0 / 360.0

    r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(hue, 1.0, BRIGHTNESS / 255.0)]
    fanshim.set_light(r, g, b)
    led_busy.release()

def get_cpu_temp():
    t = psutil.sensors_temperatures()
    for x in ['cpu-thermal', 'cpu_thermal']:
        if x in t:
            return t[x][0].current
    logger.warning("Warning: Unable to get CPU temperature!")
    return 0

def get_cpu_freq():
    freq = psutil.cpu_freq()
    return freq

def set_fan(status):
    global enabled
    changed = False
    if status != enabled:
        changed = True
        fanshim.set_fan(status)
        FAN_STATE.set(int(status))
    enabled = status
    return changed

def set_automatic(status):
    global armed, last_change
    armed = status
    last_change = 0

fanshim = FanShim(disable_button=NOBUTTON, disable_led=NOLED)
fanshim.set_hold_time(1.0)
fanshim.set_fan(False)
armed = True
enabled = False
led_busy = Lock()
enable = False
is_fast = False
last_change = 0
min_temp = 30
max_temp = 85
signal.signal(signal.SIGTERM, clean_exit)

if NOLED:
    led_busy.acquire()
    fanshim.set_light(0, 0, 0)
    led_busy.release()

if LOW_TEMP is None:
    LOW_TEMP = OFF_THRESHOLD

if HIGH_TEMP is None:
    HIGH_TEMP = ON_THRESHOLD

if not NOBUTTON:
    @fanshim.on_release()
    def release_handler(was_held):
        global armed
        if was_held:
            set_automatic(not armed)
        elif not armed:
            set_fan(not enabled)
    @fanshim.on_hold()
    def held_handler():
        global led_busy
        if NOLED:
            return
        led_busy.acquire()
        for _ in range(3):
            fanshim.set_light(0, 0, 255)
            time.sleep(0.04)
            fanshim.set_light(0, 0, 0)
            time.sleep(0.04)
        led_busy.release()

# Decorate function with metric.
@PROCESSING_TIME.time()
@LOOP_EXECUTION_LATENCY.time()
def handle_fanshim():
    global is_fast
    global enable
    global last_change
    t = get_cpu_temp()
    f = get_cpu_freq()
    was_fast = is_fast
    is_fast = (int(f.current) == int(f.max))
    if VERBOSE:
        logger.info("Current: {:05.02f} Target(OFF): {:05.02f} Target(ON): {:05.02f} Freq {: 5.02f} Automatic: {} On: {}".format(t, OFF_THRESHOLD, ON_THRESHOLD, f.current / 1000.0, armed, enabled))
    if PREEMPT and is_fast and was_fast:
        enable = True
    elif armed:
        if t >= ON_THRESHOLD:
            enable = True
        elif t <= OFF_THRESHOLD:
            enable = False
        if set_fan(enable):
            last_change = t
    if not NOLED:
        update_led_temperature(t)

if __name__ == '__main__':
    first_run = True
    try:
        logger.info("fanshim started")
        while True:
            handle_fanshim()
            if first_run:
                first_run = False
                # Start up the server to expose the metrics.
                start_http_server(PROMETHEUS_METRIC_PORT)
            time.sleep(DELAY)
    except KeyboardInterrupt:
        pass
