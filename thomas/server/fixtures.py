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
    session = db.sqla.session
    clsname = constructor.__name__

    try:
        obj = constructor(**kwargs)
        session.add(obj)
        session.commit()

    except Exception as e:
        log.warn(f'  Could not create {clsname} {identifier}')
        log.warn(e)
        session.rollback()

    else:
        log.info(f'  Succesfully created {clsname} {identifier}')


# ------------------------------------------------------------------------------
# Model creation
# ------------------------------------------------------------------------------
def create_roles():
    log.info("Creating roles")

    try_to_create(db.Role, "root", id=1, name='root')
    try_to_create(db.Role, "admin", id=2, name='admin')
    try_to_create(db.Role, "user", id=3, name='user')


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
        id=1,
        username="root",
        password="toor",
        roles=root_roles,
    )


def create_networks():
    log.info("Creating networks")

    root = db.User.getByUsername('root')

    try_to_create(db.Network, 'lungcancer',
        id='lungcancer',
        name='Lungcancer',
        json=examples.get_lungcancer_network().as_dict(),
        owner=root,
    )

    try_to_create(db.Network, 'student',
        id='student',
        name='Student',
        json=examples.get_student_network().as_dict(),
        owner=root,
    )

    try_to_create(db.Network, 'sprinkler',
        id='sprinkler',
        name='Sprinkler',
        json=examples.get_sprinkler_network().as_dict(),
        owner=root,
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