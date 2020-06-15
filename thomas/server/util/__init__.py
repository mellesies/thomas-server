# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys
import os, os.path
import inspect

import logging
import logging.handlers

import colorama
from colorama import Fore, Style

import yaml
from appdirs import *

from . import Colorer
from .. import db

colorama.init()
using_console_for_logging = False

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def echo(msg, level="info"):
    type_ = {
        "error": f"[{Fore.RED}error{Style.RESET_ALL}]",
        "warn": f"[{Fore.YELLOW}warn{Style.RESET_ALL}]",
        "info": f"[{Fore.GREEN}info{Style.RESET_ALL}]",
        "debug": f"[{Fore.CYAN}debug{Style.RESET_ALL}]",
    }.get(level)
    print(f"{type_:16} - {msg}")


def info(msg):
    echo(msg, "info")


def warning(msg):
    echo(msg, "warn")


def error(msg):
    echo(msg, "error")


def debug(msg):
    echo(msg, "debug")


def sep(chr='-', rep=80):
    """Print a separator to the console."""
    print(chr * 80)

def log_full_request(request, log=None):
    if log is None:
        stack = inspect.stack()
        calling = stack[1]
        filename = os.path.split(calling.filename)[-1]
        module_name = os.path.splitext(filename)[0]

        log = logging.getLogger(module_name)

    log.info(f'{request.method}: {request.url}')
    log.info(f'  request.args: {request.args}')
    log.info(f'  request.data: {request.get_data()}')

    if request.is_json and len(request.data):
        log.info(f'  request.json: {request.json}')

    log.info(f'  headers:')
    for header in str(request.headers).splitlines():
        log.info(f'    ' + header)

def get_package_name():
    return __name__.split('.')[0]

def load_config(filename):
    """Load YAML configuration from disk."""
    with open(filename) as fp:
        config = yaml.load(fp, Loader=yaml.FullLoader)
        return config

def chdir(dirname=None):
    if not dirname:
        app = sys.argv[0]
        dirname = os.path.dirname(app)

    try:
      # This may fail if dirname == ''
      os.chdir(dirname)
    except:
      print("Could not change directory to: '%s'" % dirname)

def get_log(__name__):
    module_name = __name__.split('.')[-1]
    return logging.getLogger(module_name)



