# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/network'
"""
import os
import logging

from flask_jwt_extended import current_user as user
from flask_restful import reqparse, inputs
from flask import request, jsonify, abort
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, field_for
from http import HTTPStatus
from uuid import uuid1

import json

from thomas.core import BayesianNetwork

from . import BaseResource, only_for, with_user
from .. import server
from .. import db
from ._schema import *

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    schema_class = NetworkSchema

    api.add_resource(
        Network,
        path,
        path + '/<string:id_or_operation>',
        resource_class_kwargs={'schema_class': schema_class},
    )

# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class Network(BaseResource):
    """Resource for network"""

    @with_user
    def _create(self, data):
        """Create a new Network resource."""

        # Clients may suggest an ID for the network.
        id_ = data.get('id', str(uuid1()))
        name = data.get('name', '')

        log.info(f'Creating network {id_}')

        # Make sure this is a proper serialization.
        bn = BayesianNetwork.from_dict(data['json'])

        # Create a new entry
        network = db.Network(
            id=id_,
            name=name,
            json=bn.as_dict(),
            owner=user,
        )

        print()
        print(network)
        print()

        # session = db.Session()
        session = db.sqla.session
        session.add(network)

        try:
            session.commit()

        except Exception as e:
            session.rollback()
            return abort(409, "Could not create resource!")

        return self.schema.dump(network, many=False)

    @with_user
    def _update(self, id, data):
        """Update a Network resource."""
        log.info(f'Updating network "{id}"')
        result = db.Network.get(id)

        if result is None:
            # Cannot POST to a URL with an id if the corresponding resource
            # does not yet exist ...
            log.error(f'Network "{id}" does not exist!?')
            abort(400)

        if (user == result.owner) or user.isRoot() or user.hasRole('admin'):
            bn = BayesianNetwork.from_dict(data['json'])
            result.json = bn.as_dict()

            result.save()
            return self.schema.dump(result, many=False)

        log.info(f"403: not allowed!")
        abort(403)

    def _search(self, *args, **kwargs):
        """Overrides BaseResource._search()"""
        # util.log_full_request(request)

        parser = reqparse.RequestParser()
        parser.add_argument('_summary', type=inputs.boolean, default=True)
        args = parser.parse_args()

        if args['_summary']:
            self.schema_args['exclude'] = ['json']

        return super()._search(*args, **kwargs)

    def _query(self):
        """Action: perform a network query."""
        # log.info(f'query: {query}, ({type(query)})')
        log.info(request.json)

        id_ = request.json['id']
        query = request.json['query']

        result = db.Network.get(id_)
        bn = BayesianNetwork.from_dict(result.json)

        probs = bn.compute_marginals(None, query)
        probabilities = {key: value.zipped() for key, value in probs.items()}

        return {
            'query': query,
            'probabilities': probabilities
        }
