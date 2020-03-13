# -*- coding: utf-8 -*-
"""
"""
# from __future__ import unicode_literals, print_function

import os, random, string
import datetime, time
import uuid

from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.ext.hybrid import hybrid_property

import bcrypt


from .. import db
from . import Base

__all__ = ['User', 'Role']


association_table_user_role = Table(
    'association_table_user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)


# ------------------------------------------------------------------------------
# User
# ------------------------------------------------------------------------------
class Role(Base):
    __tablename__ = 'role'

    name =  Column(String, unique=True)

    def __repr__(self):
        return f"<Role name='{self.name}'>"

    @classmethod
    def getRoleByName(cls, name):
        """Find a Role by its name."""
        session = db.Session()
        return session.query(cls).filter_by(name=name).one()


# ------------------------------------------------------------------------------
# User
# ------------------------------------------------------------------------------
class User(Base):
    __tablename__ = 'user'

    # id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)

    firstname = Column(String(50), default='')
    middlename = Column(String(25), default='')
    lastname = Column(String(50) , default='')

    roles = relationship(
        'Role',
        secondary=association_table_user_role,
        backref='users'
    )

    def __repr__(self):
        """repr(x) <==> x.__repr__()"""
        return f"<db.security.User(id={self.id}, username='{self.username}')>"

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

    @classmethod
    def getByUsername(cls, username):
        """Get a user by username."""
        session = db.Session()
        return session.query(cls).filter_by(username=username).one()

    @classmethod
    def username_exists(cls, username):
        """Return True iff a username exists."""
        session = db.Session()
        res = session.query(exists().where(cls.username == username)).scalar()
        return res

    def getFullname(self):
        """Return the full name of the user."""
        if self.middlename:
            return f'{self.firstname} {self.middlename} {self.lastname}'

        return f'{self.firstname} {self.lastname}'
