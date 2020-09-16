from datetime import datetime
from enum import IntEnum, auto

import config

class LogLevel(IntEnum):
    TRACE   = auto()
    DEBUG   = auto()
    INFO    = auto()
    WARN    = auto()
    ERROR   = auto()
    FATAL   = auto()

def _write_log(message, level=LogLevel.INFO):
    if config.DEBUG or level >= LogLevel.INFO:
        logtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("%s [%s] %s" % (logtime, level.name, message))

def trace(message):
    _write_log(message, LogLevel.TRACE)

def debug(message):
    _write_log(message, LogLevel.DEBUG)

def info(message):
    _write_log(message, LogLevel.INFO)

def warn(message):
    _write_log(message, LogLevel.WARN)

def error(message):
    _write_log(message, LogLevel.ERROR)

def fatal(message):
    _write_log(message, LogLevel.FATAL)