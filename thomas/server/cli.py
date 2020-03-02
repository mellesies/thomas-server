# -*- coding: utf-8 -*-
import click

import logging
import warnings
warnings.filterwarnings("ignore")

from . import util
from . import server

# ------------------------------------------------------------------------------
# bnserver 
# ------------------------------------------------------------------------------
@click.group()
def cli():
    """Main entry point for CLI scripts."""
    pass


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

