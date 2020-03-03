# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/token'
"""
import os
import logging

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, field_for
from http import HTTPStatus

import json

from thomas.core import BayesianNetwork

from .. import server
from .. import db

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    api.add_resource(
        Network,
        path,
        endpoint='network_all',
    )

    api.add_resource(
        Network,
        path + '/<int:id>',
        endpoint='network_single',
    )

    api.add_resource(
        NetworkQuery,
        path + '/<int:id>/_query',
        endpoint='network_query',
    )

# ------------------------------------------------------------------------------
# Model schema's
# ------------------------------------------------------------------------------
class NetworkSchema(ModelSchema):
    # _url = ma.URLFor('address', id='<id>')

    class Meta:
        model = db.Network

        exclude = [
            'json',
        ]


schema = NetworkSchema()

# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class Network(Resource):
    """resource for network"""

    def get(self, id=None):
        """Return a (list of) Bayesian Network(s)."""

        if id:
            return db.Network.get(id)

        result = db.Network.get()
        return schema.dump(result, many=(not id))

    def post(self, id):
        # See if the data that was sent to us checks out
        data = request.json
        bn = BayesianNetwork.from_dict(data)

        # Retrieve current entry from DB
        result = db.Network.get(id)
        result.json = bn.as_dict()
        result.save()

        return result.json


class NetworkQuery(Resource):
    """Action: perform a network query."""
    def _query(self, id, query):
        # log.info(f'query: {query}, ({type(query)})')
        result = db.Network.get(id)
        bn = BayesianNetwork.from_dict(result.json)

        probs = bn.compute_marginals(None, query)
        probabilities = {key: value.zipped() for key, value in probs.items()}


        return {
            'query': query,
            'probabilities': probabilities
        }

    def get(self, id):
        query = request.args
        return self._query(id, query)

    def post(self, id):
        query = request.json
        return self._query(id, query)


