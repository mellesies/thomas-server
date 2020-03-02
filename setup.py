# -*- coding: utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
PKG_NAME = "thomas-server"
PKG_DESC = "Thomas' RESTful API and webinterface."

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    PKG_DESCRIPTION = f.read()

# Read the API version from disk. This file should be located in the package
# folder, since it's also used to set the pkg.__version__ variable.
with open(path.join(here, 'thomas', 'server', 'VERSION')) as fp:
    PKG_VERSION = fp.read().strip()


# Setup the package
setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description=PKG_DESC,
    long_description=PKG_DESCRIPTION,
    url='https://github.com/mellesies/thomas-server',
    author='Melle Sieswerda',
    author_email='m.sieswerda@iknl.nl',
    packages=find_namespace_packages(include=['thomas.*']),
    python_requires='>= 3.6',
    install_requires=[
        'appdirs',
        'bcrypt',
        'click',
        'eventlet',
        'flask',
        'flask-cors',
        'flask-restful',
        'flask-socketio',
        'flask_marshmallow',
        'flask_jwt_extended',
        'marshmallow',
        'marshmallow-sqlalchemy',
        'pyyaml',
        'requests',
        'sqlalchemy',
        'termcolor',
        'lark-parser',
        'networkx',
        'thomas-core @git+https://github.com/mellesies/thomas-core',
    ],
    package_data={
        "": [
            "config.yaml"
        ],
        "thomas.server": [
            "VERSION",
            "data/*.lark",
            "data/*.json",
            "data/*.oobn",
        ],
    },
    entry_points={
        'console_scripts': [
            f'thomas=thomas.server.cli:cli',
        ],
    },
)
