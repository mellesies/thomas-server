#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os, sys
import datetime

import json

from flask import Flask, render_template, abort, redirect, url_for, request, make_response
from flask_cors import CORS
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_socketio import (
    SocketIO,
    emit, send,
    join_room, leave_room
)

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
app = Flask(APP_NAME)

# ------------------------------------------------------------------------------
# Enable cross-origin resource sharing
# ------------------------------------------------------------------------------
CORS(app)

# ------------------------------------------------------------------------------
# Setup Marshmallow for marshalling/serializing
# ------------------------------------------------------------------------------
ma = Marshmallow(app)

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
# Setup flask-socketio
# ------------------------------------------------------------------------------
socketio = SocketIO(app)


# ------------------------------------------------------------------------------
# Http routes
# ------------------------------------------------------------------------------
@app.route(WEB_BASE+'/', defaults={'path': ''})
@app.route(WEB_BASE+'/<path:path>')
def index(path):
    return "<html><body><h1>Hi there!!</h2></body></html>"



# ------------------------------------------------------------------------------
# Update the configuration
# ------------------------------------------------------------------------------
app.config.update(
    DEBUG=True,
    JSON_AS_ASCII=False,
)


def init(config_file, environment, system):
    # Load configuration and init logging
    # config = util.init(APP_NAME, config_file, environment, run_as_user)
    # db.init(config['database']['uri'])
    app_ctx = ctx.AppContext(
        APP_NAME,
        environment,
        config_file,
        system,
    )

    app_ctx.init()
    init_resources(app_ctx)

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
    config = app_ctx.config
    ip = ip or config['server']['ip'] or '127.0.0.1'
    port = port or config['server']['port'] or 5000

    # Run the (web)server without SSL
    log.warn(f'Starting server at http://{ip}:{port}')
    socketio.run(
        app, ip, port,
        debug=debug,
        log_output=False
    )



# ------------------------------------------------------------------------------
# __main__
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    config = init('config.yaml', 'dev')
    init_resources(config)
    run(config)


