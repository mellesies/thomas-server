"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
PKG_NAME = 'thomas'
PKG_DESC = 'Thomas, the BN webinterface.'

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    PKG_DESCRIPTION = f.read()


# Read the API version from disk. This file should be located in the package
# folder, since it's also used to set the pkg.__version__ variable.
with open(path.join(here, PKG_NAME, 'VERSION')) as fp:
    PKG_VERSION = fp.read().strip()


# Setup the package
setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description=PKG_DESC,
    long_description=PKG_DESCRIPTION,
    url='',
    author='Melle Sieswerda',
    author_email='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3',
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
    ],
    package_data={
        PKG_NAME: [
            'VERSION',
            'server/resource/swagger/*.yaml'
        ],
    },
    entry_points={
        'console_scripts': [
            f'{PKG_NAME}={PKG_NAME}.cli:cli',
        ],
    },
    # dependency_links=[
    #     'https://github.com/IKNL/flasgger/archive/0.9.3.tar.gz#egg=flasgger-0.9.3'
    # ]
)
