# -*- coding: utf-8 -*-
import os
import sys
import click

import logging
import warnings
warnings.filterwarnings("ignore")

import json
import yaml

from . import util
from . import error
from . import server
from . import fixtures
from . import db

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


# ------------------------------------------------------------------------------
# thomas
# ------------------------------------------------------------------------------
@click.group()
def cli():
    """Command Line Interface to Thomas' RESTful API and webinterface."""
    pass


# ------------------------------------------------------------------------------
# thomas start
# ------------------------------------------------------------------------------
@cli.command(name='start')
@click.option('--ip', type=str, help='ip address to listen on')
@click.option('-p', '--port', type=int, help='port to listen on')
@click.option('-c', '--config', default='config.yaml', help='filename of config file')
@click.option('-e', '--environment', default='dev', help='database environment to use')
@click.option('--system', default=False, help='Run the server as a system user')
@click.option('--debug/--no-debug', default=True, help='run server in debug mode (auto-restart)')
def cli_server_start(ip, port, config, system, environment, debug):
    """Start the server."""
    try:
        ctx = server.init(config, environment, system)

    except error.ConfigNotFoundError as e:
        util.error('Bailing out ...')
        sys.exit(1)

    server.run(ctx, ip, port, debug)


# ------------------------------------------------------------------------------
# thomas shell
# ------------------------------------------------------------------------------
@cli.command(name='shell')
@click.option('-c', '--config', default='config.yaml', help='filename of config file')
@click.option('-e', '--environment', default='dev', help='database environment to use')
@click.option('--system', default=False, help='Run the server as a system user')
def cli_shell(config, environment, system):
    """Run a shell with access to the database."""

    # Suppress logging (e.g. on tab-completion)
    import logging
    logging.getLogger('parso.cache').setLevel(logging.WARNING)
    logging.getLogger('parso.python.diff').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    del logging

    # Initialize the database
    try:
        ctx = server.init(config, environment, system)

    except error.ConfigNotFoundError:
        # Not good. Exit!
        sys.exit(1)

    server.app.app_context().push()
    db.sqla.create_all()

    # Run the iPython shell
    import IPython
    from traitlets.config import get_config
    c = get_config()
    c.InteractiveShellEmbed.colors = "Linux"

    print()
    IPython.embed(config=c)


# ------------------------------------------------------------------------------
# thomas load-fixtures
# ------------------------------------------------------------------------------
@cli.command(name='load-fixtures')
@click.option('--drop-database/--keep-database', default=False, help='drop database before loading fixtures')
@click.option('-c', '--config', default='config.yaml', help='filename of config file')
@click.option('-e', '--environment', default='dev', help='database environment to use')
@click.option('--system', default=False, help='Run the server as a system user')
def cli_fixtures(config, environment, system, drop_database):
    """Load fixtures."""

    # Initialize the database
    try:
        ctx = server.init(config, environment, system, drop_database)

    except error.ConfigNotFoundError:
        # Not good. Exit!
        sys.exit(1)

    server.app.app_context().push()
    db.sqla.create_all()

    # Run the fixtures ...
    fixtures.run()


# ------------------------------------------------------------------------------
# thomas import
# ------------------------------------------------------------------------------
@cli.command(name='import')
@click.option('--drop-database/--keep-database', default=False, help='drop database before loading fixtures')
@click.option('-c', '--config', default='config.yaml', help='filename of config file')
@click.option('-e', '--environment', default='dev', help='database environment to use')
@click.option('--system', default=False, help='Run the server as a system user')
@click.argument('filename')
def cli_import(config, environment, system, drop_database, filename):
    """Import data (json or yaml)."""

    # Initialize the database
    ctx = server.init(config, environment, system, drop_database)

    # Load the data
    try:
        with open(filename) as fp:
            data = fp.read()

    except FileNotFoundError as e:
        log.error(e)
        sys.exit(1)


    ext = os.path.splitext(filename)[-1]
    if ext == '.yaml':
        data = yaml.load(data)

    elif ext == '.json':
        data = json.loads(data)

    else:
        log.error('Invalid filetype?')
        sys.exit(1)

    db.import_data(data)


