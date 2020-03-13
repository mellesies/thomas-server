# -*- coding: utf-8 -*-
"""

"""
from datetime import date

from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.util import classproperty


from . import Base

__all__ = ['Network']


# ------------------------------------------------------------------------------
# Address
# ------------------------------------------------------------------------------
class Network(Base):
    __tablename__ = 'network'

    _keys = ['name', 'json']

    id = Column(Integer, primary_key=True)
    abbr = Column(String(16), unique=True)
    name = Column(String(64))
    json = Column(JSON)



