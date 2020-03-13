# -*- coding: utf-8 -*-
import logging

from . import db
from thomas.core import examples

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


# ------------------------------------------------------------------------------
# Helper function
# ------------------------------------------------------------------------------
def try_to_create(constructor, identifier, **kwargs):
    session = db.Session()
    clsname = constructor.__name__

    try:
        obj = constructor(**kwargs)
        session.add(obj)
        session.commit()

    except Exception as e:
        log.warn(f'  Could not create {clsname} {identifier}')
        # log.exception(e)
        session.rollback()

    else:
        log.info(f'  Succesfully created {clsname} {identifier}')


# ------------------------------------------------------------------------------
# Model creation
# ------------------------------------------------------------------------------
def create_roles():
    log.info("Creating roles")

    try_to_create(db.Role, "root", name='root')
    try_to_create(db.Role, "admin", name='admin')


def create_users():
    log.info("Creating users")

    roles = {
        "root": db.Role.getRoleByName('root'),
        "admin": db.Role.getRoleByName('admin'),
    }

    root_roles = [roles['root'], roles['admin']]
    admin_roles = [roles['admin']]

    try_to_create(
        db.User,
        "root",
        username="root",
        password="toor",
        roles=root_roles,
    )


def create_networks():
    log.info("Creating networks")

    try_to_create(db.Network, 'lungcancer',
        abbr='lungcancer',
        name='Lungcancer',
        json=examples.get_lungcancer_network().as_dict(),
    )

    try_to_create(db.Network, 'student',
        abbr='student',
        name='Student',
        json=examples.get_student_network().as_dict(),
    )

    try_to_create(db.Network, 'sprinkler',
        abbr='sprinkler',
        name='Sprinkler',
        json=examples.get_sprinkler_network().as_dict(),
    )



# ------------------------------------------------------------------------------
# __main__ and entry points
# ------------------------------------------------------------------------------
def run():
    """Load fixtures."""
    log.info('Loading fixtures')
    create_roles()
    create_users()
    create_networks()