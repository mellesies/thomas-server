# -*- coding: utf-8 -*-
import click

import logging
import warnings
warnings.filterwarnings("ignore")

from . import util
from . import server
from . import fixtures

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
@click.option('-c', '--config', default='config.yaml', help='filename of config file; overrides --name if provided')
@click.option('-e', '--environment', default='dev', help='database environment to use')
@click.option('--system', default=False, help='Run the server as a system user')
@click.option('--debug/--no-debug', default=True, help='run server in debug mode (auto-restart)')
def cli_server_start(ip, port, config, system, environment, debug):
    """Start the server."""
    ctx = server.init(config, environment, system)
    server.run(ctx, ip, port, debug)


# ------------------------------------------------------------------------------
# thomas shell
# ------------------------------------------------------------------------------
@cli.command(name='shell')
@click.option('-c', '--config', default='config.yaml', help='filename of config file; overrides --name if provided')
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
    ctx = server.init(config, environment, system)

    # Make the db easily accessible
    from . import db

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
@click.option('-c', '--config', default='config.yaml', help='filename of config file; overrides --name if provided')
@click.option('-e', '--environment', default='dev', help='database environment to use')
@click.option('--system', default=False, help='Run the server as a system user')
def cli_fixtures(config, environment, system):
    """Load fixtures."""

    # Initialize the database
    ctx = server.init(config, environment, system)

    # Run the fixtures ...
    fixtures.run()