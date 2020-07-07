# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys
import os, os.path
import inspect

# from datetime import timedelta, datetime
# import ipaddress

import logging
import logging.handlers

import colorama
from colorama import Fore, Style

import yaml
from appdirs import *

from . import Colorer
from .. import db

colorama.init()

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)
using_console_for_logging = False

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def echo(msg, level="info"):
    type_ = {
        "error": f"[{Fore.RED}error{Style.RESET_ALL}]",
        "warn": f"[{Fore.YELLOW}warn{Style.RESET_ALL}]",
        "info": f"[{Fore.GREEN}info{Style.RESET_ALL}]",
        "debug": f"[{Fore.CYAN}debug{Style.RESET_ALL}]",
    }.get(level)
    print(f"{type_:16} - {msg}")


def debug(msg):
    echo(msg, "debug")

def info(msg):
    echo(msg, "info")

def warning(msg):
    echo(msg, "warn")

def error(msg):
    echo(msg, "error")


def sep(chr='-', rep=80):
    """Print a separator to the console."""
    print(chr * 80)

def log_full_request(request, log=None):
    if log is None:
        stack = inspect.stack()
        calling = stack[1]
        filename = os.path.split(calling.filename)[-1]
        module_name = os.path.splitext(filename)[0]

        log = logging.getLogger(module_name)

    log.info(f'{request.method}: {request.url}')
    log.info(f'  request.args: {request.args}')
    log.info(f'  request.data: {request.get_data()}')

    if request.is_json and len(request.data):
        log.info(f'  request.json: {request.json}')

    log.info(f'  headers:')
    for header in str(request.headers).splitlines():
        log.info(f'    ' + header)

def get_package_name():
    return __name__.split('.')[0]

def load_config(filename):
    """Load YAML configuration from disk."""
    with open(filename) as fp:
        config = yaml.load(fp, Loader=yaml.FullLoader)
        return config

def chdir(dirname=None):
    if not dirname:
        app = sys.argv[0]
        dirname = os.path.dirname(app)

    try:
      # This may fail if dirname == ''
      os.chdir(dirname)
    except:
      print("Could not change directory to: '%s'" % dirname)

def get_log(__name__):
    module_name = __name__.split('.')[-1]
    return logging.getLogger(module_name)


# ------------------------------------------------------------------------------
# Certificate stuff
# ------------------------------------------------------------------------------
# def create_self_signed_cert(certfile, keyfile, certargs, cert_dir="."):
#
#     C_F = os.path.join(cert_dir, certfile)
#     K_F = os.path.join(cert_dir, keyfile)
#
#     log.info(f"Checking for self-signed certificates at")
#
#     if not os.path.exists(C_F) or not os.path.exists(K_F):
#         log.warn(f"Creating new certificate files '{C_F}' and '{K_F}'")
#         cert_pem, key_pem = generate_selfsigned_cert(
#             'localhost',
#             ['127.0.0.1', '192.168.2.35'],
#         )
#
#         open(C_F, "wb").write(cert_pem)
#         open(K_F, "wb").write(key_pem)
#
#         # k = crypto.PKey()
#         # k.generate_key(crypto.TYPE_RSA, 1024)
#
#         # cert = crypto.X509()
#         # cert.get_subject().C = certargs["Country"]
#         # cert.get_subject().ST = certargs["State"]
#         # cert.get_subject().L = certargs["City"]
#         # cert.get_subject().O = certargs["Organization"]
#         # # cert.get_subject().OU = certargs["Org. Unit"]
#         # cert.get_subject().CN = certargs["CN"]
#
#         # san_list = ["IP:192.168.2.35"]
#         # cert.add_extensions([
#         #     crypto.X509Extension(
#         #         b"subjectAltName", False, (", ".join(san_list)).encode()
#         #    )
#         # ])
#
#         # cert.set_serial_number(1000)
#         # cert.gmtime_adj_notBefore(0)
#
#         # # cert.gmtime_adj_notAfter(315360000)
#         # cert.gmtime_adj_notAfter(1 * 365 * 24 * 60 * 60)
#         # cert.set_issuer(cert.get_subject())
#         # cert.set_pubkey(k)
#         # cert.sign(k, 'sha1')
#         # open(C_F, "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#         # open(K_F, "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
#
#     else:
#         log.info(f"Certificate found! cert: '{C_F}', key: '{K_F}'")
#
# def generate_selfsigned_cert(hostname, ip_addresses=None, key=None):
#     """Generates self signed certificate for a hostname, and optional IP addresses."""
#     from cryptography import x509
#     from cryptography.x509.oid import NameOID
#     from cryptography.hazmat.primitives import hashes
#     from cryptography.hazmat.backends import default_backend
#     from cryptography.hazmat.primitives import serialization
#     from cryptography.hazmat.primitives.asymmetric import rsa
#
#     # Generate our key
#     if key is None:
#         key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend(),
#         )
#
#     name = x509.Name([
#         x509.NameAttribute(NameOID.COMMON_NAME, hostname)
#     ])
#
#     # best practice seem to be to include the hostname in the SAN, which *SHOULD* mean COMMON_NAME is ignored.
#     alt_names = [x509.DNSName(hostname)]
#
#     # allow addressing by IP, for when you don't have real DNS (common in most testing scenarios
#     if ip_addresses:
#         for addr in ip_addresses:
#             # openssl wants DNSnames for ips...
#             alt_names.append(x509.DNSName(addr))
#             # ... whereas golang's crypto/tls is stricter, and needs IPAddresses
#             # note: older versions of cryptography do not understand ip_address objects
#             alt_names.append(x509.IPAddress(ipaddress.ip_address(addr)))
#
#     san = x509.SubjectAlternativeName(alt_names)
#
#     # path_len=0 means this cert can only sign itself, not other certs.
#     basic_contraints = x509.BasicConstraints(ca=True, path_length=0)
#     now = datetime.utcnow()
#     cert = (
#         x509.CertificateBuilder()
#         .subject_name(name)
#         .issuer_name(name)
#         .public_key(key.public_key())
#         .serial_number(1000)
#         .not_valid_before(now)
#         .not_valid_after(now + timedelta(days=2*365))
#         .add_extension(basic_contraints, False)
#         .add_extension(san, False)
#         .sign(key, hashes.SHA256(), default_backend())
#     )
#     cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
#     key_pem = key.private_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PrivateFormat.TraditionalOpenSSL,
#         encryption_algorithm=serialization.NoEncryption(),
#     )
#
#     return cert_pem, key_pem


