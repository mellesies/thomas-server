# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/token'
"""
from __future__ import print_function, unicode_literals
import os
import logging

from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_refresh_token_required, create_access_token, create_refresh_token, get_jwt_identity
from http import HTTPStatus
from pathlib import Path

from .. import server
from .. import db
from .. import util

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    api.add_resource(
        Token,
        path,
        endpoint='token',
        methods=('POST',)
    )

    api.add_resource(
        RefreshToken,
        path+'/refresh',
        endpoint='refresh_token',
        methods=('POST',)
    )


# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class Token(Resource):
    """resource for api/token"""

    def post(self):
        """Authenticate user or node"""
        util.log_full_request(request)

        if not request.is_json:
            log.warning('POST request without JSON body.')
            return {"msg": "Missing JSON in request"}, HTTPStatus.BAD_REQUEST

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not (username and password):
            msg = "no user/password combination provided"
            return {"msg": msg}, HTTPStatus.UNAUTHORIZED

        log.info("trying to login '{}'".format(username))

        if db.User.username_exists(username):
            user = db.User.getByUsername(username)
            if not user.check_password(password):
                msg = "password for username={} is invalid".format(username)
                log.error(msg)
                return {"msg": msg}, HTTPStatus.UNAUTHORIZED
        else:
            msg = f"username '{username}' does not exist"
            log.error(msg)
            return {"msg": msg}, HTTPStatus.UNAUTHORIZED

        log.info("Successful login for '{}'".format(username))

        ret = {
            'access_token': create_access_token(user),
            'refresh_token': create_refresh_token(user),
            'refresh_url': server.api.url_for(RefreshToken),
            'fullname': user.getFullname(),
        }

        return ret, HTTPStatus.OK


class RefreshToken(Resource):

    @jwt_refresh_token_required
    def post(self):
        """Create a token from a refresh token."""
        user_id = get_jwt_identity()
        log.info(f'Refreshing token for user_id {user_id}')
        user = db.User.get(user_id)
        ret = {'access_token': create_access_token(user)}

        return ret, HTTPStatus.OK
