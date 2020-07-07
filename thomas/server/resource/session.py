# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/session'
"""
import os
import logging

from flask import request, redirect, session, abort
from flask_restful import Resource
from flask_jwt_extended import jwt_refresh_token_required, create_access_token, create_refresh_token, get_jwt_identity
from http import HTTPStatus

import requests
from urllib.parse import urlencode
from uuid import uuid1

from . import BaseResource, only_for, with_user
from .. import server
from .. import db
from .. import util

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    api.add_resource(
        Session,
        path,
        # path + '/<string:id_or_operation>',
    )


# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class Session(Resource):
    """resource for Session Launch"""

    def get(self, id_or_operation=None):
        """Return Session contents."""
        util.log_full_request(request)
        log.warn(session)

        if id_or_operation and id_or_operation.startswith('_'):
            try:
                func = getattr(self, id_or_operation)
            except Exception as e:
                log.warn("Could not find operation '{id_or_operation}'!?")
                log.warn(e)
            else:
                return func()

        return dict(session)


