# -*- coding: utf-8 -*-
import os, sys

import logging
from logging.handlers import RotatingFileHandler

from appdirs import *
import yaml

from . import db
from . import util

log = util.get_log(__name__)

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppContext(object, metaclass=Singleton):
    """AppContext holds the context for the current application.

    This includes file locations and database connections.
    """

    def __init__(self, app_name, environment, config_file='config.yaml',
                 system_context=False):
        """Create a new AppContext instance.

        Args;
            environment (str): Environment, as defined in the configuration
                file, to use.
            config_file (str): Path to the configuration file.
            system_context (bool): Signals whether the application should run
                in a system (True) or user (False) context. This determines
                where the application looks for and stores files.
        """
        # app = sys.argv[0]
        # dirname = os.path.dirname(app)

        self.app_name = app_name
        self.app_author = ''
        self.environment = environment
        self.config_file = config_file
        self.system_context = system_context

        self.config = None

    def __repr__(self):
        """repr(x) <==> x.__repr__()"""
        app = self.app_name
        env = self.environment

        return f"AppContext('{app}', {env})"

    def find_config(self):
        app_name = self.app_name
        app_author = self.app_author
        filename = self.config_file

        if self.system_context:
            dirs = [
                f'/etc/{app_name}/',
                site_config_dir(app_name, app_author)
            ]

        else:
            dirs = [
                './',
                user_config_dir(app_name, app_author)
            ]

        for location in dirs:
            fullpath = os.path.join(location, filename)

            if os.path.exists(fullpath):
                return fullpath

        msg = f'Could not find configuration file "{filename}"!?'
        log.error(msg)
        log.info('Tried the following directories:')
        for d in dirs:
            log.info(f' * {d}')

        raise Exception(msg)

    def load_config(self):
        """Load YAML configuration from disk."""
        filename = self.find_config()

        # sep()
        # print(f'Using configuration at "{filename}"')
        # sep()

        with open(filename) as fp:
            config = yaml.load(fp, Loader=yaml.FullLoader)

        self.config_file = filename
        self.config = config['environment'][self.environment]

    def abspath(self, path, type):
        """Return the absolute path for a path."""
        assert type in ['log', 'data'], "'type' should be 'log' or 'data'"

        if os.path.isabs(path):
            return path

        app_name = self.app_name
        app_author = self.app_author

        if self.system_context:
            base = site_data_dir(app_name, app_author)
        else:
            base = user_data_dir(app_name, app_author)

        return os.path.join(base, type, path)

    def setup_logging(self):
        """Setup the logging system."""
        msg = "Configuration should be loaded first!"
        assert self.config is not None, msg

        config = self.config
        level = config["logging"]["level"]

        if level == 'NONE':
          return

        level = getattr(logging, level.upper())
        filename = config["logging"]["file"]
        format = config["logging"]["format"]

        # Create the root logger
        logger = logging.getLogger()
        logger.setLevel(level)

        if filename:
            filename = self.abspath(filename, 'log')
            bytes_ = config["logging"]["max_size"]
            count = config["logging"]["backup_count"]

            # Create RotatingFileHandler
            log_dir = os.path.dirname(filename)

            if not os.path.exists(log_dir):
                print(f'⚠️  Location used for logging does not exist!')
                print(f'⚠️  Creating "{log_dir}"')
                os.makedirs(log_dir)

            bytes_ = 1024 * bytes_
            rfh = RotatingFileHandler(filename, 'a', bytes_, count)
            rfh.setLevel(level)
            rfh.setFormatter(logging.Formatter(format))
            logger.addHandler(rfh)

        # Check what to do with the console output ...
        if config["logging"]["use_console"]:
              ch = logging.StreamHandler(sys.stdout)
              ch.setLevel(level)
              ch.setFormatter(logging.Formatter(format))
              logger.addHandler(ch)


        # Finally, capture all warnings using the logging mechanism.
        logging.captureWarnings(True)

    def setup_database(self):
        """Initialize the database."""
        msg = "Configuration should be loaded first!"
        assert self.config is not None, msg

        config = self.config
        uri = config['database']['uri']
        db.init(self, uri)

    def init(self):
        """Set the CWD, load the config file and setup logging."""
        # Read the command line parameters and change directory to the application
        # root.
        app = self.app_name
        env = self.environment

        self.load_config()
        self.setup_logging()

        log.info(f"#" * 80)
        log.info(f"#{app:^78}#")
        log.info(f"#" * 80)
        log.info(f"Started application '{app}' ({env})")
        log.info(f"Current working directory is '{os.getcwd()}'")
        log.info(f"Succesfully loaded configuration from '{self.config_file}'")

        self.setup_database()


