# -*- coding: utf-8 -*-
"""

"""
from datetime import date

from . import sqla


__all__ = ['Network']


# ------------------------------------------------------------------------------
# Address
# ------------------------------------------------------------------------------
class Network(sqla.Model):
    __tablename__ = 'network'

    _keys = ['name', 'json']

    id = sqla.Column(sqla.String(64), primary_key=True)
    name = sqla.Column(sqla.String(64))
    json = sqla.Column(sqla.JSON)

    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('user.id'))
    owner = sqla.relationship('User', backref='networks')

    def __repr__(self):
        """repr(x) <==> x.__repr__()"""
        name = self.name
        owner = self.owner.username
        return f"db.Network(id={self.id}, name='{name}')"