# -*- coding: utf-8 -*-
"""
Resources ...
"""
import sys
import os, os.path
import glob
import importlib
from functools import wraps

from http import HTTPStatus
from flask import g, abort, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims
)

import datetime
import logging

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)

from .. import db
from ..util import get_package_name, get_log, log_full_request

__RESOURCES_INITIALIZED = False

# ------------------------------------------------------------------------------
# Helper functions/decoraters ...
# ------------------------------------------------------------------------------
def parse_datetime(dt=None, default=None):
    if dt:
        return datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%f')

    return default

def only_for(types = {'user', 'api-token'}):
    """JWT endpoint protection decorator"""
    def protection_decorator(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):

            # decode JWT-token
            identity = get_jwt_identity()
            claims = get_jwt_claims()

            roles = set(claims['roles'])
            type_set = set(types)
            intersection = type_set.intersection(roles)

            # log.debug(f'roles: {roles}')
            # log.debug(f'type_set: {type_set}')
            # log.debug(f'intersection: {intersection}')
            # log.debug(f'len(intersection): {len(intersection)}')

            # Root may do everything :-)
            is_root_or_for_everyone = ('root' in roles) or ('everyone' in types)

            if len(intersection) == 0 and not is_root_or_for_everyone:
                abort(403)

            return fn(*args, **kwargs)
        return jwt_required(decorator)
    return protection_decorator

# create alias decorators
with_user = only_for(["user"])

def init(api, api_base, exclude=None):
    """Initialize resources."""
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

# ------------------------------------------------------------------------------
# Base class for FHIR resources
# ------------------------------------------------------------------------------
class BaseResource(Resource):
    """CRUD operations for resources."""

    # Decoraters to be applied to all REST methods:
    # method_decorators = [...]

    def __init__(self, schema_class):
        """Create a new BaseResource instance."""
        self.schema_class = schema_class
        self.schema_args = {}
        self._schema = None

    @classmethod
    def clsname(cls):
        """x.clsname <==> x.__class__.__name__"""
        return cls.__name__

    @property
    def schema(self):
        if self._schema is None:
            self._schema = self.schema_class(**self.schema_args)

        return self._schema

    def _search(self, *args, **kwargs):
        """Search ..."""
        # FIXME: implement filtering/searching
        results = getattr(db, self.clsname()).get()

        self.schema.context['links'] = request.args.get('links', True)
        self.schema.context['embed'] = request.args.getlist('embed')

        return self.schema.dump(results, many=True)

    def _read(self, id):
        """Read a single resource."""
        result = getattr(db, self.clsname()).get(id)

        self.schema.context['links'] = request.args.get('links', True)
        self.schema.context['embed'] = request.args.getlist('embed')

        return self.schema.dump(result, many=False)

    def _create(self, data):
        """Create a new resource."""
        pass

    def _update(self, id, data):
        """Update a resource."""
        pass

    def _delete(self, id):
        """Delete a resource."""
        pass


    # --------------------------------------------------------------------------
    # HTTP methods
    # --------------------------------------------------------------------------
    def get(self, id_or_operation=None):
        """Search or read."""
        log = get_log(__name__)
        # log_full_request(request, log)

        if id_or_operation:
            func = self._read

            if id_or_operation.startswith('_'):

                try:
                    func = getattr(self, id_or_operation)

                except Exception as e:
                    log.warn("Could not find operation '{id_or_operation}'!?")
                    log.warn(e)
                    log.debug("Defaulting to '_read'")

            return func(id_or_operation)

        return self._search(id_or_operation)

    def post(self, id_or_operation=None):
        """Create a resource or execute an operation."""
        log = get_log(__name__)

        if id_or_operation is None:
            # log.info('reqular POST')
            data = request.json
            return self._create(data)

        elif id_or_operation.startswith('_'):
            # Dispatch request to appropriate handler
            try:
                func = getattr(self, id_or_operation)
            except AttributeError as e:
                log.error(f'Could not execute method "{id_or_operation}": {e}')
                abort(HTTPStatus.METHOD_NOT_ALLOWED)

            return func()

        elif id_or_operation == '_search':
            params = request.form
            # log.info(f'params: {params}')
            return self._search(**params)

    def put(self, id_or_operation):
        """Update or create a resource."""
        log = get_log(__name__)

        data = request.json
        return self._update(id_or_operation, data)

    def delete(self, id_or_operation):
        """Delete a resource."""
        self._delete(id_or_operation)

