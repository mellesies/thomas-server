# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/token'
"""
import os
import logging

from flask import request, jsonify
from flask_restful import Resource
from http import HTTPStatus

from .. import util
from .. import server

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    api.add_resource(
        Version,
        path,
        endpoint='version',
        methods=('GET',)
    )


# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class Version(Resource):
    """resource for api/token"""

    def get(self):
        """Get the current version."""
        # return util.get_package_name()
        return 'Version 0.01 - alpha'