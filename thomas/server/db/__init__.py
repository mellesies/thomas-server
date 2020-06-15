# -*- coding: utf-8 -*-
"""
"""
import os
import datetime
import logging

from flask_sqlalchemy import SQLAlchemy, Model

from sqlalchemy import (
    create_engine, inspect,
    Table, Column, ForeignKey,
    Integer, String, Text, DateTime,
)
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm.exc import NoResultFound

import json
import yaml

import enum

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)

# Globals for relational database
# engine = None
# Session = None
# object_session = None


# ------------------------------------------------------------------------------
# Base declaration.
# ------------------------------------------------------------------------------
class Base(Model):
    """Declarative base that defines default attributes."""
    _hidden_attributes = []

    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()

    # Primay key, internal use only
    id = Column(Integer, primary_key=True)

    @classmethod
    def clsname(cls):
        """x.classname <==> x.__class__.__name__"""
        return cls.__name__

    @classmethod
    def get(cls, id_=None, with_session=False):
        # session = Session()
        session = sqla.session

        if id_ is None:
            result = session.query(cls).all()
        else:
            try:
                result = session.query(cls).filter_by(id=id_).one()
            except NoResultFound:
                result = None

        if with_session:
            return result, session

        return result

    def save(self):
        if self.id is None:
            # FIXME: this is dangerous: when session.add() fails (due to table
            #        constraints, for example) it is not possible to call
            #        session.rollback()
            # session = Session()
            session = sqla.session
            session.add(self)
        else:
            session = sqla.session.object_session(self)

        session.commit()

    def delete(self):
        if not self.id:
            session = Session()
        else:
            session = Session.object_session(self)

        session.delete(self)
        session.commit()



sqla = SQLAlchemy(model_class=Base)


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def jsonable(value):
    """Convert a (list of) SQLAlchemy instance(s) to native Python objects."""
    if isinstance(value, list):
        return [jsonable(i) for i in value]

    elif isinstance(value, Base):
        retval = dict()
        mapper = inspect(value.__class__)

        columns = [c.key for c in mapper.columns if c.key not in value._hidden_attributes]

        for column in columns:
            column_value = getattr(value, column)

            if isinstance(column_value, enum.Enum):
                column_value = column_value.value
            elif isinstance(column_value, datetime.datetime):
                column_value = column_value.isoformat()

            retval[column] = column_value

        return retval

    # FIXME: does it make sense to raise an exception or should base types
    #        (or other JSON-serializable types) just be returned as-is?
    raise Exception('value should be instance of db.Base or list!')

# Alias
as_dict = jsonable

def as_yaml(value):
    """Dump a database instance to yaml."""

    value = as_dict(value)

    # columns with json data are treated a little differnently
    try:
        json_data = json.dumps(value['json'])

    except AttributeError:
        pass

    else:
        value['json'] = json_data


    return yaml.dump(value)

# def init(ctx, URI='sqlite:////tmp/test.db', drop_all=False):
#     """Initialize the database."""
#     global engine, object_session, Session
#
#     # Make sure that the directory for the SQLite
#     # database exists (if we're using sqlite ..)
#     url = make_url(URI)
#
#     if url.host is None and url.database:
#         # Make sure we resolve a relative path
#         directory, filename = os.path.split(url.database)
#         directory = ctx.abspath(directory, 'data')
#
#         if directory:
#             os.makedirs(directory, exist_ok=True)
#
#         fullpath = os.path.join(directory, filename)
#
#         # Update the URI
#         URI = URL(
#             url.drivername,
#             username=url.username,
#             password=url.password,
#             host=url.host,
#             port=url.port,
#             database=fullpath,
#         )
#
#     url = make_url(URI)
#     log.info("Initializing the database")
#     log.debug("  driver:   {}".format(url.drivername))
#     log.debug("  host:     {}".format(url.host))
#     log.debug("  port:     {}".format(url.port))
#     log.debug("  database: {}".format(url.database))
#     log.debug("  username: {}".format(url.username))
#
#
#     engine = create_engine(URI, convert_unicode=True)
#     Session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
#     object_session = Session.object_session
#
#     Session.configure(bind=engine)
#
#     if drop_all:
#         log.warn("⚠️  Dropping existing tables! 🦖")
#         Base.metadata.drop_all(engine)
#
#     Base.metadata.create_all(bind=engine)
#     log.info("Database initialized!")

def import_data(data):
    """Load fixtures from a dictionary.

    Args:
        data (dict): data to import, indexed by classname.
    """
    log.warn("Importing data")

    # session = Session()
    session = sqla.session

    for clsname, values in data.items():
        log.debug(f"  - Processing {clsname}")
        cls = eval(clsname)

        if isinstance(cls, Table):
            for entry in values:
                try:
                    stmt = cls.insert().values(**entry)
                    session.execute(stmt)

                except Exception as e:
                    log.error('Could not add entry to database!')
                    log.error(e)
                    session.rollback()

        elif issubclass(cls, Base):
            for entry in values:
                try:
                    instance = cls(**entry)
                    session.add(instance)
                    session.commit()

                except Exception as e:
                    log.error('Could not add entry to database!')
                    log.error(e)
                    session.rollback()

        else:
            msg = f'not sure what to do with {cls}'
            # raise Exception(msg)

    session.commit()



# ------------------------------------------------------------------------------
# Import model here
# ------------------------------------------------------------------------------
from .network import *
from .security import *

