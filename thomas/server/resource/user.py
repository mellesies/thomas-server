# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/user'
"""
import os
import logging

from flask_restful import Resource
from flask_jwt_extended import current_user as user
from flask_jwt_extended import jwt_required

from . import BaseResource, only_for, with_user
from .. import server
from .. import db
from ._schema import *

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    schema_class = UserSchema

    api.add_resource(
        User,
        path,
        path + '/<string:id_or_operation>',
        resource_class_kwargs={'schema_class': schema_class},
    )


# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class User(BaseResource):
    """Resource for user"""
    pass



