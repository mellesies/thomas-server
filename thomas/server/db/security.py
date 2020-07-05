# -*- coding: utf-8 -*-
"""
"""
# from __future__ import unicode_literals, print_function

import os, random, string
import datetime, time
import uuid

from . import sqla

import bcrypt


__all__ = ['User', 'Role', 'association_table_user_role']


association_table_user_role = sqla.Table(
    'association_table_user_role',
    sqla.metadata,
    sqla.Column('user_id', sqla.Integer, sqla.ForeignKey('user.id')),
    sqla.Column('role_id', sqla.Integer, sqla.ForeignKey('role.id'))
)


# ------------------------------------------------------------------------------
# User
# ------------------------------------------------------------------------------
class Role(sqla.Model):

    name = sqla.Column(sqla.String, unique=True)

    def __repr__(self):
        return f"db.Role(name='{self.name}')"

    @classmethod
    def getRoleByName(cls, name):
        """Find a Role by its name."""
        session = sqla.session
        return session.query(cls).filter_by(name=name).one()


# ------------------------------------------------------------------------------
# User
# ------------------------------------------------------------------------------
class User(sqla.Model):

    # id = Column(Integer, primary_key=True)
    username = sqla.Column(sqla.String, unique=True)
    password_hash = sqla.Column(sqla.String)

    firstname = sqla.Column(sqla.String(50), default='')
    middlename = sqla.Column(sqla.String(25), default='')
    lastname = sqla.Column(sqla.String(50) , default='')

    roles = sqla.relationship(
        'Role',
        secondary=association_table_user_role,
        backref='users'
    )

    @classmethod
    def getByUsername(cls, username):
        """Get a user by username."""
        session = sqla.session
        return session.query(cls).filter_by(username=username).one()

    @classmethod
    def username_exists(cls, username):
        """Return True iff a username exists."""
        # session = db.Session()
        session = sqla.session
        exists = sqla.exists
        res = session.query(exists().where(cls.username == username)).scalar()
        return res


    def __repr__(self):
        """repr(x) <==> x.__repr__()"""
        return f"db.User(id={self.id}, username='{self.username}')"

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        self.set_password(value)

    # Copied from https://docs.pylonsproject.org/projects/pyramid/en/master/tutorials/wiki2/definingmodels.html
    def set_password(self, pw):
        """Set the user's password."""
        pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf8')

    # Copied from https://docs.pylonsproject.org/projects/pyramid/en/master/tutorials/wiki2/definingmodels.html
    def check_password(self, pw):
        """Return True iff the password is correct."""
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False

    def getFullname(self):
        """Return the full name of the user."""
        if self.middlename:
            return f'{self.firstname} {self.middlename} {self.lastname}'

        return f'{self.firstname} {self.lastname}'

    def isRoot(self):
        """Return True if the user is root."""
        return self.username == "root"

    def hasRole(self, roles):
        """Return true if the use has (any of) the role(s) requested."""
        if isinstance(roles, str):
            roles = [roles]

        roles = set(roles)
        user_roles = set([r.name for r in self.roles])

        return len(user_roles.intersection(roles)) > 0

