# -*- coding: utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages

# To use a consistent encoding
from codecs import open
import os
from os import path

here = path.abspath(path.dirname(__file__))
PKG_NAME = "thomas-server"
PKG_DESC = "Thomas' RESTful API and webinterface."

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    PKG_DESCRIPTION = f.read()

# Read the API version from disk. This file should be located in the package
# folder, since it's also used to set the pkg.__version__ variable.
version_path = os.path.join(here, 'thomas', 'server', '_version.py')
version_ns = {
    '__file__': version_path
}
with open(version_path) as f:
    exec(f.read(), {}, version_ns)

def package_files(directory, base=''):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            p = os.path.join(path, filename)
            paths.append(p.replace(base, ''))
    return paths


thomas_server_files = [
    "__build__",
]

thomas_server_files.extend(
    package_files(
        'thomas/server/static/',
        base='thomas/server/'
    )
)

# Setup the package
setup(
    name=PKG_NAME,
    version=version_ns['__version__'],
    description=PKG_DESC,
    long_description=PKG_DESCRIPTION,
    long_description_content_type='text/markdown',
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
        'flask>=1.1',
        'flask-cors',
        'flask-restful',
        'flask-socketio>=4.2',
        'flask_marshmallow',
        'flask_jwt_extended',
        'marshmallow',
        'marshmallow-sqlalchemy',
        'pyyaml',
        'requests',
        'sqlalchemy>=1.3',
        'termcolor',
        'thomas-core',
    ],
    package_data={
        "": [
            "config.yaml"
        ],
        "thomas.server": thomas_server_files,
    },
    entry_points={
        'console_scripts': [
            f'thomas=thomas.server.cli:cli',
        ],
    },
)
