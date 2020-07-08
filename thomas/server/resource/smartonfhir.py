# -*- coding: utf-8 -*-
"""
Resources below '/<api_base>/fhir'
"""
import os
import logging

from flask import request, redirect, session, abort
from flask_restful import Resource
from flask_jwt_extended import jwt_refresh_token_required, create_access_token, create_refresh_token, get_jwt_identity
from http import HTTPStatus

import requests
from urllib.parse import urlencode
from uuid import uuid1

import fhir

from . import BaseResource, only_for, with_user
from .. import server
from .. import db
from .. import util

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api, API_BASE):

    path = os.path.join(API_BASE, module_name)
    log.info(f'Setting up "{path}" and subdirectories')

    api.add_resource(
        FHIR,
        path,
        path + '/<string:id_or_operation>',
    )



def gen_dict_with_key_value(key, value, var):
    if hasattr(var,'items'):
        for k, v in var.items():
            if (k == key) and (v == value):
                yield var
            if isinstance(v, dict):
                for result in gen_dict_with_key_value(key, value, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_with_key_value(key, value, d):
                        yield result


# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
class FHIR(Resource):
    """resource for FHIR Launch"""

    @staticmethod
    def getvalue(v):
        if isinstance(v, fhir.model.codeableconcept.CodeableConcept):
            return v.coding[0].code.toNative()

        return v.toNative()


    def __get_observations(self):
        """Return observations (key/value) for current patient."""
        iss = session['iss']
        patient = session['patient']

        url = f'{iss}/Observation?patient={patient}'
        response = requests.get(url)
        log.debug(response.json())

        codes = []
        values = []

        try:
            bundle = fhir.model.Resource.fromNative(response.json())
            log.warn(bundle)

            # codes = [e.resource.code for e in bundle.entry]
            # values = [e.resource.value for e in bundle.entry]
            # values = [e['resource']['valueCodeableConcept']['coding'][0]['code'] for e in bundle['entry']]
            # codes = [e['resource']['code']['coding'][0]['code'] for e in bundle['entry']]

            codes = [e.resource.code.coding[0].code.toNative() for e in bundle.entry]
            values = [self.getvalue(e.resource.value) for e in bundle.entry]

        except Exception as e:
            log.error('Could not retrieve data from Observation')
            log.exception(e)

        return list(zip(codes, values))

    def _launch(self):
        """SMART on FHIR Launch point!"""
        # 'iss' contains the URL to the FHIR server. 'launch' contains context
        # provided by EHR.
        log.warn('-' * 80)
        log.warn('_launch')
        log.warn('-' * 80)
        util.log_full_request(request)

        iss = request.args['iss']
        launch = request.args['launch']
        model = request.args.get('model', 'network/lungcancer')

        # Retrieve the metadata to determine the authorization endpoint
        url = f'{iss}/metadata'
        log.debug(f'Retrieving FHIR server metatadata from "{url}"')
        response = requests.get(url)
        metadata = response.json()

        value = next(gen_dict_with_key_value(
            "url",
            "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris",
            metadata
        ))

        if value is None:
            log.debug("Could not find OAuth URIs in metadata?")
            log.debug(metadata)
            abort(500)

        authorize_url = None
        extensions = value['extension']

        for e in extensions:
            if e['url'] == 'authorize':
                authorize_url = e['valueUri']
                log.debug(f"Found authorize_url: '{authorize_url}'")

            elif e['url'] == 'token':
                session['token'] = e['valueUri']

        if (authorize_url is None) or ('token' not in session):
            log.debug("Could not find OAuth URIs in metadata?")
            log.debug(extensions)
            abort(500)

        # Let the user/browser authorize with the endpoint by passing along
        # - launch, which contains context, like patientnr. and episode
        # - state, a parameter we generate ourselves to identify this specific
        #   launch
        #
        # Accessing the endpoint, triggers the server to do a GET request to
        # 'redirect_uri'. This GET sends a JWT as a query parameter.
        params = {
            'response_type': 'code',
            'redirect_uri': f'https://{request.host}/smartonfhir/_redirect',
            'launch': launch,
            'scope': 'launch',
            'state': str(uuid1()),
            'aud': iss,
        }

        # 'state' is set in a session cookie so it can be checked in
        # `_redirect()`
        session['iss'] = iss
        session['state'] = params['state']
        session['model'] = model
        log.warn(session)

        qs = urlencode(params)
        redirect_url = f'{authorize_url}?{qs}'
        log.debug(f"Redirecting to '{redirect_url}'")
        log.debug('')

        return redirect(redirect_url)

    def _redirect(self):
        """Method!"""
        log.warn('-' * 80)
        log.warn('_redirect!')
        log.warn('-' * 80)
        log.warn(session)

        if ('state' not in session) or (request.args['state'] != session['state']):
            abort(500, 'Cross site request forgery or cookies not allowed/set?')

        data = {
            'grant_type': 'authorization_code',
            'code': request.args['code'],
            'redirect_uri': f'https://{request.host}/smartonfhir/_redirect',
        }

        response = requests.post(session['token'], data)
        authorization_result = response.json()

        log.warn(authorization_result)

        session.update(authorization_result)

        params = self.__get_observations()
        qs = urlencode(params)

        redirect_url = f'https://{request.host}/app/{session["model"]}?{qs}'
        log.debug(f"Redirecting to '{redirect_url}'")
        log.debug('')

        return redirect(redirect_url)


    def get(self, id_or_operation=None):
        """FHIR EHR launch endpoint"""
        # util.log_full_request(request)

        if id_or_operation and id_or_operation.startswith('_'):
            try:
                func = getattr(self, id_or_operation)
            except Exception as e:
                log.warn("Could not find operation '{id_or_operation}'!?")
                log.warn(e)
            else:
                return func()

        return "nah .. "


