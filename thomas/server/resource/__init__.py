# -*- coding: utf-8 -*-
"""
Resources ...
"""
import sys
import os, os.path
import glob
import importlib

from flask import g
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims
)

import datetime
import logging
# log = logging.getLogger(__name__)
module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)

from ..util import get_package_name

__RESOURCES_INITIALIZED = False

# ------------------------------------------------------------------------------
# Helper functions/decoraters ...
# ------------------------------------------------------------------------------
def parse_datetime(dt=None, default=None):
    if dt:
        return datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%f')

    return default


def init(api, api_base, exclude=None):
    global __RESOURCES_INITIALIZED
    if __RESOURCES_INITIALIZED:
        return True

    # Make sure exclude is a list instead of None
    exclude = exclude or []
    exclude.append('__init__')
    exclude = [e + '.py' for e in exclude]

    # Get the name of the root package
    pkg_name = get_package_name()

    # Retrieve all modules in the resource folder.
    cwd = os.path.dirname(__file__)
    modules = glob.glob(os.path.join(cwd, "*.py"))
    modules = [os.path.basename(f) for f in modules]
    modules = [os.path.splitext(f)[0] for f in modules if f not in exclude]

    log.info(f'Found the following modules: {modules}')
    log.debug(f'Will not include: {exclude}')

    # Import the modules and call setup()
    for name in modules:
        module = importlib.import_module(f'{pkg_name}.server.resource.{name}')
        module.setup(api, api_base)

    __RESOURCES_INITIALIZED = True
    return True


