# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys
import os, os.path

import logging
import logging.handlers

import yaml
from appdirs import *

from . import Colorer
from .. import db

using_console_for_logging = False

def sep(chr='-', rep=80):
    """Print a separator to the console."""
    print(chr * 80)

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



