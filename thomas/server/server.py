#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import datetime

import uuid
import json

from flask import Flask, render_template, abort, redirect, url_for, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt_claims, get_raw_jwt, jwt_required, jwt_optional, verify_jwt_in_request
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_socketio import (
    SocketIO,
    emit, send,
    join_room, leave_room
)

from sqlalchemy.engine.url import make_url

import logging

from . import ctx
from . import util
from . import resource
from . import db


# Define a module global log instance
logging.getLogger("urllib3").setLevel(logging.WARNING)
module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)

# Constants & defaults
APP_NAME = util.get_package_name()
PKG_NAME = util.get_package_name()

RESOURCES_INITIALIZED = False
WEB_BASE = '/app'


# ------------------------------------------------------------------------------
# Initialize Flask
# ------------------------------------------------------------------------------
ROOT_PATH = os.path.dirname(__file__)
app = Flask(APP_NAME, root_path=ROOT_PATH)

# ------------------------------------------------------------------------------
# Initialization of Marshmallow is deferred until init() is called and database
# has been initialized.
# ------------------------------------------------------------------------------
ma = Marshmallow()

# ------------------------------------------------------------------------------
# Enable cross-origin resource sharing
# ------------------------------------------------------------------------------
# CORS(app)
CORS(app, supports_credentials=True)



# ------------------------------------------------------------------------------
# Api - REST JSON-rpc
# ------------------------------------------------------------------------------
api = Api(app)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

@api.representation('application/json')
def output_json(data, code, headers=None):

    if isinstance(data, db.Base):
        data = db.jsonable(data)
    elif isinstance(data, list) and len(data) and isinstance(data[0], db.Base):
        data = db.jsonable(data)

    json_data = json.dumps(data, indent=4, sort_keys=False, cls=JSONEncoder)
    resp = make_response(json_data, code)
    resp.headers.extend(headers or {})

    return resp


# ------------------------------------------------------------------------------
# Setup the Flask-JWT-Extended extension (JWT: JSON Web Token)
# ------------------------------------------------------------------------------
jwt = JWTManager(app)

@jwt.user_claims_loader
def user_claims_loader(user):
    claims = {
        'roles': [role.name for role in user.roles],
    }

    return claims

@jwt.user_identity_loader
def user_identity_loader(user):
    if isinstance(user, db.User):
        return user.id

    msg = f"Could not create a JSON serializable identity from '{identity}'"
    log.error(msg)
    return None

@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return db.User.get(identity)


# ------------------------------------------------------------------------------
# Setup flask-socketio
# ------------------------------------------------------------------------------
socketio = SocketIO(app)


# ------------------------------------------------------------------------------
# Http routes
# ------------------------------------------------------------------------------
@app.route('/', defaults={'path': ''})
def root(path):
    return redirect(WEB_BASE, 301)

@app.route(WEB_BASE+'/', defaults={'path': ''})
@app.route(WEB_BASE+'/<path:path>')
# @app.route(WEB_BASE+'/index.html', defaults={'path': ''})
def index(path):
    # return "<html><body><h1>Hi there!!</h2></body></html>"
    # return redirect('/static/index.html', 301)
    return app.send_static_file('index.html')



# ------------------------------------------------------------------------------
# Update the configuration
# ------------------------------------------------------------------------------
app.config.update(
    DEBUG=True,
    JSON_AS_ASCII=False,
    JSON_SORT_KEYS=False,
    SECRET_KEY=str(uuid.uuid1()).encode('utf8'),
    # SECRET_KEY='developing'.encode('utf8'),
    SESSION_COOKIE_DOMAIN='zakbroek.com',
    SESSION_COOKIE_SAMESITE=None,
)

def init(config_file, environment, system, drop_database=False):
    global app, ma, database

    # Load configuration and init logging
    app_ctx = ctx.AppContext(
        APP_NAME,
        environment,
        config_file,
        system,
    )

    # Setup Marshmallow for marshalling/serializing
    # Order matters: Initialize SQLAlchemy before Marshmallow
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    URI = app_ctx.database_uri
    app.config["SQLALCHEMY_DATABASE_URI"] = URI

    url = make_url(URI)
    log.info("Initializing the database")
    log.debug("  driver:   {}".format(url.drivername))
    log.debug("  host:     {}".format(url.host))
    log.debug("  port:     {}".format(url.port))
    log.debug("  database: {}".format(url.database))
    log.debug("  username: {}".format(url.username))

    db.sqla.init_app(app)
    ma.init_app(app)

    return app_ctx


def init_resources(app_ctx):
    """Initialize the resources that handle the RESTful API requests."""
    config = app_ctx.config
    api_base = config['server']['api_path']
    exclude = config['server']['exclude']
    resource.init(api, api_base, exclude)


# ------------------------------------------------------------------------------
# run()
# ------------------------------------------------------------------------------
def run(app_ctx, ip=None, port=None, debug=True):
    """Run the server."""
    init_resources(app_ctx)

    config = app_ctx.config
    ip = ip or config['server']['ip'] or '127.0.0.1'
    port = port or config['server']['port'] or 5000
    # use_ssl = config['server'].get('use_ssl', False)
    secret_key = config['server'].get('jwt_secret_key', str(uuid.uuid1()))

    if app_ctx.environment == 'prod':
        debug = False

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
    app.config['JWT_SECRET_KEY'] = secret_key

    # Only useful if not running behind a proxy (like nginx). Even then,
    # self-signed certificates cause issues :-(
    # if use_ssl:
    #     cert_file = config['server'].get('cert_file', "cert.pem")
    #     key_file = config['server'].get('key_file', "key.pem")
    #
    #     util.create_self_signed_cert(
    #         cert_file,
    #         key_file,
    #         certargs={
    #             "Country": "NL",
    #              "State": "ZH",
    #              "City": "Oegstgeest",
    #              "Organization": "Sieswerda",
    #              "Org. Unit": "",
    #              "CN": 'sieswerda.net',
    #         }
    #     )
    #
    #     # Run the (web)server with SSL
    #     log.info(f'Starting server at https://{ip}:{port}')
    #     socketio.run(
    #         app, ip, port,
    #         debug=debug,
    #         certfile=cert_file, keyfile=key_file,
    #         log_output=False
    #     )

    # Run the (web)server without SSL
    log.warn(f'Starting server at http://{ip}:{port}')
    socketio.run(
        app, ip, port,
        debug=debug,
        log_output=False
    )



